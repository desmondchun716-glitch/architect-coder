from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any

from _common import load_config, prepare_command, run_cli
from secret_scan_guard import redact_text


NUMBER = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)")


def run_once(
    command: str,
    cwd: Path,
    timeout: int,
    value_regex: str | None,
    *,
    allow_shell: bool,
) -> dict[str, Any]:
    prepared_command, shell = prepare_command(command, allow_shell=allow_shell)
    completed = subprocess.run(
        prepared_command,
        cwd=cwd,
        shell=shell,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if completed.returncode != 0:
        raise ValueError(
            f"Benchmark failed with exit code {completed.returncode}: "
            f"{redact_text(completed.stderr or completed.stdout)[-1000:]}"
        )
    if value_regex:
        pattern = re.compile(value_regex)
        match = pattern.search(completed.stdout)
        if not match:
            raise ValueError("Benchmark output did not match --value-regex")
        value = match.group(1) if match.groups() else match.group(0)
        rule = "regex_capture" if match.groups() else "regex_match"
        matched_text = match.group(0)
    else:
        matches = NUMBER.findall(completed.stdout)
        if not matches:
            raise ValueError("Benchmark output contained no numeric result")
        if len(matches) != 1:
            raise ValueError(
                "Benchmark output contains multiple numeric values; "
                "pass --value-regex"
            )
        value = matches[0]
        rule = "single_number"
        matched_text = value
    return {
        "value": float(value),
        "extraction": {
            "rule": rule,
            "value_regex": value_regex,
            "matched_text": matched_text,
            "matched_value": value,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run and compare a numeric benchmark.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--config")
    parser.add_argument("--command")
    parser.add_argument("--before", type=float)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--metric", default="benchmark")
    parser.add_argument("--unit", default="")
    parser.add_argument("--higher-is-better", action="store_true")
    parser.add_argument("--max-cv", type=float, default=0.10)
    parser.add_argument("--value-regex")
    parser.add_argument(
        "--allow-shell",
        action="store_true",
        help="Allow shell=True for a reviewed benchmark command.",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    command = args.command
    allow_shell = args.allow_shell
    if not command and args.config:
        config = load_config(args.config)
        quality = config.get("quality") or {}
        command = quality.get("benchmark_command")
        allow_shell = allow_shell or bool(quality.get("allow_shell"))
    if not command:
        parser.error("Provide --command or a config with quality.benchmark_command")
    if args.runs < 1:
        parser.error("--runs must be at least 1")

    try:
        run_results = [
            run_once(
                command,
                root,
                args.timeout,
                args.value_regex,
                allow_shell=allow_shell,
            )
            for _ in range(args.runs)
        ]
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print(
            json.dumps({"status": "failed", "error": redact_text(str(exc))}),
            file=sys.stderr,
        )
        return 2

    samples = [float(item["value"]) for item in run_results]
    extractions = [item["extraction"] for item in run_results]
    after = statistics.mean(samples)
    deviation = statistics.pstdev(samples) if len(samples) > 1 else 0.0
    cv = deviation / abs(after) if after else 0.0
    stable = cv <= args.max_cv
    result: dict[str, Any] = {
        "status": "measured",
        "metric": args.metric,
        "unit": args.unit,
        "command": redact_text(command),
        "shell": allow_shell,
        "shell_warning": (
            "Shell execution was explicitly enabled; commands must be reviewed."
            if allow_shell
            else ""
        ),
        "samples": samples,
        "extractions": extractions,
        "after_mean": after,
        "coefficient_of_variation": cv,
        "stable": stable,
        "claim": "baseline recorded; no before value supplied",
    }
    if args.before is not None:
        raw_change = (
            ((after - args.before) / abs(args.before)) * 100
            if args.before != 0
            else None
        )
        improvement = (
            raw_change if args.higher_is_better else -raw_change
            if raw_change is not None
            else None
        )
        result.update(
            {
                "before": args.before,
                "change_percent": raw_change,
                "improvement_percent": improvement,
                "claim": (
                    "inconclusive due to benchmark variance"
                    if not stable
                    else "improved"
                    if improvement is not None and improvement > 0
                    else "regressed"
                    if improvement is not None and improvement < 0
                    else "unchanged"
                ),
            }
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
