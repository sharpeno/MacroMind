# Validator rules

The machine catalog is `phase1/validator_rule_catalog.json`.
Every rule executes or records NOT_APPLICABLE. PASS means only its structural
check passed. Known errors are never waived by review workflow.

| ID | Name | Boundaries / principles | Debts | Limitation |
|---|---|---|---|---|
| V-SCH001 | Canonical versions | Canonical runtime contract | — | Structural check only; no inference, repair, or reality verdict. |
| V-SCH002 | Registered Pydantic shape | B08 | — | Structural check only; no inference, repair, or reality verdict. |
| V-REF001 | Unique object identity | Canonical runtime contract | — | Structural check only; no inference, repair, or reality verdict. |
| V-REF002 | Registered object discriminator | Canonical runtime contract | — | Structural check only; no inference, repair, or reality verdict. |
| V-REF003 | Allowed reference target type | B01, B06, B14 | — | Structural check only; no inference, repair, or reality verdict. |
| V-REF004 | Complete bundle resolution | Canonical runtime contract | — | Structural check only; no inference, repair, or reality verdict. |
| V-REF005 | Partial bundle resolution | Canonical runtime contract | — | Structural check only; no inference, repair, or reality verdict. |
| V-REF006 | Explicitly forbidden prior self reference | Canonical runtime contract | D04 | Structural check only; no inference, repair, or reality verdict. |
| V-PROV001 | Claim source provenance | B01, P01 | — | Structural check only; no inference, repair, or reality verdict. |
| V-PROV002 | Occurrence provenance consistency | B01, P01 | — | Structural check only; no inference, repair, or reality verdict. |
| V-PROV003 | Origin family independence boundary | B01, P01 | — | Independence scoring is intentionally not implemented. |
| V-TEMP001 | Structured temporal intervals | P13 | D04 | Structural check only; no inference, repair, or reality verdict. |
| V-TEMP002 | Forecast cutoff versus window | B09, P13 | D03 | Structural check only; no inference, repair, or reality verdict. |
| V-TEMP003 | Future prior leakage | P13 | D04 | Unknown/overlapping content time is indeterminate; no sample-label ordering or date text parsing. |
| V-TEMP004 | Independent source time axes | P13 | D04 | Structural check only; no inference, repair, or reality verdict. |
| V-BND001 | Scenario stays Scenario | B09 | D03 | Structural check only; no inference, repair, or reality verdict. |
| V-BND002 | Structural process evidence | B03 | — | Structural check only; no inference, repair, or reality verdict. |
| V-BND003 | Assessment truth non-propagation | B10, B11 | D20 | Structural check only; no inference, repair, or reality verdict. |
| V-BND004 | Usage authorship non-propagation | B14, P15 | D20 | Structural check only; no inference, repair, or reality verdict. |
| V-BND005 | Actor attribute identity boundary | B04 | D20 | Structural check only; no inference, repair, or reality verdict. |
| V-BND006 | Comparison preservation | B05 | D16 | Units are free text; no controlled conversion/denominator or stage-transition contract exists. |
| V-FC001 | Conservative structural admission | B08, B09, P13 | D03 | Structural check only; no inference, repair, or reality verdict. |
| V-FC002 | Conditional endorsement gap | B09 | D03 | Conditional endorsement cannot be proved from free text conditions/branch selection. |
| V-FC003 | Resolution timing consistency | B09, P13 | D03 | Structural check only; no inference, repair, or reality verdict. |
| V-ARG001 | Unique local step identities | B07, P08 | D11 | Structural check only; no inference, repair, or reality verdict. |
| V-ARG002 | Fragile step resolution | B07, P08 | D11 | Structural check only; no inference, repair, or reality verdict. |
| V-ARG003 | Directed argument cycles | B07, P08 | D11 | Structural check only; no inference, repair, or reality verdict. |
| V-ARG004 | Orphan inference steps | B07, P08 | D11 | Structural check only; no inference, repair, or reality verdict. |
| V-ARG005 | Per-edge attribution | B07, P15, P16 | D11, D20 | Structural check only; no inference, repair, or reality verdict. |
| V-ARG006 | Argument semantic transition gap | B07, P08 | D11, D16 | No typed denominator/unit/role transition evidence on inference edges. |
| V-AN001 | Recurrence match consistency | B12 | D04 | Structural check only; no inference, repair, or reality verdict. |
| V-AN002 | Eligible historical recurrence | B12, P13 | D04 | Structural check only; no inference, repair, or reality verdict. |
| V-AN003 | Model reconstruction evidence guard | B12, B13, P15, P16 | D20 | Mixed Argument citations lack selected-edge evidence scope; flagged for review. |
| V-AN004 | Observed reasoner and observer attribution | B12, P15 | D20 | Structural check only; no inference, repair, or reality verdict. |
| V-GOV001 | Review never waives validation | Canonical runtime contract | — | Structural check only; no inference, repair, or reality verdict. |
| V-GOV002 | Input immutability | Canonical runtime contract | — | Structural check only; no inference, repair, or reality verdict. |
| V-GOV003 | No Skill promotion | B12, B13 | — | Schema only admits candidate/unknown Heuristic; Skill promotion/evidence is not implemented. |

Reference resolution is centralized in reference_contracts.py. Schema errors
preserve Pydantic error type and JSON field path. Unknown values are legal;
unknown semantic evidence is indeterminate, not automatically ERROR.

V-FC001 distinguishes ADMISSION_STRUCTURALLY_SUPPORTED, ADMISSION_INDETERMINATE
and ADMISSION_INVALID without retyping objects. V-AN003 reports ERROR plus
review for explicit diagnostic evidence and WARNING for mixed unscoped evidence.
V-PROV003/V-ARG006/V-GOV003 intentionally expose evidence/scope limitations.
V-BND006 never computes a baseline/delta and cannot certify unit conversions.
See PHASE1_3_VALIDATOR_ARCHITECTURE.md for time precision, modes and hash rules.
