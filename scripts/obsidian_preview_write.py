from __future__ import annotations

import argparse
import json

from _common import (
    build_obsidian_note_content,
    load_config,
    now_iso,
    read_input,
    run_cli,
    sha256_text,
    target_note_path,
)
from secret_scan_guard import scan_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview a safe Obsidian note write.")
    parser.add_argument("--config", required=True)
    parser.add_argument(
        "--type", choices=["worklog", "adr", "acceptance", "note"], required=True
    )
    parser.add_argument("--title", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--source-repo", default="")
    parser.add_argument("--related-file", action="append", default=[])
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    config = load_config(args.config)
    body = read_input(args.input, config=config).strip()
    allowed, target = target_note_path(
        config,
        args.type,
        args.title,
        unique=args.type in {"adr", "acceptance", "note"},
    )
    preview_timestamp = now_iso()
    content, write_mode = build_obsidian_note_content(
        config=config,
        note_type=args.type,
        title=args.title,
        body=body,
        target=target,
        append_existing=args.type == "worklog" and target.exists(),
        update_timestamp=preview_timestamp,
        source_repo=args.source_repo,
        related_files=args.related_file,
    )
    content_sha256 = sha256_text(content)
    scan = scan_text(content, f"generated {args.type} note from {args.input}")
    result = {
        "safe": scan["safe"],
        "note_type": args.type,
        "target_path": str(target),
        "relative_path": target.relative_to(allowed).as_posix(),
        "exists": target.exists(),
        "write_mode": write_mode,
        "content_sha256": content_sha256,
        "preview_timestamp": preview_timestamp,
        "secret_scan": scan,
    }
    if scan["safe"]:
        result["content"] = content
    else:
        result["content_omitted"] = True
        result["omission_reason"] = (
            "Generated content contains high-severity secret-scan findings; "
            "full content is not printed."
        )
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("# Obsidian Write Preview\n")
        print(f"- Target: `{result['relative_path']}`")
        print(f"- Existing file: `{result['exists']}`")
        print(f"- Mode: `{result['write_mode']}`")
        print(f"- Content SHA-256: `{result['content_sha256']}`")
        print(f"- Preview timestamp: `{result['preview_timestamp']}`")
        print(f"- Secret scan safe: `{result['safe']}`\n")
        if scan["safe"]:
            print("```markdown")
            print(content.rstrip())
            print("```")
        else:
            print("Full preview content omitted because the generated note contains likely secrets.")
            print("\n| Type | Severity | Line |")
            print("|---|---|---:|")
            for finding in scan["findings"]:
                print(
                    f"| {finding['type']} | {finding['severity']} | "
                    f"{finding['line']} |"
                )
    return 0 if scan["safe"] else 1


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
