# Project-DJ-Engine Docs

This repository contains the hand-written Sphinx sources, generated API
artifacts, and external-harness metadata used to keep the PDJE documentation in
sync with the cloned wrapper and core repositories.

## Docs Harness

Use `docs-harness` to inspect the recorded documentation baseline and the source
diff that still needs to be reflected into `srcs/*.rst`.

```bash
uv run docs-harness record-source-heads
uv run docs-harness status --json
uv run docs-harness diff-context --json
uv run docs-harness show-diff --repo core --name-only
uv run docs-harness stamp-baseline
```

`record-source-heads` snapshots the current `PDJE` wrapper/core branch and commit
hashes into a tracked file. This matters because the `PDJE*` clone directories
are intentionally ignored by this repository.

`stamp-baseline` advances the recorded source baseline only after documentation
updates have been reviewed and validated.

The canonical generation reference for the hand-written docs lives in
`docs_harness/SRCS_DOC_GENERATION_SPEC.md`. `Editor_Format` also has a dedicated
asset snapshot under `docs_harness/important_assets/editor_format/`.
