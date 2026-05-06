# CodePrism vX.Y.Z

## What Changed

-

## Token-Saving Workflow Impact

- Mapper/context export:
- Slice/query/read workflow:
- Benchmark or audit tooling:
- Visual/replay layer:

## Verification

- [ ] `python scripts/pre_release_proof.py --baseline-suite <previous-suite.json>`
- [ ] `pytest`
- [ ] `ruff check .`
- [ ] `codeprism benchmark-suite examples/benchmarks --out .codeprism/benchmarks/suite.json`
- [ ] `codeprism benchmark-compare <previous-suite.json> .codeprism/benchmarks/suite.json --out .codeprism/benchmarks/comparison.md`
- [ ] Public hygiene scan passed

## Benchmark Notes

Token counts are local estimates for comparison, not billing-grade measurements.

- Fixture count:
- Average source-to-slice saving:
- Notable improvements:
- Notable regressions:
- External field-note run (optional): `2026-05-06` executed 7 public repos via `scripts/run_field_notes.py --config examples/field-notes/public-repos.json --repos-root external`; all 7 passed.

## Upgrade Notes

-

## Known Limitations

-
