from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parent.parent
BASELINE_RELATIVE_PATH = Path("docs_harness/source_baseline.lock.json")
SOURCE_HEADS_RELATIVE_PATH = Path("docs_harness/source_heads.lock.json")
SCOPE_RELATIVE_PATH = Path("docs_harness/doc_scope.yaml")


@dataclass(frozen=True)
class RepoBaseline:
    name: str
    path: str
    branch: str
    documented_commit: str


@dataclass(frozen=True)
class RuntimeConfig:
    root: Path
    baseline_path: Path
    source_heads_path: Path
    scope_path: Path
    baseline_data: dict[str, Any]
    source_heads_data: dict[str, Any] | None
    scope_data: dict[str, Any]


class HarnessError(RuntimeError):
    """Raised when the local harness contract is invalid."""


def resolve_root(root: Path | None = None) -> Path:
    if root is not None:
        return root.resolve()
    env_root = os.environ.get("DOCS_HARNESS_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return DEFAULT_ROOT.resolve()


def load_json_document(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HarnessError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise HarnessError(f"Invalid JSON document: {path}: {exc}") from exc


def load_runtime(root: Path | None = None) -> RuntimeConfig:
    resolved_root = resolve_root(root)
    baseline_path = resolved_root / BASELINE_RELATIVE_PATH
    source_heads_path = resolved_root / SOURCE_HEADS_RELATIVE_PATH
    scope_path = resolved_root / SCOPE_RELATIVE_PATH
    baseline_data = load_json_document(baseline_path)
    source_heads_data = load_optional_json_document(source_heads_path)
    scope_data = load_json_document(scope_path)
    validate_baseline_data(baseline_data)
    if source_heads_data is not None:
        validate_source_heads_data(source_heads_data)
    validate_scope_data(scope_data)
    return RuntimeConfig(
        root=resolved_root,
        baseline_path=baseline_path,
        source_heads_path=source_heads_path,
        scope_path=scope_path,
        baseline_data=baseline_data,
        source_heads_data=source_heads_data,
        scope_data=scope_data,
    )


def validate_baseline_data(data: dict[str, Any]) -> None:
    if data.get("version") != 1:
        raise HarnessError("Unsupported baseline version")
    for repo_name in ("wrapper", "core"):
        repo = data.get(repo_name)
        if not isinstance(repo, dict):
            raise HarnessError(f"Missing baseline repo entry: {repo_name}")
        for key in ("path", "branch", "documented_commit"):
            value = repo.get(key)
            if not isinstance(value, str) or not value:
                raise HarnessError(f"Missing baseline field {repo_name}.{key}")


def validate_source_heads_data(data: dict[str, Any]) -> None:
    if data.get("version") != 1:
        raise HarnessError("Unsupported source heads version")
    for repo_name in ("wrapper", "core"):
        repo = data.get(repo_name)
        if not isinstance(repo, dict):
            raise HarnessError(f"Missing source heads repo entry: {repo_name}")
        for key in ("path", "branch", "head_commit"):
            value = repo.get(key)
            if not isinstance(value, str) or not value:
                raise HarnessError(f"Missing source heads field {repo_name}.{key}")


def validate_scope_data(data: dict[str, Any]) -> None:
    if data.get("version") != 1:
        raise HarnessError("Unsupported doc scope version")
    if not isinstance(data.get("editable_globs"), list):
        raise HarnessError("doc_scope editable_globs must be a list")
    if not isinstance(data.get("readonly_globs"), list):
        raise HarnessError("doc_scope readonly_globs must be a list")
    repos = data.get("repos")
    if not isinstance(repos, dict):
        raise HarnessError("doc_scope repos must be an object")
    for repo_name in ("wrapper", "core"):
        repo = repos.get(repo_name)
        if not isinstance(repo, dict):
            raise HarnessError(f"Missing doc scope repo entry: {repo_name}")
        rules = repo.get("rules")
        if not isinstance(rules, list):
            raise HarnessError(f"doc_scope {repo_name}.rules must be a list")


def load_optional_json_document(path: Path) -> dict[str, Any] | None:
    try:
        return load_json_document(path)
    except HarnessError as exc:
        if "Missing required file" in str(exc):
            return None
        raise


def iter_repo_baselines(runtime: RuntimeConfig) -> list[RepoBaseline]:
    repos: list[RepoBaseline] = []
    for repo_name in ("wrapper", "core"):
        repo_data = runtime.baseline_data[repo_name]
        repos.append(
            RepoBaseline(
                name=repo_name,
                path=repo_data["path"],
                branch=repo_data["branch"],
                documented_commit=repo_data["documented_commit"],
            )
        )
    return repos


def run_git(repo_root: Path, args: list[str], capture_output: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        text=True,
        capture_output=capture_output,
    )


def git_output(repo_root: Path, args: list[str]) -> str:
    result = run_git(repo_root, args)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise HarnessError(f"{repo_root}: {message}")
    return result.stdout.strip()


def repo_absolute_path(runtime: RuntimeConfig, repo: RepoBaseline) -> Path:
    return (runtime.root / repo.path).resolve()


def nested_repo_relative_paths(runtime: RuntimeConfig, repo: RepoBaseline) -> list[str]:
    repo_path = Path(repo.path)
    nested_paths: list[str] = []
    for candidate in iter_repo_baselines(runtime):
        candidate_path = Path(candidate.path)
        if candidate.name == repo.name:
            continue
        try:
            relative_path = candidate_path.relative_to(repo_path)
        except ValueError:
            continue
        if relative_path.parts:
            nested_paths.append(relative_path.as_posix())
    return sorted(nested_paths)


def dirty_paths(repo_root: Path, ignored_prefixes: list[str]) -> list[str]:
    result = run_git(repo_root, ["status", "--porcelain"])
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise HarnessError(f"{repo_root}: {message}")
    if not result.stdout:
        return []
    dirty: list[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else line
        path = path.split(" -> ", 1)[-1]
        if any(path == prefix or path.startswith(f"{prefix}/") for prefix in ignored_prefixes):
            continue
        dirty.append(path)
    return dirty


def repo_status(runtime: RuntimeConfig, repo: RepoBaseline) -> dict[str, Any]:
    repo_root = repo_absolute_path(runtime, repo)
    current_branch = git_output(repo_root, ["branch", "--show-current"])
    if not current_branch:
        current_branch = git_output(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    current_commit = git_output(repo_root, ["rev-parse", "HEAD"])
    uncommitted_paths = dirty_paths(repo_root, nested_repo_relative_paths(runtime, repo))
    recorded_source_head = None
    if runtime.source_heads_data is not None:
        recorded_source_head = runtime.source_heads_data[repo.name]["head_commit"]
    status = {
        "repo": repo.name,
        "path": repo.path,
        "expected_branch": repo.branch,
        "current_branch": current_branch,
        "documented_commit": repo.documented_commit,
        "recorded_source_head": recorded_source_head,
        "current_commit": current_commit,
        "branch_matches": current_branch == repo.branch,
        "has_uncommitted_changes": bool(uncommitted_paths),
        "uncommitted_paths": uncommitted_paths,
    }
    return status


def build_statuses(runtime: RuntimeConfig) -> list[dict[str, Any]]:
    return [repo_status(runtime, repo) for repo in iter_repo_baselines(runtime)]


def branch_mismatches(statuses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [status for status in statuses if not status["branch_matches"]]


def root_relative_changed_files(runtime: RuntimeConfig, repo: RepoBaseline) -> list[str]:
    repo_root = repo_absolute_path(runtime, repo)
    diff_range = f"{repo.documented_commit}..HEAD"
    output = git_output(repo_root, ["diff", "--name-only", diff_range, "--"])
    if not output:
        return []
    rooted_files = []
    for line in output.splitlines():
        relative_path = Path(repo.path) / Path(line)
        rooted_files.append(relative_path.as_posix())
    return rooted_files


def short_diffstat(runtime: RuntimeConfig, repo: RepoBaseline) -> str:
    repo_root = repo_absolute_path(runtime, repo)
    diff_range = f"{repo.documented_commit}..HEAD"
    return git_output(repo_root, ["diff", "--shortstat", diff_range, "--"])


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def impacted_docs(runtime: RuntimeConfig, repo: RepoBaseline, changed_files: list[str]) -> list[str]:
    docs: set[str] = set()
    rules = runtime.scope_data["repos"][repo.name]["rules"]
    for changed_file in changed_files:
        for rule in rules:
            if matches_any(changed_file, rule["globs"]):
                docs.update(rule["docs"])
    return sorted(docs)


def editable_docs(runtime: RuntimeConfig, docs: list[str]) -> list[str]:
    editable_globs = runtime.scope_data["editable_globs"]
    return sorted(doc for doc in docs if matches_any(doc, editable_globs))


def build_diff_context(runtime: RuntimeConfig) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []
    readonly_paths = sorted(runtime.scope_data["readonly_globs"])
    for repo in iter_repo_baselines(runtime):
        changed_files = root_relative_changed_files(runtime, repo)
        docs = impacted_docs(runtime, repo, changed_files)
        contexts.append(
            {
                "repo": repo.name,
                "path": repo.path,
                "documented_commit": repo.documented_commit,
                "current_commit": repo_status(runtime, repo)["current_commit"],
                "changed_files": changed_files,
                "diffstat": short_diffstat(runtime, repo),
                "impacted_docs": docs,
                "editable_docs": editable_docs(runtime, docs),
                "readonly_paths": readonly_paths,
            }
        )
    return contexts


def current_repo_snapshot(root: Path, name: str, path: str) -> dict[str, str]:
    repo_root = (root / path).resolve()
    branch = git_output(repo_root, ["branch", "--show-current"])
    if not branch:
        branch = git_output(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    commit = git_output(repo_root, ["rev-parse", "HEAD"])
    return {
        "path": path,
        "branch": branch,
        "documented_commit": commit,
    }


def current_source_heads_snapshot(root: Path, path: str) -> dict[str, str]:
    repo_root = (root / path).resolve()
    branch = git_output(repo_root, ["branch", "--show-current"])
    if not branch:
        branch = git_output(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    commit = git_output(repo_root, ["rev-parse", "HEAD"])
    return {
        "path": path,
        "branch": branch,
        "head_commit": commit,
    }


def write_baseline(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def record_source_heads(root: Path | None = None) -> dict[str, Any]:
    resolved_root = resolve_root(root)
    payload = {
        "version": 1,
        "wrapper": current_source_heads_snapshot(resolved_root, "PDJE-Godot-Plugin"),
        "core": current_source_heads_snapshot(
            resolved_root,
            "PDJE-Godot-Plugin/Project-DJ-Engine",
        ),
    }
    write_baseline(resolved_root / SOURCE_HEADS_RELATIVE_PATH, payload)
    return payload


def stamp_baseline(root: Path | None = None) -> dict[str, Any]:
    resolved_root = resolve_root(root)
    payload = {
        "version": 1,
        "wrapper": current_repo_snapshot(resolved_root, "wrapper", "PDJE-Godot-Plugin"),
        "core": current_repo_snapshot(
            resolved_root,
            "core",
            "PDJE-Godot-Plugin/Project-DJ-Engine",
        ),
    }
    write_baseline(resolved_root / BASELINE_RELATIVE_PATH, payload)
    return payload


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2))


def print_statuses(statuses: list[dict[str, Any]]) -> None:
    for status in statuses:
        print(
            f"{status['repo']}: branch {status['current_branch']} "
            f"(expected {status['expected_branch']}), "
            f"commit {status['current_commit']}, "
            f"dirty={status['has_uncommitted_changes']}"
        )


def print_diff_contexts(contexts: list[dict[str, Any]]) -> None:
    for context in contexts:
        print(
            f"{context['repo']}: {context['documented_commit']}..{context['current_commit']}"
        )
        if context["changed_files"]:
            for path in context["changed_files"]:
                print(f"  {path}")
        else:
            print("  no committed changes since baseline")
        if context["impacted_docs"]:
            print("  impacted docs:")
            for path in context["impacted_docs"]:
                print(f"  {path}")


def stream_show_diff(runtime: RuntimeConfig, repo_name: str, name_only: bool) -> int:
    repo = next(repo for repo in iter_repo_baselines(runtime) if repo.name == repo_name)
    repo_root = repo_absolute_path(runtime, repo)
    diff_range = f"{repo.documented_commit}..HEAD"
    args = ["diff"]
    if name_only:
        args.append("--name-only")
    args.extend([diff_range, "--"])
    result = run_git(repo_root, args, capture_output=False)
    return result.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect documentation baseline state")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Show current baseline status")
    status_parser.add_argument("--json", action="store_true", help="Emit JSON")

    diff_parser = subparsers.add_parser(
        "diff-context",
        help="Show changed files and impacted docs since the recorded baseline",
    )
    diff_parser.add_argument("--json", action="store_true", help="Emit JSON")

    show_parser = subparsers.add_parser("show-diff", help="Stream the raw source diff")
    show_parser.add_argument("--repo", choices=("wrapper", "core"), required=True)
    mode = show_parser.add_mutually_exclusive_group()
    mode.add_argument("--patch", action="store_true", help="Show the full patch")
    mode.add_argument("--name-only", action="store_true", help="Show only changed paths")

    record_parser = subparsers.add_parser(
        "record-source-heads",
        help="Record the current wrapper/core HEADs in a tracked file",
    )
    record_parser.add_argument("--json", action="store_true", help="Emit JSON")

    stamp_parser = subparsers.add_parser(
        "stamp-baseline",
        help="Record the current wrapper/core HEADs as the documentation baseline",
    )
    stamp_parser.add_argument("--json", action="store_true", help="Emit JSON")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "record-source-heads":
            payload = record_source_heads()
            if args.json:
                print_json(payload)
            else:
                print(
                    "Recorded current wrapper/core HEADs in "
                    f"{SOURCE_HEADS_RELATIVE_PATH.as_posix()}"
                )
            return 0

        if args.command == "stamp-baseline":
            payload = stamp_baseline()
            if args.json:
                print_json(payload)
            else:
                print(
                    "Recorded documentation baseline for wrapper and core in "
                    f"{BASELINE_RELATIVE_PATH.as_posix()}"
                )
            return 0

        runtime = load_runtime()

        if args.command == "status":
            statuses = build_statuses(runtime)
            if args.json:
                print_json(statuses)
            else:
                print_statuses(statuses)
            return 1 if branch_mismatches(statuses) else 0

        if args.command == "diff-context":
            statuses = build_statuses(runtime)
            contexts = build_diff_context(runtime)
            if args.json:
                print_json(contexts)
            else:
                print_diff_contexts(contexts)
            return 1 if branch_mismatches(statuses) else 0

        if args.command == "show-diff":
            return stream_show_diff(runtime, args.repo, name_only=args.name_only)

        parser.error(f"Unknown command: {args.command}")
        return 2
    except HarnessError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
