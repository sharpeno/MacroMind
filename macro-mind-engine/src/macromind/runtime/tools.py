"""Allowlisted, read-only tools over verified in-memory task snapshots."""

import json
from pathlib import Path

from pydantic import Field

from macromind.runtime.models import AnalysisResult, Citation, StrictModel
from macromind.runtime.storage import inside, verify_snapshot


class Empty(StrictModel):
    pass


class ReadArgs(StrictModel):
    document_id: str
    start_line: int = Field(default=1, ge=1)
    end_line: int = Field(default=30, ge=1)


class SearchArgs(StrictModel):
    query: str = Field(min_length=1, max_length=200)
    limit: int = Field(default=8, ge=1, le=20)


DEFINITIONS = {
    "list_evidence": (Empty, "List pinned evidence documents and line counts."),
    "read_evidence": (ReadArgs, "Read up to 80 numbered lines from a pinned document."),
    "search_evidence": (SearchArgs, "Literal substring search over pinned evidence; no internet."),
    "verify_citation": (Citation, "Check exact quotation against specified evidence lines."),
    "audit_snapshot": (Empty, "Check snapshot hashes; not truth or semantic validity."),
}


def tool_schemas():
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": model.model_json_schema(),
            },
        }
        for name, (model, description) in DEFINITIONS.items()
    ]


class EvidenceTools:
    def __init__(self, task):
        self.task = Path(task)
        self.spec = verify_snapshot(self.task)
        self.documents = {
            d.id: inside(self.task, f"inputs/{d.id}.txt")
            .read_text(encoding="utf-8-sig")
            .splitlines()
            for d in self.spec.documents
        }
        self.method = inside(self.task, "inputs/method.txt").read_text(encoding="utf-8-sig")
        self.read_ids = set()

    def lines(self, document_id, start, end):
        if document_id not in self.documents:
            raise ValueError("Unknown document ID")
        lines = self.documents[document_id]
        if not 1 <= start <= end <= len(lines) or end - start >= 80:
            raise ValueError("Invalid line range (maximum 80 lines)")
        return lines[start - 1 : end]

    def verify(self, citation):
        lines = self.lines(citation.document_id, citation.start_line, citation.end_line)
        if citation.quote not in "\n".join(lines):
            raise ValueError("Quote not found in cited lines")
        return {"valid": True, "scope": "verbatim_match_only", **citation.model_dump()}

    def call(self, name, arguments):
        if name not in DEFINITIONS:
            raise ValueError("Unknown tool; only read-only evidence tools are available")
        args = DEFINITIONS[name][0].model_validate(arguments)
        if name == "list_evidence":
            return {
                "documents": [
                    {
                        "id": d.id,
                        "published_at": str(d.published_at),
                        "sha256": d.sha256,
                        "lines": len(self.documents[d.id]),
                    }
                    for d in self.spec.documents
                ]
            }
        if name == "audit_snapshot":
            verify_snapshot(self.task)
            return {
                "integrity": "PASS",
                "semantic_acceptance": False,
                "dataset_version": self.spec.dataset_version,
                "method_version": self.spec.method_version,
            }
        if name == "verify_citation":
            return self.verify(args)
        if name == "read_evidence":
            lines = self.lines(args.document_id, args.start_line, args.end_line)
            text = "\n".join(lines)
            if len(text) > 16000:
                raise ValueError("Requested content too large; select fewer lines")
            self.read_ids.add(args.document_id)
            return {
                "document_id": args.document_id,
                "untrusted_source_material": True,
                "lines": [{"line": i, "text": s} for i, s in enumerate(lines, args.start_line)],
            }
        hits = []
        for doc_id, lines in self.documents.items():
            for number, line in enumerate(lines, 1):
                if args.query.casefold() in line.casefold():
                    hits.append({"document_id": doc_id, "line": number, "text": line[:1000]})
                    self.read_ids.add(doc_id)
                    if len(hits) == args.limit:
                        return {"hits": hits, "limit_reached": True}
        return {"hits": hits, "limit_reached": False}

    def validate_result(self, content):
        result = AnalysisResult.model_validate(json.loads(content))
        if not self.read_ids:
            raise ValueError("Model must read or search evidence before completing")
        for claim in result.claims:
            for citation in claim.citations:
                if citation.document_id not in self.read_ids:
                    raise ValueError("Citation references evidence not retrieved by this attempt")
                self.verify(citation)
        verify_snapshot(self.task)
        return result
