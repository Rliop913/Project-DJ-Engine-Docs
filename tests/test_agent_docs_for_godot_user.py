from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOC_ROOT = ROOT / "agent_docs_for_godot_user"
ROOT_DOC = DOC_ROOT / "README.md"
CORE_DOC = DOC_ROOT / "harness/core/README.md"
INPUT_DOC = DOC_ROOT / "harness/input/README.md"
JUDGE_DOC = DOC_ROOT / "harness/judge/README.md"
UTIL_DOC = DOC_ROOT / "harness/util/README.md"
TROUBLESHOOTING_DOC = DOC_ROOT / "harness/basic_troubleshooting/README.md"
REPORT_DOC = DOC_ROOT / "report/README.md"
BUG_REPORT_DOC = DOC_ROOT / "report/bug_report.md"
FEATURE_REQUEST_DOC = DOC_ROOT / "report/feature_request.md"
TABLES_PATH = ROOT / "docs_harness/important_assets/editor_format/tables.json"


class AgentDocsForGodotUserTests(unittest.TestCase):
    def test_required_harness_files_exist(self) -> None:
        for relative in [
            "README.md",
            "harness/README.md",
            "harness/core/README.md",
            "harness/input/README.md",
            "harness/judge/README.md",
            "harness/util/README.md",
            "harness/basic_troubleshooting/README.md",
            "report/README.md",
            "report/bug_report.md",
            "report/feature_request.md",
        ]:
            path = DOC_ROOT / relative
            self.assertTrue(path.exists(), f"missing {relative}")
            self.assertGreater(path.stat().st_size, 0, f"empty {relative}")

    def test_core_doc_preserves_mix_args_table_rows(self) -> None:
        core = CORE_DOC.read_text(encoding="utf-8")
        tables = json.loads(TABLES_PATH.read_text(encoding="utf-8"))["tables"]
        for row in tables["mix_data_table"]["rows"]:
            for cell in row:
                self.assertIn(cell, core)

    def test_core_doc_explains_eight_point_interpolation(self) -> None:
        core = CORE_DOC.read_text(encoding="utf-8")
        for phrase in [
            "8PointValues",
            "eight comma-separated data points",
            "ITPL_LINEAR",
            "ITPL_COSINE",
            "ITPL_CUBIC",
            "ITPL_FLAT",
            "filter frequency",
            "Wet amount",
        ]:
            self.assertIn(phrase, core)

    def test_core_doc_warns_editor_arg_is_one_shot(self) -> None:
        core = CORE_DOC.read_text(encoding="utf-8")
        for phrase in [
            "one `PDJE_EDITOR_ARG` per row",
            "one-shot carrier",
            "Do not reuse",
            "InitMixArg()",
            "PDJE_EDITOR_ARG.new()",
            "stale",
            "partial payload",
        ]:
            self.assertIn(phrase, core)

    def test_module_docs_cover_required_godot_classes(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [CORE_DOC, INPUT_DOC, JUDGE_DOC, UTIL_DOC]
        )
        for symbol in [
            "PDJE_Wrapper",
            "PlayerWrapper",
            "EditorWrapper",
            "PDJE_EDITOR_ARG",
            "PDJE_Input_Module",
            "InputLine",
            "PDJE_Judge_Module",
            "PDJE_KeyValueDB",
            "PDJE_RelationalDB",
            "PDJE_VectorDB",
            "PDJE_MIR",
            "PDJE_AI",
            "PDJE_BeatThisDetector",
            "PDJE_BeatThisResult",
        ]:
            self.assertIn(symbol, combined)

    def test_util_ai_doc_has_model_and_api_boundaries(self) -> None:
        util = UTIL_DOC.read_text(encoding="utf-8")
        for phrase in [
            "generic ONNX Runtime",
            "current Godot wrapper exposes only Beat This",
            "res://models/beat_this.onnx",
            "CreateBeatThisDetector",
            "DetectPCM",
            "DetectMusic",
            ".onnx",
        ]:
            self.assertIn(phrase, util)

    def test_troubleshooting_covers_deployment_and_bug_policy(self) -> None:
        troubleshooting = TROUBLESHOOTING_DOC.read_text(encoding="utf-8")
        for phrase in [
            "PDJE_Wrapper.gdextension",
            "PDJE_godot_wrapper",
            "onnxruntime.dll",
            "libonnxruntime.so",
            "libonnxruntime*.dylib",
            "zlib",
            "highway",
            "Beat This model",
            "Discord first",
            "https://discord.gg/2Pwju7xhmS",
            "https://github.com/Rliop913/PDJE-Godot-Plugin",
        ]:
            self.assertIn(phrase, troubleshooting)

    def test_report_templates_cover_discord_policy_and_required_fields(self) -> None:
        report = REPORT_DOC.read_text(encoding="utf-8")
        bug_report = BUG_REPORT_DOC.read_text(encoding="utf-8")
        feature_request = FEATURE_REQUEST_DOC.read_text(encoding="utf-8")
        combined = "\n".join([report, bug_report, feature_request])
        normalized_combined = " ".join(combined.split())

        for phrase in [
            "https://discord.gg/2Pwju7xhmS",
            "bug report",
            "feature request",
            "minimal reproduction",
            "private music, database, or model files",
            "Godot version",
            "OS and architecture",
            "Logs",
            "PDJE_VERSION",
            "PDJE_WRAPPER_VERSION",
            ".gdextension path",
            "Wrapper library path",
            "Runtime library path",
            "Root DB path",
            "Audio asset information",
            ".onnx path",
            "Input device information",
            "Desired Godot API shape",
            "Current workaround",
            "Compatibility impact",
            "Deployment or packaging impact",
            "human developer",
            "must directly review and send",
            "Developers welcome",
            "agent-generated",
            "make reporting easier",
            "Automated reporting or unreviewed message sending is discouraged",
            "personal information",
            "```text",
        ]:
            self.assertIn(phrase, normalized_combined)

    def test_root_and_troubleshooting_link_report_templates(self) -> None:
        root_doc = ROOT_DOC.read_text(encoding="utf-8")
        troubleshooting = TROUBLESHOOTING_DOC.read_text(encoding="utf-8")
        normalized_root = " ".join(root_doc.split())
        normalized_troubleshooting = " ".join(troubleshooting.split())

        self.assertIn("[report/](report/)", root_doc)
        self.assertIn("[../../report/](../../report/)", troubleshooting)
        self.assertIn(
            "A human developer must directly review and send", normalized_root
        )
        self.assertIn(
            "A human developer must directly review and send",
            normalized_troubleshooting,
        )
        self.assertIn(
            "Developers welcome bug reports and feature requests",
            normalized_root,
        )
        self.assertIn(
            "Developers welcome bug reports and feature requests",
            normalized_troubleshooting,
        )
        self.assertIn("agent-generated report drafts are fine", normalized_root)
        self.assertIn(
            "agent-generated report drafts are fine", normalized_troubleshooting
        )
        self.assertIn(
            "Automated reporting or unreviewed message sending", normalized_root
        )
        self.assertIn(
            "Automated reporting or unreviewed message sending",
            normalized_troubleshooting,
        )

    def test_input_and_judge_docs_capture_runtime_order(self) -> None:
        input_doc = INPUT_DOC.read_text(encoding="utf-8")
        judge = JUDGE_DOC.read_text(encoding="utf-8")
        for phrase in [
            "InitWithOptions",
            "GetDevs",
            "GetMIDIDevs",
            "Config",
            "InitializeInputLine",
            "emit_input_signal",
        ]:
            self.assertIn(phrase, input_doc)
        for phrase in [
            "AddDataLines",
            "DeviceAdd",
            "MIDI_DeviceAdd",
            "SetRule",
            "SetNotes",
            "StartJudge",
            "EndJudge",
        ]:
            self.assertIn(phrase, judge)


if __name__ == "__main__":
    unittest.main()
