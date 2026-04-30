# `srcs` Documentation Generation Specification

This document defines the canonical shape of the hand-written documentation
under `srcs/*.rst`. It is written for external coding harnesses that need to
regenerate or update the current documentation while preserving the existing
information architecture and source-backed claims.

## Purpose

- Reconstruct the current `srcs` guide set without inventing a new structure.
- Preserve page roles, section order, cross-links, and the current split
  between hand-written guidance and generated API lookup.
- Explain which pages are hybrid manual/API pages, which are policy pages, and
  which are catalog pages.
- Define the special asset-backed preservation rules for `Editor_Format.rst`.

## Non-Goals

- Regenerating `srcs/api/**`, `srcs/xml/**`, or `docs/**`.
- Defining model prompts or an agent runtime.
- Replacing code-backed verification against the current source tree.

## Canonical Document Set

The hand-written guide set consists of these 12 files:

- `srcs/index.rst`
- `srcs/Getting Started.rst`
- `srcs/Developer_Onboarding.rst`
- `srcs/Core_Engine.rst`
- `srcs/Editor_Workflows.rst`
- `srcs/Input_Engine.rst`
- `srcs/Judge_Engine.rst`
- `srcs/Util_Engine.rst`
- `srcs/Data_Lines.rst`
- `srcs/Editor_Format.rst`
- `srcs/FX_ARGS.rst`
- `srcs/PDJE_For_AI_Agents.rst`

Generated API output under `srcs/api/api_root.rst` is reference-only. It is not
part of this generation spec.

## Global Information Architecture

The current guide hierarchy is fixed:

1. `index.rst`
   landing page, quick start, architecture framing, milestone graph, resource
   links, top-level toctree.
2. `Getting Started.rst`
   guide hub, documentation map, reading order, binding notes, guide toctree.
3. The remaining pages
   topic guides grouped by workflow, module, data model, or policy.

When regenerating pages:

- Keep the current page titles exactly.
- Keep the current second-level section order exactly.
- Preserve `:doc:` cross-links when they represent reading flow.
- Treat `index.rst` as structure-frozen. Do not add, remove, reorder, rename,
  or repurpose its major sections or its current final toctree unless the user
  explicitly requests an index-structure change.
- Use the generated API only for symbol anchors or exact member lookup, not as
  the sole proof of recommended workflows.
- Prefer wording grounded in “the current source tree” or “the hand-written
  docs currently describe”.
- Do not collapse wrapper naming into native C++ naming.
- Do not claim unverified release, packaging, performance, or platform status.

## Page Type Rules

### Landing Page

`index.rst` is a landing page, not a deep API page.

- It must contain project framing before any deep guide links.
- It must keep quick-start build instructions and the architecture overview.
- It may contain project-level diagrams such as Mermaid graphs.
- It must end with a short toctree rather than embedding all guide detail.

### Hub Page

`Getting Started.rst` is the guide hub.

- It must summarize what each guide is for.
- It must include a recommended reading order.
- It must explain where wrapper-related notes live.
- It must own the guide toctree for the topic pages.

### Hybrid Workflow Pages

These pages mix manual guidance, selected Doxygen anchors, and short example
snippets:

- `Core_Engine.rst`
- `Editor_Workflows.rst`
- `Input_Engine.rst`
- `Judge_Engine.rst`
- `Util_Engine.rst`
- `Data_Lines.rst`

Rules for hybrid pages:

- Start with prose that explains how the subsystem is meant to be used.
- Introduce Doxygen directives only after the workflow framing is clear.
- Use selected directives, not exhaustive symbol dumps.
- Keep at least one source-backed example when the page currently uses one.
- Separate native and wrapper guidance explicitly when both exist.

### Data Catalog Pages

These pages are structured inventories of keys, fields, or accepted values:

- `Editor_Format.rst`
- `FX_ARGS.rst`

Rules for data catalog pages:

- Keep exact field/key/value spellings when the source is case-sensitive.
- Preserve author-facing tables or lists that explain field meanings.
- Link back to workflow pages when operational behavior lives elsewhere.

### Policy and Safety Pages

These pages are guidance and safety rails rather than direct subsystem usage
manuals:

