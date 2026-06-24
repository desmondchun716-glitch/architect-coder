from __future__ import annotations

import argparse
import json
import sys

from _common import (
    build_architecture_index_base,
    configured_obsidian_asset_path,
    load_config,
    run_cli,
    validate_preview_contract,
)
from secret_scan_guard import scan_text


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create or replace the Obsidian Bases architecture index after preview."
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--confirm-preview", action="store_true")
    parser.add_argument("--expected-relative-path", required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument(
        "--expected-write-mode",
        choices=["create", "replace_existing"],
        required=True,
        help="write_mode from the accepted preview.",
    )
    parser.add_argument(
        "--allow-replace",
        action="store_true",
        help="Required when the target .base file already exists.",
    )
    args = parser.parse_args()
    if not args.confirm_preview:
        parser.error("Run preview first, then pass --confirm-preview")

    config = load_config(args.config)
    allowed, target = configured_obsidian_asset_path(
        config,
        config_key="architecture_index_path",
        default_relative_path="architecture-index.base",
        allowed_suffixes={".base"},
        create_parent=True,
    )
    actual_write_mode = "replace_existing" if target.exists() else "create"
    if actual_write_mode != args.expected_write_mode:
        raise ValueError(
            "Preview write mode mismatch: "
            f"expected {args.expected_write_mode}, got {actual_write_mode}. "
            "Rerun preview before writing."
        )
    if actual_write_mode == "replace_existing" and not args.allow_replace:
        raise ValueError(
            "Target architecture index already exists; rerun preview and pass "
            "--allow-replace only after the replacement is accepted."
        )

    content = build_architecture_index_base(config=config, allowed=allowed)
    content_sha256 = validate_preview_contract(
        allowed=allowed,
        target=target,
        content=content,
        expected_relative_path=args.expected_relative_path,
        expected_sha256=args.expected_sha256,
    )
    scan = scan_text(content, f"generated architecture index base for {target.name}")
    if not scan["safe"]:
        print(json.dumps(scan, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    existed = target.exists()
    target.write_text(content, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "status": "replaced" if existed else "created",
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
