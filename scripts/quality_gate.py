from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Any

from _common import load_config, prepare_command, run_cli
from project_context_scan import scan_project
from secret_scan_guard import redact_text


def _overall_status(results: list[dict[str, Any]]) -> str:
    statuses = {item["status"] for item in results}
    if "failed" in statuses:
        return "failed"
    if statuses == {"passed"}:
        return "passed"
    if "passed" in statuses and "skipped" in statuses:
        return "partial"
    return "skipped"


def _tail_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    return redact_text(value)[-4000:]


def _run(command: str, cwd: Path, timeout: int, *, allow_shell: bool) -> dict[str, Any]:
    started = time.perf_counter()
    reported_command = redact_text(command)
    try:
        prepared_command, shell = prepare_command(command, allow_shell=allow_shell)
        completed = subprocess.run(
            prepared_command,
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except ValueError as exc:
        return {
            "command": reported_command,
            "status": "failed",
            "exit_code": None,
            "duration_seconds": 0,
            "shell": False,
            "stdout": "",
            "stderr": str(exc),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": reported_command,
            "status": "failed",
            "exit_code": None,
            "duration_seconds": round(time.perf_counter() - started, 3),
            "shell": allow_shell,
            "stdout": _tail_output(exc.stdout),
            "stderr": f"Timed out after {timeout} seconds",
        }
    except OSError as exc:
        return {
            "command": reported_command,
            "status": "failed",
            "exit_code": None,
            "duration_seconds": round(time.perf_counter() - started, 3),
            "shell": False,
            "stdout": "",
            "stderr": str(exc),
        }
    return {
        "command": reported_command,
        "status": "passed" if completed.returncode == 0 else "failed",
        "exit_code": completed.returncode,
        "duration_seconds": round(time.perf_counter() - started, 3),
        "shell": shell,
        "stdout": _tail_output(completed.stdout),
        "stderr": _tail_output(completed.stderr),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run configured repository quality checks.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--config", default=".architect-coder.json")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument(
        "--allow-shell",
        action="store_true",
        help="Allow shell=True for reviewed quality commands.",
    )
    parser.add_argument(
        "--fail-on-skip",
        action="store_true",
        help="Return non-zero when any configured quality category is skipped.",
    )
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = root / config_path

    quality: dict[str, Any] = {}
    if config_path.exists():
        quality = load_config(config_path).get("quality") or {}
    allow_shell = bool(args.allow_shell or quality.get("allow_shell"))
    inferred = scan_project(root)
    categories = {
        "lint": quality.get("lint_command")
        or (inferred["lint_commands"][0] if inferred["lint_commands"] else None),
        "typecheck": quality.get("typecheck_command")
        or (
            inferred["typecheck_commands"][0]
            if inferred["typecheck_commands"]
            else None
        ),
        "test": quality.get("test_command")
        or (inferred["test_commands"][0] if inferred["test_commands"] else None),
    }

    results = []
    for category, command in categories.items():
        if command:
            result = _run(str(command), root, args.timeout, allow_shell=allow_shell)
        else:
            result = {
                "command": None,
                "status": "skipped",
                "exit_code": None,
                "duration_seconds": 0,
                "shell": False,
                "stdout": "",
                "stderr": "No configured or inferred command",
            }
        result["category"] = category
        results.append(result)

    overall = _overall_status(results)
    report = {
        "root": str(root),
        "overall": overall,
        "shell_warning": (
            "Shell execution was explicitly enabled; commands must be reviewed."
            if allow_shell
            else ""
        ),
        "skipped_categories": [
            item["category"] for item in results if item["status"] == "skipped"
        ],
        "results": results,
    }
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("# Quality Gate\n")
        print(f"- Overall: `{report['overall']}`\n")
        if report["shell_warning"]:
            print(f"- Shell execution: `enabled`; {report['shell_warning']}\n")
        print("| Check | Status | Exit | Seconds | Shell |")
        print("|---|---|---:|---:|---|")
        for item in results:
            print(
                f"| {item['category']} | {item['status']} | "
                f"{item['exit_code'] if item['exit_code'] is not None else '-'} | "
                f"{item['duration_seconds']} | {item['shell']} |"
            )
        for item in results:
            if item["status"] == "failed":
                print(f"\n## {item['category']} failure\n")
                print("```text")
                print((item["stderr"] or item["stdout"] or "No output").strip())
                print("```")
    if report["overall"] == "failed":
        return 1
    if args.fail_on_skip and report["overall"] in {"partial", "skipped"}:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
