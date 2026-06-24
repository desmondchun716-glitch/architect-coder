from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from _common import (
    forbidden_patterns,
    is_forbidden,
    load_config,
    obsidian_roots,
    run_cli,
)


def summarize(text: str, limit: int = 280) -> str:
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("---")
    ]
    return " ".join(lines)[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description="Search an allowed Obsidian project root.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--max-results", type=int, default=10)
    parser.add_argument("--max-files", type=int, default=500)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()

    config = load_config(args.config)
    _, _, allowed = obsidian_roots(config)
    patterns = forbidden_patterns(config)
    terms = [part.casefold() for part in args.query.split() if part.strip()]
    matches = []
    scanned = 0
    for path in allowed.rglob("*.md"):
        if scanned >= args.max_files:
            break
        if is_forbidden(path.relative_to(allowed), patterns):
            continue
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        haystack = f"{path.name}\n{text}".casefold()
        score = sum(haystack.count(term) for term in terms)
        if score:
            stat = path.stat()
            matches.append(
                {
                    "path": path.relative_to(allowed).as_posix(),
                    "modified_time": datetime.fromtimestamp(
                        stat.st_mtime
                    ).astimezone().isoformat(timespec="seconds"),
                    "title": path.stem,
                    "summary": summarize(text),
                    "score": score,
                }
            )
    matches.sort(key=lambda item: (item["score"], item["modified_time"]), reverse=True)
    result = {
        "query": args.query,
        "allowed_root": str(allowed),
        "files_scanned": scanned,
        "scan_truncated": scanned >= args.max_files,
        "matched_notes": matches[: args.max_results],
    }
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# Obsidian search: {args.query}\n")
        for item in result["matched_notes"]:
            print(f"- `{item['path']}` ({item['modified_time']}): {item['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
