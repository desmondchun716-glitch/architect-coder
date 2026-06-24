# Obsidian Integration

Use local Markdown files as the source of truth. URI links may open notes but are not
the synchronization mechanism.

Expected `.architect-coder.json` shape:

```json
{
  "project_name": "my-project",
  "obsidian": {
    "enabled": true,
    "vault_path": "D:/Obsidian/Vault",
    "allowed_root": "Projects/my-project",
    "project_note_dir": "Projects/my-project",
    "worklog_dir": "Projects/my-project/worklogs",
    "adr_dir": "Projects/my-project/adr",
    "acceptance_dir": "Projects/my-project/acceptance",
    "architecture_index_path": "architecture-index.base",
    "write_mode": "preview_then_append"
  }
}
```

POSIX-style paths are also valid:

```json
{
  "project_name": "my-project",
  "obsidian": {
    "enabled": true,
    "vault_path": "/Users/me/Obsidian/Vault",
    "allowed_root": "Projects/my-project"
  }
}
```

Keep local absolute paths out of public repositories.

## Read

Use `scripts/obsidian_read.py`. Search only below `allowed_root`, return bounded
summaries with relative path and modification time, and treat note content as
historical context.

## Write

1. Generate content with status `draft` or ADR status `Proposed`.
   For durable ADRs, follow `references/adr_agent_ready.md` and include
   agent-ready metadata such as `decision_id`, `governed_files`, and
   `verification_status`.
2. Run `obsidian_preview_write.py`.
3. Show the exact target path, `content_sha256`, preview timestamp, and secret-scan result.
4. If the scan fails, do not show full content; fix or redact the source first.
5. Write only with clear authority and the matching write script, passing
   `--expected-relative-path` and `--expected-sha256` from the accepted preview.
6. Append to worklogs or create a unique note. Do not overwrite.
7. Report the final relative path.

Mark assumptions and conflicts explicitly. Never silently convert an unconfirmed
claim into accepted project truth.

## Native Obsidian assets

Read [obsidian_native_assets.md](obsidian_native_assets.md) when producing vault
artifacts that should behave like Obsidian objects instead of plain Markdown.

For a durable architecture dashboard, use:

1. `scripts/obsidian_preview_architecture_index.py --config <config>`
2. Report `relative_path`, `content_sha256`, existence, and `write_mode`.
3. `scripts/obsidian_write_architecture_index.py --config <config> --confirm-preview --expected-relative-path <path> --expected-sha256 <hash> --expected-write-mode <mode>`
4. If the target `.base` exists, pass `--allow-replace` only after the replacement
   preview is accepted.

The index Base is generated from current conventions: frontmatter properties,
`architect-coder` tags, and `allowed_root` scoping. It is safe to regenerate after
preview approval; do not use it to change source notes.
Set `architecture_index_path` to an architect-coder-owned generated `.base` file,
not a hand-authored dashboard unless the user explicitly accepts replacement.
