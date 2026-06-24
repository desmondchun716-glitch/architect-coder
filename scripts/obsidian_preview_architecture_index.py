from __future__ import annotations

import argparse
import json

from _common import (
    build_architecture_index_base,
    configured_obsidian_asset_path,
    load_config,
    now_iso,
    run_cli,
    sha256_text,
)
from secret_scan_guard import scan_text


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preview a deterministic Obsidian Bases architecture index."
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    config = load_config(args.config)
    allowed, target = configured_obsidian_asset_path(
        config,
        config_key="architecture_index_path",
        default_relative_path="architecture-index.base",
        allowed_suffixes={".base"},
    )
    preview_timestamp = now_iso()
    content = build_architecture_index_base(config=config, allowed=allowed)
    content_sha256 = sha256_text(content)
    scan = scan_text(content, f"generated architecture index base for {target.name}")
    result = {
        "safe": scan["safe"],
        "asset_type": "architecture_index_base",
        "target_path": str(target),
        "relative_path": target.relative_to(allowed).as_posix(),
        "exists": target.exists(),
        "write_mode": "replace_existing" if target.exists() else "create",
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
        print("# Obsidian Architecture Index Preview\n")
        print(f"- Target: `{result['relative_path']}`")
        print(f"- Existing file: `{result['exists']}`")
        print(f"- Mode: `{result['write_mode']}`")
        print(f"- Content SHA-256: `{result['content_sha256']}`")
        print(f"- Preview timestamp: `{result['preview_timestamp']}`")
        print(f"- Secret scan safe: `{result['safe']}`\n")
        if scan["safe"]:
            print("```yaml")
            print(content.rstrip())
            print("```")
        else:
            print("Full preview content omitted because the generated base contains likely secrets.")
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
