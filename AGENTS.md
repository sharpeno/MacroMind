# Operational Directives: Bias to Implementation

## 1. Minimal Documentation & Zero Slop
- Strictly DO NOT generate markdown summaries, explanatory essays, design documents, or status logs unless explicitly requested by the user.
- Do not create or update scratchpads, `NOTES.md`, or architecture walkthroughs.
- Avoid conversational filler, apologies, and transition boilerplate. Output code changes, minimal command output, and concise results directly.

## 2. Pragmatic Verification (No Paranoid Hash/Integrity Loops)
- Never perform multi-step hash checks (MD5/SHA256), redundant file signature verifications, or recursive diff comparisons unless verifying remote cryptographic downloads.
- Trust the local filesystem and harness state directly. Inspect files via standard targeted edits (AST/diff), not full-file recalculations.
- Test proportionate to the scope: run only the relevant unit/smoke tests directly touching the changed code. Do not rerun full regression test suites or excessive verification harnesses for local, reversible changes.

## 3. Bias for Action
- Implement directly. Resolve routine, reversible coding decisions autonomously without stopping to ask permission or proposing multi-phase plans.
- Finish the task with a clean patch and brief one-sentence verification proof.
## 4. Title-Derived Time
- When a date/time is derived from a programme or video title and no verified publication time is available, use 23:59 on that date in Asia/Shanghai (UTC+08:00), serialized as `YYYY-MM-DDT23:59:00+08:00`. Do not default to 00:00.
- Apply this rule to title-derived timestamps and replay cutoffs. Record that the time is inferred from the title, not a verified publication time. Prefer a verified publication timestamp when available.
