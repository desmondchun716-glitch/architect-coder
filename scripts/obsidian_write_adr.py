from __future__ import annotations

import argparse
import json
import sys

from _common import (
    build_obsidian_note_content,
    load_config,
    read_input,
    run_cli,
    target_note_path,
    validate_preview_contract,
)
from secret_scan_guard import scan_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a unique Proposed ADR note.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--source-repo", default="")
    parser.add_argument("--related-file", action="append", default=[])
    parser.add_argument("--confirm-preview", action="store_true")
    parser.add_argument("--expected-relative-path", required=True)
    parser.add_argument("--expected-sha256", required=True)
    args = parser.parse_args()
    if not args.confirm_preview:
        parser.error("Run preview first, then pass --confirm-preview")

    config = load_config(args.config)
    body = read_input(args.input, config=config).strip()
    allowed, target = target_note_path(
        config, "adr", args.title, create_dir=False, unique=True
    )
    content, _write_mode = build_obsidian_note_content(
        config=config,
        note_type="adr",
        title=args.title,
        body=body,
        target=target,
        source_repo=args.source_repo,
        related_files=args.related_file,
    )
    content_sha256 = validate_preview_contract(
        allowed=allowed,
        target=target,
        content=content,
        expected_relative_path=args.expected_relative_path,
        expected_sha256=args.expected_sha256,
    )
    scan = scan_text(content, f"generated ADR note from {args.input}")
    if not scan["safe"]:
        print(json.dumps(scan, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "status": "created",
                "path": target.relative_to(allowed).as_posix(),
                "content_sha256": content_sha256,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
