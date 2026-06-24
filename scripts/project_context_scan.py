from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "target",
    "coverage",
}
EXTENSIONS = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".kt": "kotlin",
    ".cs": "csharp",
}


def _package_commands(path: Path) -> tuple[list[str], list[str], list[str]]:
    try:
        package = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [], [], []
    scripts = package.get("scripts") or {}
    tests = ["npm test"] if "test" in scripts else []
    lint = ["npm run lint"] if "lint" in scripts else []
    typecheck = ["npm run typecheck"] if "typecheck" in scripts else []
    return tests, lint, typecheck


def scan_project(root: str | Path, max_files: int = 5000) -> dict[str, Any]:
    project_root = Path(root).expanduser().resolve()
    if not project_root.is_dir():
        raise ValueError(f"Project root does not exist: {project_root}")

    names = {item.name.casefold(): item for item in project_root.iterdir()}
    instruction_names = ["agents.md", "claude.md"]
    manifest_names = [
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "cargo.toml",
        "go.mod",
        "pom.xml",
        "build.gradle",
    ]
    instructions = [
        item.name for name in instruction_names if (item := names.get(name))
    ]
    readmes = [
        item.name
        for key, item in names.items()
        if key.startswith("readme") and item.is_file()
    ]
    manifests = [
        item.name for name in manifest_names if (item := names.get(name))
    ]
    important_dirs = [
        name
        for name in ["src", "app", "lib", "tests", "test", "docs", ".github"]
        if (project_root / name).exists()
    ]

    counts: Counter[str] = Counter()
    scanned = 0
    for path in project_root.rglob("*"):
        if scanned >= max_files:
            break
        if any(part.casefold() in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            scanned += 1
            language = EXTENSIONS.get(path.suffix.casefold())
            if language:
                counts[language] += 1

    test_commands: list[str] = []
    lint_commands: list[str] = []
    typecheck_commands: list[str] = []
    package_path = project_root / "package.json"
    package_data: dict[str, Any] = {}
    if package_path.exists():
        test_commands, lint_commands, typecheck_commands = _package_commands(package_path)
        try:
            package_data = json.loads(package_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    if (project_root / "pyproject.toml").exists():
        pyproject_text = (project_root / "pyproject.toml").read_text(
            encoding="utf-8", errors="ignore"
        ).casefold()
        if "pytest" in pyproject_text:
            test_commands.append("python -m pytest")
        if "ruff" in pyproject_text:
            lint_commands.append("python -m ruff check .")
        if "mypy" in pyproject_text:
            typecheck_commands.append("python -m mypy .")
    if (project_root / "cargo.toml").exists():
        test_commands.append("cargo test")
        lint_commands.append("cargo clippy --all-targets --all-features")
    if (project_root / "go.mod").exists():
        test_commands.append("go test ./...")

    deps = {
        **(package_data.get("dependencies") or {}),
        **(package_data.get("devDependencies") or {}),
    }
    if "react" in deps and counts["typescript"]:
        project_type = "typescript-react"
    elif "package.json" in manifests:
        project_type = "node"
    elif "pyproject.toml" in manifests or counts["python"]:
        project_type = "python"
    elif "cargo.toml" in manifests:
        project_type = "rust"
    elif "go.mod" in manifests:
        project_type = "go"
    else:
        project_type = "unknown"

    return {
        "root": str(project_root),
        "project_type": project_type,
        "languages": dict(counts.most_common()),
        "instructions": instructions,
        "readmes": sorted(readmes),
        "manifests": manifests,
        "test_commands": list(dict.fromkeys(test_commands)),
        "lint_commands": list(dict.fromkeys(lint_commands)),
        "typecheck_commands": list(dict.fromkeys(typecheck_commands)),
        "important_dirs": important_dirs,
        "files_scanned": scanned,
        "scan_truncated": scanned >= max_files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Perform a bounded project context scan.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--max-files", type=int, default=5000)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()
    try:
        result = scan_project(args.root, max_files=args.max_files)
    except ValueError as exc:
        parser.error(str(exc))
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# Project Context\n\n- Type: `{result['project_type']}`")
        print(f"- Manifests: {', '.join(result['manifests']) or 'none'}")
        print(f"- Languages: {json.dumps(result['languages'], ensure_ascii=False)}")
        print(f"- Tests: {', '.join(result['test_commands']) or 'unknown'}")
        print(f"- Lint: {', '.join(result['lint_commands']) or 'unknown'}")
        print(f"- Typecheck: {', '.join(result['typecheck_commands']) or 'unknown'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
