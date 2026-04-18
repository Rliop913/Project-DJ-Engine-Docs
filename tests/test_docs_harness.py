from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools import docs_harness


DOC_SCOPE_FIXTURE = {
    "version": 1,
    "editable_globs": ["srcs/*.rst"],
    "readonly_globs": [
        "srcs/api/**",
        "srcs/xml/**",
        "docs/**",
        "PDJE-Godot-Plugin/Project-DJ-Engine/document_sources/**",
    ],
    "repos": {
        "wrapper": {
            "rules": [
                {
                    "globs": [
                        "PDJE-Godot-Plugin/Wrapper_Includes/**",
                        "PDJE-Godot-Plugin/**/swig*",
                        "PDJE-Godot-Plugin/extension_api.json",
                    ],
                    "docs": [
                        "srcs/Getting Started.rst",
                        "srcs/Core_Engine.rst",
                        "srcs/Input_Engine.rst",
                        "srcs/Judge_Engine.rst",
                        "srcs/PDJE_For_AI_Agents.rst",
                    ],
                }
            ]
        },
        "core": {
            "rules": [
                {
                    "globs": [
                        "PDJE-Godot-Plugin/Project-DJ-Engine/include/core/**"
                    ],
                    "docs": [
                        "srcs/Core_Engine.rst",
                        "srcs/Editor_Workflows.rst",
                        "srcs/Developer_Onboarding.rst",
                        "srcs/PDJE_For_AI_Agents.rst",
                    ],
                }
            ]
        },
    },
}


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def init_repo(path: Path, branch: str) -> None:
    subprocess.run(["git", "init", "-b", branch, str(path)], check=True, capture_output=True, text=True)
    git(path, "config", "user.email", "test@example.com")
    git(path, "config", "user.name", "Test User")


def write_and_commit(repo: Path, relative_path: str, content: str, message: str) -> str:
    path = repo / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    git(repo, "add", relative_path)
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


class DocsHarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "docs_harness").mkdir()
        (self.root / "srcs").mkdir()
        (self.root / "docs_harness/doc_scope.yaml").write_text(
            json.dumps(DOC_SCOPE_FIXTURE, indent=2) + "\n",
            encoding="utf-8",
        )

        self.wrapper = self.root / "PDJE-Godot-Plugin"
        init_repo(self.wrapper, "master")
        write_and_commit(
            self.wrapper,
            "Wrapper_Includes/wrapper.hpp",
            "wrapper v1\n",
            "initial wrapper",
        )

        self.core = self.wrapper / "Project-DJ-Engine"
        init_repo(self.core, "main")
        write_and_commit(
            self.core,
            "include/core/core.hpp",
            "core v1\n",
            "initial core",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_stamp_baseline_records_current_branch_and_commit(self) -> None:
        payload = docs_harness.stamp_baseline(self.root)
        baseline = json.loads(
            (self.root / "docs_harness/source_baseline.lock.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload, baseline)
        self.assertEqual(baseline["wrapper"]["branch"], "master")
        self.assertEqual(baseline["core"]["branch"], "main")
        self.assertEqual(
            baseline["wrapper"]["documented_commit"],
            git(self.wrapper, "rev-parse", "HEAD"),
        )
        self.assertEqual(
            baseline["core"]["documented_commit"],
            git(self.core, "rev-parse", "HEAD"),
        )

    def test_record_source_heads_writes_current_clone_hashes(self) -> None:
        payload = docs_harness.record_source_heads(self.root)
        heads = json.loads(
            (self.root / "docs_harness/source_heads.lock.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload, heads)
        self.assertEqual(heads["wrapper"]["branch"], "master")
        self.assertEqual(heads["core"]["branch"], "main")
        self.assertEqual(
            heads["wrapper"]["head_commit"],
            git(self.wrapper, "rev-parse", "HEAD"),
        )
        self.assertEqual(
            heads["core"]["head_commit"],
            git(self.core, "rev-parse", "HEAD"),
        )

    def test_diff_context_maps_changed_files_to_impacted_docs(self) -> None:
        docs_harness.stamp_baseline(self.root)
        write_and_commit(
            self.core,
            "include/core/new_feature.hpp",
            "core v2\n",
            "core update",
        )
        write_and_commit(
            self.wrapper,
            "Wrapper_Includes/bridge.hpp",
            "wrapper v2\n",
            "wrapper update",
        )

        runtime = docs_harness.load_runtime(self.root)
        contexts = {context["repo"]: context for context in docs_harness.build_diff_context(runtime)}

        self.assertIn(
            "PDJE-Godot-Plugin/Project-DJ-Engine/include/core/new_feature.hpp",
            contexts["core"]["changed_files"],
        )
        self.assertIn("srcs/Core_Engine.rst", contexts["core"]["impacted_docs"])
        self.assertIn("srcs/Editor_Workflows.rst", contexts["core"]["editable_docs"])

        self.assertIn(
            "PDJE-Godot-Plugin/Wrapper_Includes/bridge.hpp",
            contexts["wrapper"]["changed_files"],
        )
        self.assertIn("srcs/Input_Engine.rst", contexts["wrapper"]["impacted_docs"])
        self.assertIn(
            "PDJE-Godot-Plugin/Project-DJ-Engine/document_sources/**",
            contexts["wrapper"]["readonly_paths"],
        )

    def test_status_detects_branch_mismatch(self) -> None:
        docs_harness.stamp_baseline(self.root)
        git(self.wrapper, "checkout", "-b", "feature/docs-refresh")

        runtime = docs_harness.load_runtime(self.root)
        statuses = docs_harness.build_statuses(runtime)
        mismatches = docs_harness.branch_mismatches(statuses)

        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0]["repo"], "wrapper")
        self.assertFalse(mismatches[0]["branch_matches"])

    def test_wrapper_status_ignores_nested_core_gitlink_drift(self) -> None:
        docs_harness.stamp_baseline(self.root)
        write_and_commit(
            self.core,
            "include/core/runtime.hpp",
            "core v2\n",
            "advance nested core",
        )

        runtime = docs_harness.load_runtime(self.root)
        statuses = {status["repo"]: status for status in docs_harness.build_statuses(runtime)}

        self.assertFalse(statuses["wrapper"]["has_uncommitted_changes"])
        self.assertEqual(statuses["wrapper"]["uncommitted_paths"], [])


if __name__ == "__main__":
    unittest.main()
