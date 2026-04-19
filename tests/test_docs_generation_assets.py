from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SPEC_PATH = ROOT / "docs_harness" / "SRCS_DOC_GENERATION_SPEC.md"
ASSET_ROOT = ROOT / "docs_harness" / "important_assets" / "editor_format"
MANIFEST_PATH = ASSET_ROOT / "assets_manifest.json"
TABLES_PATH = ASSET_ROOT / "tables.json"
IMAGE_PATH = ASSET_ROOT / "eightPoint_example.png"
SOURCE_IMAGE_PATH = ROOT / "srcs" / "_static" / "eightPoint_example.png"


class DocsGenerationAssetsTests(unittest.TestCase):
    def test_spec_mentions_all_handwritten_rst_pages(self) -> None:
        spec = SPEC_PATH.read_text(encoding="utf-8")
        for name in [
            "srcs/index.rst",
            "srcs/Getting Started.rst",
            "srcs/Developer_Onboarding.rst",
            "srcs/Core_Engine.rst",
            "srcs/Editor_Workflows.rst",
            "srcs/Input_Engine.rst",
            "srcs/Judge_Engine.rst",
            "srcs/Util_Engine.rst",
            "srcs/Data_Lines.rst",
            "srcs/Editor_Format.rst",
            "srcs/FX_ARGS.rst",
            "srcs/PDJE_For_AI_Agents.rst",
        ]:
            self.assertIn(name, spec)

    def test_editor_format_manifest_lists_required_assets(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        asset_ids = {asset["asset_id"] for asset in manifest["assets"]}
        self.assertEqual(
            asset_ids,
            {
                "track_data_format",
                "music_metadata_format",
                "mix_data_format",
                "mix_data_table",
                "note_data_format",
                "interpolation_keywords",
                "mix_json_keys",
                "eight_point_example",
            },
        )

    def test_table_assets_exist_in_tables_json(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        tables = json.loads(TABLES_PATH.read_text(encoding="utf-8"))["tables"]
        for asset in manifest["assets"]:
            if asset["kind"] == "table":
                self.assertIn(asset["asset_id"], tables)
                self.assertTrue(tables[asset["asset_id"]]["rows"])

    def test_editor_format_image_snapshot_matches_source_image(self) -> None:
        self.assertTrue(IMAGE_PATH.exists())
        self.assertEqual(IMAGE_PATH.read_bytes(), SOURCE_IMAGE_PATH.read_bytes())

    def test_spec_requires_editor_format_asset_backed_explanations(self) -> None:
        spec = SPEC_PATH.read_text(encoding="utf-8")
        self.assertIn("Missing prose counts as a generation failure", spec)
        self.assertIn("The `Mix JSON Keys` table is mandatory", spec)
        self.assertIn("eight control points", spec)
        self.assertIn("stretched across the event span", spec)

    def test_spec_freezes_index_structure_without_explicit_request(self) -> None:
        spec = SPEC_PATH.read_text(encoding="utf-8")
        self.assertIn("Treat `index.rst` as structure-frozen", spec)
        self.assertIn("Do not add, remove, reorder, rename,", spec)
        self.assertIn("without an explicit user request, preserve the current composition of", spec)


if __name__ == "__main__":
    unittest.main()
