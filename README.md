# Project-DJ-Engine Docs

This repository contains the hand-written Sphinx sources, generated API
artifacts, and external-harness metadata used to keep the PDJE documentation in
sync with the cloned wrapper and core repositories.

## Project Overview

**Project-DJ-Engine (PDJE)** is a soft real-time C++ engine that combines
rhythm game logic, DJ performance workflows, and DAW-style editing APIs. The
documentation in this repository covers all four major integration surfaces:

- **Core Engine (`PDJE`)** — playback control, editor access, and the core data line
- **Input Engine (`PDJE_Input`)** — low-latency keyboard, mouse, and MIDI
  ingestion
- **Judge Engine (`PDJE_JUDGE::JUDGE`)** — microsecond-precision note matching
- **Utility Engine (`PDJE_UTIL`)** — status/result types, DB wrappers, image
  helpers, and STFT utilities

## Documentation Structure

```
.
├── srcs/                        # Hand-written RST sources (canonical edit targets)
│   ├── index.rst                # Landing page, quick start, architecture
│   ├── Getting Started.rst      # Guide hub, reading order, binding notes
│   ├── Developer_Onboarding.rst # Integration-first mental model
│   ├── Core_Engine.rst          # Playback facade and player control
│   ├── Editor_Workflows.rst     # Authoring, mutation, history, persistence
│   ├── Input_Engine.rst         # Low-latency input runtime
│   ├── Judge_Engine.rst         # Timing and judgment pipeline
│   ├── Util_Engine.rst          # Utility surface and consumption boundaries
│   ├── Data_Lines.rst           # Zero-copy live-state bridge structs
│   ├── Editor_Format.rst        # Editor data shapes and JSON keys
│   ├── FX_ARGS.rst              # Case-sensitive FX argument key catalog
│   ├── PDJE_For_AI_Agents.rst   # Anti-hallucination guide for AI systems
│   ├── api/                     # Generated API reference (read-only)
│   ├── xml/                     # Doxygen XML output (read-only)
│   └── conf.py                  # Sphinx configuration
├── docs/                        # Built HTML output (read-only)
├── docs_harness/                # Documentation harness metadata
│   ├── SRCS_DOC_GENERATION_SPEC.md  # Canonical generation specification
│   ├── HARNESS.md                   # Harness contract and CLI reference
│   ├── doc_scope.yaml               # File-to-page mapping rules
│   ├── source_baseline.lock.json     # Last documented commit hashes
│   ├── source_heads.lock.json        # Current observed commit hashes
│   └── important_assets/            # Asset-backed tables and images
├── tools/                       # Python CLI implementation
├── tests/                       # Harness and asset tests
├── PDJE-Godot-Plugin/          # Cloned wrapper repo (gitignored)
│   └── Project-DJ-Engine/      # Cloned core repo (submodule)
├── Doxyfile                     # Doxygen configuration
├── DOCUMENT_GENERATOR.sh        # One-command build script
└── README.md                    # This file
```

## Building the Documentation

Prerequisites:

- Python 3.12+ with `uv`
- Doxygen
- Graphviz

Build the full documentation set:

```bash
./DOCUMENT_GENERATOR.sh
```

Or build manually:

```bash
doxygen ./Doxyfile
uv run sphinx-build -b html ./srcs docs
```

The output lands in `docs/`. Open `docs/index.html` to browse.

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

## Reading Order

For new developers or integrators:

1. Start with the [landing page](srcs/index.rst) for the project overview
2. Read [Getting Started](srcs/Getting%20Started.rst) for the guide map
3. Read [Developer_Onboarding](srcs/Developer_Onboarding.rst) for the mental model
4. Then follow the topic guides relevant to your use case

## Related Repositories

- **Core Engine**: https://github.com/Rliop913/Project-DJ-Engine
- **Godot Plugin**: https://github.com/Rliop913/PDJE-Godot-Plugin
- **Plugin Prebuilt**: https://github.com/Rliop913/Project_DJ_Godot

## Changelog

### 2026-04-19 — Documentation update

- **README.md**: 프로젝트 개요, 문서 구조 맵, 빌드 방법, 독서 순서, 관련 저장소 링크 대폭 추가
- **srcs/index.rst**: `Util_Engine`을 toctree에 추가 (SRCS_DOC_GENERATION_SPEC 필수 링크에 명시되어 있었으나 누락), CI/CD Call Graph의 주석 처리된 mermaid 설정 라인 제거
- **srcs/conf.py**: 저작권 연도 `2025` → `2025-2026` 업데이트
- **docs_harness/SRCS_DOC_GENERATION_SPEC.md**: `index.rst` 계약에 Required toctree entries 필드 추가, `Util_Engine.rst` 계약에 Required links 필드 추가
- **docs_harness/HARNESS.md**: Documentation Map 섹션 추가 (12개 가이드 페이지 역할 요약)

## License

LGPL v2.1
