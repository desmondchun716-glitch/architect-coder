from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from _common import DEFAULT_FORBIDDEN, is_forbidden


PATTERNS = [
    (
        "private_key",
        "high",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    ),
    (
        "openai_api_key",
        "high",
        re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    ),
    (
        "github_token",
        "high",
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    ),
    (
        "slack_token",
        "high",
        re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b"),
    ),
    (
        "aws_access_key",
        "high",
        re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    ),
    (
        "credential_assignment",
        "high",
        re.compile(
            r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token|credential)"
            r"\b\s*[:=]\s*[\"']?(?!<|redacted|example|changeme|null|none)"
            r"[^\s\"']{8,}"
        ),
    ),
]


def scan_text(text: str, source: str = "<text>") -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        for finding_type, severity, pattern in PATTERNS:
            if pattern.search(line):
                key = (finding_type, line_number)
                if key not in seen:
                    findings.append(
                        {
                            "type": finding_type,
                            "line": line_number,
                            "severity": severity,
                        }
                    )
                    seen.add(key)
    return {
        "source": source,
        "safe": not any(item["severity"] == "high" for item in findings),
        "findings": findings,
    }


def redact_text(text: str) -> str:
    redacted = text
    for finding_type, _severity, pattern in PATTERNS:
        redacted = pattern.sub(f"[REDACTED:{finding_type}]", redacted)
    return redacted


def scan_file(path: str | Path) -> dict[str, Any]:
    file_path = Path(path).expanduser().resolve()
    if is_forbidden(file_path, DEFAULT_FORBIDDEN):
        return {
            "source": str(file_path),
            "safe": False,
            "findings": [
                {"type": "forbidden_path", "line": 0, "severity": "high"}
            ],
        }
    try:
        text = file_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"File not found: {file_path}") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"File is not valid UTF-8 text: {file_path}") from exc
    return scan_text(text, str(file_path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan text for likely secrets.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="UTF-8 text file to scan")
    group.add_argument("--text", help="Literal text to scan")
    args = parser.parse_args()
    try:
        result = scan_file(args.file) if args.file else scan_text(args.text)
    except ValueError as exc:
        print(json.dumps({"safe": False, "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["safe"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
