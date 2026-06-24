# CLI Rules

- Default destructive operations to preview or `--dry-run`.
- Validate paths, configuration, and required arguments before side effects.
- Use stable exit codes: `0` success, non-zero failure, and document special codes.
- Send machine-readable output to stdout and diagnostics to stderr when practical.
- Offer JSON output for automation and concise human output for direct use.
- Never swallow subprocess failures; preserve a bounded stdout/stderr excerpt.
- Summarize batch results with succeeded, failed, and skipped counts.
- Make retries and overwrites explicit flags, not hidden behavior.