- `Developer_Onboarding.rst`
- `PDJE_For_AI_Agents.rst`

Rules for policy pages:

- Preserve route-setting guidance, terminology, and common-mistake sections.
- Preserve explicit “safe to state” versus “must verify” distinctions.
- Preserve anti-hallucination rules and wrapper/native naming boundaries.

## Page Contracts

### `index.rst`

- Role: landing page for project overview and build entrypoint.
- Required sections in order:
  `Quick Start`, `System Architecture`, `MileStones`, `Use Cases`,
  `Additional Resources`, `CI/CD Call Graph`, final toctree.
- Freeze rule:
  without an explicit user request, preserve the current composition of
  `index.rst`, including its section set, section order, project-overview
  opening, and current final toctree entries.
- Required links:
  `:doc:\`Getting Started\``, `:doc:\`Util_Engine\``.
- Required toctree entries:
  `Getting Started`, `api/api_root`, `Util_Engine`, `Editor_Format`.
- Sources:
  top-level build flow, module overview, repository automation context.
- Doxygen directives: none required.
- Examples: build snippets for Linux/macOS and Windows are required.

### `Getting Started.rst`

- Role: guide map and reading order.
- Required sections in order:
  `Documentation Map`, `Recommended Reading Order`, `Binding Notes`, final
  toctree.
- Required links:
  every topic guide page, plus `/api/api_root`.
- Doxygen directives: none.
- Examples: not required.

### `Developer_Onboarding.rst`

- Role: shortest path to a correct mental model for contributors and integrators.
- Required sections in order:
  `What PDJE Is`, `Choose Your Starting Path`, `How To Read This Project`,
  `Build And Configuration Reality`, `Project Mental Model`,
  `Useful Domain Knowledge`, `First Real Workflows`,
  `Contributor Orientation`, `Common Mistakes`, `Where To Go Next`.
- Required links:
  `index`, `Core_Engine`, `Editor_Workflows`, `Input_Engine`, `Judge_Engine`,
  `Data_Lines`, `Editor_Format`, `/api/api_root`.
- Doxygen directives: none.

### `Core_Engine.rst`

- Role: public `PDJE` facade and playback control guide.
- Required sections in order:
  `Public Entry Points`, `Typical Playback Flow`, `Wrapper Bindings`,
  `Player Control`, `FX Control`, `Music Control`, `Editor Entry Points`.
- Required links:
  `Editor_Workflows`, `/api/classeditorObject`.
- Sources:
  `include/core/interface/PDJE_interface.hpp`, player-facing headers, wrapper
  entrypoints.
- Doxygen directives:
  `PLAY_MODE`, `PDJE`, selected facade methods, selected `audioPlayer` methods.
- Examples:
  native C++ plus current wrapper-language snippets.
- Wrapper rule:
  keep `Panel` vs `Pannel` distinction explicit.

### `Editor_Workflows.rst`

- Role: editor lifecycle, mutation, history, persistence, preview.
- Required sections in order:
  `What The Editor Owns`, `How The Editor Is Reached`, `Project Setup`,
  `Mutation Workflow`, `History And Time Travel`, `Persistence Workflow`,
  `Preview And Validation`, `Wrapper Notes`, `How This Relates To The Older Manual`,
  `Common Mistakes`, `Where To Go Next`.
- Required links:
  `Core_Engine`, `Editor_Format`, `/api/classeditorObject`.
- Sources:
  `include/core/MainObjects/editorObject/`, `include/core/editor/`.
- Doxygen directives:
  `PDJE::InitEditor`, `PDJE::GetEditorObject`, `PDJE::CloseEditor`, selected
  `editorObject` methods.

### `Input_Engine.rst`

- Role: low-latency input runtime guide.
- Required sections in order:
  `Public Types`, `Platform Behavior`, `Transport Notes`, `Binding Status`,
  `Initialization Signature`, `Current Lifecycle`, `Data Line Semantics`,
  `Example`, `Notes`, `Godot Wrapper Example`.
- Required links:
  `Data_Lines`, `Judge_Engine`.
- Sources:
  `include/input/`.
- Doxygen directives:
  `PDJE_Input`, `DeviceData`, enums, selected lifecycle methods,
  `PDJE_INPUT_DATA_LINE`.
