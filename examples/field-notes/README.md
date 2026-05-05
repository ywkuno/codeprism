# Field Notes

This directory lists public repositories used for local CodePrism comparison field notes.

Field notes are not release benchmark fixtures. They are maintainer-run measurements on public repo checkouts, useful for product direction and public positioning caveats. Keep them dated, reproducible, and clearly separate from the checked-in benchmark fixture suite.

The runner never clones repositories and never calls the network. Clone public targets yourself, then point the runner at those local checkouts:

```bash
git clone https://github.com/oraios/serena external/serena
python scripts/run_field_notes.py --target serena --repos-root external
```

To run every configured target that exists locally:

```bash
python scripts/run_field_notes.py --config examples/field-notes/public-repos.json --repos-root external
```

Artifacts are written under `.codeprism/field-notes/` by default. Each target gets its own `context.db`, slice files, `prime.log`, and `result.json`; the run also writes `summary.json` and `summary.md`.

Use `--fail-on-missing` only when CI or a release review has already prepared every checkout. By default, missing targets are reported with clone hints instead of failing the run.
