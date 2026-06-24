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
    parser = argparse.ArgumentParser(description="Append a draft Obsidian worklog.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--source-repo", default="")
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--confirm-preview", action="store_true")
    parser.add_argument("--expected-relative-path", required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--preview-timestamp")
    args = parser.parse_args()
    if not args.confirm_preview:
        parser.error("Run preview first, then pass --confirm-preview")

    config = load_config(args.config)
    body = read_input(args.input, config=config).strip()
    allowed, target = target_note_path(
        config, "worklog", args.title, create_dir=False
    )
    append_existing = target.exists()
    if append_existing and not args.preview_timestamp:
        raise ValueError("Pass --preview-timestamp from preview output for worklog append")
    content, write_mode = build_obsidian_note_content(
        config=config,
        note_type="worklog",
        title=args.title,
        body=body,
        target=target,
        append_existing=append_existing,
        update_timestamp=args.preview_timestamp,
        source_repo=args.source_repo,
        related_files=args.changed_file,
    )
    content_sha256 = validate_preview_contract(
        allowed=allowed,
        target=target,
        content=content,
        expected_relative_path=args.expected_relative_path,
        expected_sha256=args.expected_sha256,
    )
    scan = scan_text(content, f"generated worklog note from {args.input}")
    if not scan["safe"]:
        print(json.dumps(scan, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    target.parent.mkdir(parents=True, exist_ok=True)
    if write_mode == "append":
        with target.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        mode = "appended"
    else:
        target.write_text(content, encoding="utf-8", newline="\n")
        mode = "created"
    print(
        json.dumps(
            {
                "status": mode,
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
