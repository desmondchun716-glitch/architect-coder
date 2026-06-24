from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from _common import run_cli


LEGACY_REQUIRED = {
    "id": str,
    "prompt": str,
    "must_include": list,
    "must_not_include": list,
}

CONTRACT_REQUIRED = {
    "id": str,
    "prompt": str,
    "must_match": list,
    "must_not_match": list,
}


def _load_array(path: Path) -> list[Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a JSON array")
    return data


def _strings(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _check_shape(path: Path, item: Any, required: dict[str, type]) -> list[str]:
    issues: list[str] = []
    if not isinstance(item, dict):
        return [f"{path}: case is not an object"]
    case_id = item.get("id", "<missing id>")
    for field, expected_type in required.items():
        if not isinstance(item.get(field), expected_type):
            issues.append(f"{path}:{case_id}: {field} must be {expected_type.__name__}")
    for field in ("must_include", "must_not_include", "must_match", "must_not_match"):
        if field in item and not _strings(item[field]):
            issues.append(f"{path}:{case_id}: {field} must be a list of strings")
    if "pass_threshold" in item:
        threshold = item["pass_threshold"]
        if not isinstance(threshold, int) or threshold < 0:
            issues.append(f"{path}:{case_id}: pass_threshold must be a non-negative integer")
        elif "must_include" in item and threshold > len(item["must_include"]):
            issues.append(f"{path}:{case_id}: pass_threshold exceeds must_include count")
    if "should_trigger" in item and not isinstance(item["should_trigger"], bool):
        issues.append(f"{path}:{case_id}: should_trigger must be boolean")
    return issues


def validate_legacy(eval_dir: Path) -> list[str]:
    issues: list[str] = []
    for path in sorted(eval_dir.glob("*.json")):
        if path.name.endswith("_contracts.json"):
            continue
        try:
            cases = _load_array(path)
        except ValueError as exc:
            issues.append(str(exc))
            continue
        for item in cases:
            issues.extend(_check_shape(path, item, LEGACY_REQUIRED))
    return issues


def load_contracts(eval_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    path = eval_dir / "executable_contracts.json"
    issues: list[str] = []
    if not path.exists():
        return [], [f"{path}: missing executable contracts"]
    try:
        raw_cases = _load_array(path)
    except ValueError as exc:
        return [], [str(exc)]
    contracts: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in raw_cases:
        issues.extend(_check_shape(path, item, CONTRACT_REQUIRED))
        if not isinstance(item, dict):
            continue
        case_id = item.get("id", "<missing id>")
        if isinstance(case_id, str):
            if case_id in seen_ids:
                issues.append(f"{path}:{case_id}: duplicate contract id")
            seen_ids.add(case_id)
        for field in ("must_match", "must_not_match"):
            for pattern in item.get(field, []):
                try:
                    re.compile(pattern)
                except re.error as exc:
                    issues.append(f"{path}:{case_id}: invalid regex in {field}: {exc}")
        contracts.append(item)
    return contracts, issues


def run_contracts(
    contracts: list[dict[str, Any]], response_dir: Path
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for contract in contracts:
        case_id = contract["id"]
        response_path = response_dir / f"{case_id}.md"
        if not response_path.exists():
            results.append(
                {
                    "id": case_id,
                    "status": "failed",
                    "missing_response": str(response_path),
                    "missing_patterns": contract["must_match"],
                    "forbidden_patterns_found": [],
                }
            )
            continue
        text = response_path.read_text(encoding="utf-8", errors="replace")
        missing = [
            pattern
            for pattern in contract["must_match"]
            if not re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        ]
        forbidden = [
            pattern
            for pattern in contract["must_not_match"]
            if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        ]
        results.append(
            {
                "id": case_id,
                "status": "passed" if not missing and not forbidden else "failed",
                "missing_patterns": missing,
                "forbidden_patterns_found": forbidden,
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate architect-coder eval contracts and optional responses."
    )
    parser.add_argument("--eval-dir", default="evals")
    parser.add_argument(
        "--responses-dir",
        help="Directory containing one markdown response per executable contract id.",
    )
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()

    eval_dir = Path(args.eval_dir).expanduser().resolve()
    if not eval_dir.is_dir():
        raise ValueError(f"Eval directory not found: {eval_dir}")

    issues = validate_legacy(eval_dir)
    contracts, contract_issues = load_contracts(eval_dir)
    issues.extend(contract_issues)
    contract_results: list[dict[str, Any]] = []
    if args.responses_dir:
        response_dir = Path(args.responses_dir).expanduser().resolve()
        if not response_dir.is_dir():
            raise ValueError(f"Response directory not found: {response_dir}")
        contract_results = run_contracts(contracts, response_dir)

    failed_contracts = [
        item for item in contract_results if item["status"] != "passed"
    ]
    report = {
        "status": "failed" if issues or failed_contracts else "passed",
        "eval_dir": str(eval_dir),
        "schema_issues": issues,
        "contract_count": len(contracts),
        "semantic_contracts_run": bool(args.responses_dir),
        "contract_results": contract_results,
    }
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("# Eval Contract Check\n")
        print(f"- Status: `{report['status']}`")
        print(f"- Executable contracts: `{len(contracts)}`")
        print(f"- Semantic contracts run: `{report['semantic_contracts_run']}`")
        if issues:
            print("\n## Schema issues")
            for issue in issues:
                print(f"- {issue}")
        if contract_results:
            print("\n## Contract results")
            for result in contract_results:
                print(f"- {result['id']}: {result['status']}")
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