- Wrapper rule:
  SWIG does not expose this module as first-class bindings; Godot wrapper flow
  remains separate.

### `Judge_Engine.rst`

- Role: judge wiring and timing model guide.
- Required sections in order:
  `Judge Engine Architecture`, `Runtime Types`, `Startup Contract`,
  `Initialization API`, `Timing Model`, `Binding Status`,
  `Reference Integration Order`, `Callbacks`, `Godot Wrapper Flow`.
- Required links:
  `Input_Engine`, `Data_Lines`.
- Sources:
  `include/judge/`, judge tests.
- Doxygen directives:
  `PDJE_JUDGE::JUDGE`, `Judge_Init`, `EVENT_RULE`, selected setup methods.
- Wrapper rule:
  do not claim SWIG coverage for judge without source-backed proof.

### `Util_Engine.rst`

- Role: maintained utility surface and consumption boundaries.
- Required sections in order:
  `Public Consumption Units`, `Header Boundaries`,
  `Common Status And Result Types`, `Database Wrappers`,
  `Function Helpers`, `Scalar And Text`, `Image Helpers`,
  `Signal / STFT Helpers`, `AI Namespace`.
- Required links:
  `/api/api_root`.
- Sources:
  `include/util/`, `include/util/ai/**`, `tests/unit/util/`,
  `tests/unit/util/ai_beat_this.test.cpp`,
  `tests/unit/onnxruntime/onnxruntime_smoke.cpp`, util cmake files, and wrapper
  util files under `PDJE-Godot-Plugin/Wrapper_Includes/util/db/**`,
  `PDJE-Godot-Plugin/Wrapper_Includes/util/MIR/**`, and
  `PDJE-Godot-Plugin/Wrapper_Includes/util/AI/**`.
- Doxygen directives:
  current shared status/result file anchors plus selected file anchors where
  already present.
- Required claim:
  the utility layer is active code, not roadmap-only.
- Example rule:
  each major util family documented on this page must keep at least one
  source-backed short example. Native C++ examples must show the relevant
  `Result<T>`, `Result<void>`, or direct-return status boundary when one exists.
  Godot wrapper examples must use the wrapper class and method names from the
  binding source and remain separate from native C++ examples.
- AI rule:
  `AI Namespace` must describe the current `PDJE_UTIL::ai` ONNX Runtime facade,
  Beat This native detector, and Godot Beat This wrapper surface. Do not leave
  this section as a placeholder, and do not claim generic ONNX sessions/tensors
  are directly exposed to Godot unless the wrapper source proves it.

### `Data_Lines.rst`

- Role: shared live-state bridge and ABI/lifetime warning page.
- Required sections in order:
  `Why Data Lines Exist`, `Typical Use Cases`, `General Rules`,
  `Lifetime, Threading, And ABI Notes`, `Core Data Line`, `Input Data Line`,
  `Binding Notes`, `Threading Notes`.
- Required links:
  `Input_Engine`, `Judge_Engine`.
- Sources:
  core/input data line structs and related sync structs.
- Doxygen directives:
  `PDJE::PullOutDataLine`, `PDJE_CORE_DATA_LINE`, `audioSyncData`,
  `PDJE_Input::PullOutDataLine`, `PDJE_INPUT_DATA_LINE`, `PDJE_Input_Log`.

### `Editor_Format.rst`

- Role: editor on-disk and translation-layer data structures.
- Required sections in order:
  `Semantic Model`, `Root Database Payloads`, `Editor Argument Shapes`,
  `Time And Position Model`, `Interpolation And \`EightPointValues\``,
  `JSON Working Sets`, `Mix JSON Keys`, `Note JSON Keys`, `Music JSON Keys`,
  `Example JSON Fragments`, `Translation Layer`.
- Required links:
  `Editor_Workflows`.
- Sources:
  `include/core/editor/TimeLine/JSONWrap/jsonWrapper.hpp`, relevant editor
  translators, runtime parser references.
- Doxygen directives:
  `trackdata`, `musdata`, `MixArgs`, `NoteArgs`, `MusicArgs`.
