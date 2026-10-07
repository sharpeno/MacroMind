# Canonical reference only

The authoritative contract is `../../../golden_sample_test/core_ontology/v0.3/`.
Pass its resolved path as `--contract-root`. This directory holds no second contract.
The loader reads every artifact and verifies the nine output hashes and canonical
semantic projection. The manifest does not hash itself; its external freeze commit
log is a provenance anchor, not an external signature. Phase 1 records before/after
hashes independently and never writes any frozen file.

