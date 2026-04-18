# Docs Harness Contract

This repository is designed to be observed by an external agentic coding
harness such as Codex or Claude Code. The external harness owns planning,
reasoning, and editing. This repository exposes only the machine-readable
baseline and scope data needed to update the hand-written documentation safely.

## Canonical Targets

- Canonical editable documents live under `srcs/*.rst`.
- Generated API material under `srcs/api/`, `srcs/xml/`, and `docs/` is
  read-only.
- `PDJE-Godot-Plugin/Project-DJ-Engine/document_sources/` is reference-only.
  It may help a harness cross-check wording, but it is not the canonical edit
  target in this repository.

## Baseline Model

- `docs_harness/source_baseline.lock.json` stores the last wrapper and core
  revisions that have already been reflected into the hand-written docs.
- `docs_harness/source_heads.lock.json` stores the currently observed wrapper
  and core branch/commit hashes, even though the `PDJE*` clone directories
  themselves are gitignored by this repository.
- The recorded branch is part of the contract. If the current clone branch does
  not match the recorded branch, treat the diff context as invalid and stop.
- Advancing the baseline is a deliberate action performed only after the
  relevant `srcs/*.rst` updates have been reviewed and validated.

## Scope Model

- `docs_harness/doc_scope.yaml` maps changed wrapper/core file paths to the
  `srcs/*.rst` pages that may need updates.
- The file is JSON-formatted so it stays readable without introducing a YAML
  parser dependency, while remaining valid YAML 1.2.

## Official CLI

Use the `docs-harness` CLI from the repository root.

```bash
uv run docs-harness record-source-heads
uv run docs-harness status --json
uv run docs-harness diff-context --json
uv run docs-harness show-diff --repo core --patch
uv run docs-harness stamp-baseline
```

### `record-source-heads`

Records the current wrapper/core branch and HEAD commit into
`source_heads.lock.json`. Use this after clone/pull so the repository contains a
tracked record of which ignored wrapper/core revisions are present locally.

### `status --json`

Returns the recorded branch/commit, current branch/commit, and dirty-tree state
for the wrapper and core clones. Exit non-zero if any branch differs from the
recorded branch. The wrapper dirty-state ignores the nested core checkout,
because the core diff is tracked separately through its own baseline.

### `diff-context --json`

Returns the changed files between `documented_commit..HEAD`, a short diffstat,
and the impacted `srcs/*.rst` pages according to `doc_scope.yaml`. Exit
non-zero if any branch differs from the recorded branch.

### `show-diff --repo wrapper|core`

Streams the raw `git diff` against the recorded baseline for the selected repo.
Use `--patch` for the full patch or `--name-only` for a path list.

### `stamp-baseline`

Records the current wrapper/core branch and HEAD commit into
`source_baseline.lock.json`. Run this only after the documentation is updated
and the build passes.

## Expected External-Harness Flow

1. Pull or otherwise update the nested clones.
2. Run `uv run docs-harness record-source-heads`.
3. Run `uv run docs-harness status --json`.
4. Run `uv run docs-harness diff-context --json`.
5. Update only the impacted `srcs/*.rst` pages.
6. Validate with `./DOCUMENT_GENERATOR.sh` or
   `uv run sphinx-build -b html ./srcs docs`.
7. Advance the baseline with `uv run docs-harness stamp-baseline`.