- Asset-backed rule:
  this page must restore the `important_assets/editor_format/` tables and image
  and must preserve their explanatory prose. See the dedicated section below.

### `FX_ARGS.rst`

- Role: exact case-sensitive FX argument key catalog.
- Required sections in order:
  one section per FX enum in the current page order, then `Usage Example`.
- Sources:
  `include/core/audioRender/ManualMix/ManualFausts/*.hpp`.
- Doxygen directives: none required.
- Required claim:
  keys are exact and case-sensitive.

### `PDJE_For_AI_Agents.rst`

- Role: safe-answering guide for AI systems.
- Required sections in order:
  `Purpose`, `Project Facts Safe To State`,
  `Claims That Must Be Qualified Or Verified`,
  `Canonical Terminology`, `Architecture Cheat Sheet`,
  `How To Answer Common User Questions`, `Anti-Hallucination Rules`,
  `Known Confusion Traps`, `Answer Skeletons`,
  `When The Agent Should Be Cautious`.
- Required links:
  all relevant topic pages the cheat sheet routes to.
- Required rule:
  preserve the distinction between safe current-tree claims and externally
  unstable claims.

## `Editor_Format` Important Assets

`Editor_Format.rst` is the only page that currently carries source-like tables
and a diagram image that must survive regeneration as separate assets.

Canonical asset store:

- `docs_harness/important_assets/editor_format/assets_manifest.json`
- `docs_harness/important_assets/editor_format/tables.json`
- `docs_harness/important_assets/editor_format/eightPoint_example.png`

### Asset Inventory

The following assets are mandatory:

- `track_data_format`
- `music_metadata_format`
- `mix_data_format`
- `mix_data_table`
- `note_data_format`
- `interpolation_keywords`
- `mix_json_keys`
- `eight_point_example`

### Asset Preservation Rules

- The page must restore these tables or image in the sections listed by the
  manifest.
- The surrounding prose must explain what each asset means; assets are not
  decorative.
- Missing prose counts as a generation failure even if the raw table or image
  is present.
- The `Mix JSON Keys` table is mandatory even though its original directive is
  unlabeled.

### Required Section-Level Mentions

The following explanations are mandatory:

- `Root Database Payloads`
  must explain the `trackdata` and `musdata` column layouts and state that the
  binary fields are not intended to be edited by hand.
- `Root Database Payloads`
  must explain that `firstBeat` is used as the PCM-frame offset where the first
  musical beat begins for that asset.
- `Editor Argument Shapes`
  must explain that `Mix Data Table` preserves the older author-facing labels
  and captures how `first`, `second`, and `third` are interpreted for each mix
  type.
- `Editor Argument Shapes`
  must mention that current names such as `BPM_CONTROL` and `OSC_FILTER` map to
  older spellings shown in the table.
- `Interpolation And EightPointValues`
  must explain that `MixArgs.first` carries interpolation selection and
  `MixArgs.second` carries comma-separated control values in the current mental
  model.
- `Interpolation And EightPointValues`
  must explain that the `eightPoint_example` image represents eight control points
  stretched across the event span from the start beat tuple to the end beat
  tuple.
- `Interpolation And EightPointValues`
  must keep the flat-interpolator note that older single-value examples still
  match the flat concept in the current tree.
- `Mix JSON Keys`
  must explain each JSON key’s meaning, not just reproduce the raw key names.

### Reconstruction Order for `Editor_Format`

When regenerating `Editor_Format.rst`:

1. Rebuild the prose skeleton in the canonical section order.
2. Reinsert the asset-backed tables and image from `important_assets/editor_format/`.
3. Reinsert or rewrite the surrounding prose so the required mentions and
   claims from the asset manifest remain present in the correct section.
4. Verify that each asset listed in the manifest appears in its mapped section.

## Validation Checklist

Before accepting a regenerated page set:

- Every page title and second-level section order matches this spec.
- Cross-links still route from hub pages to topic pages and from workflow pages
  to data-format or API lookup pages.
- Hybrid pages still combine prose, selected Doxygen directives, and examples.
- `Editor_Format` still includes all asset-backed tables and the eight-point
  image, and the associated explanatory prose is still present.
- No page claims wrapper coverage, platform support, or release status that is
  not backed by the current local source tree.
