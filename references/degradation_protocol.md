# Degradation Protocol

## Missing Obsidian

Continue repository work, create a local Markdown draft if useful, report that no
vault write occurred, and state the missing configuration or path.

## Missing test command

Infer candidates from manifests and documentation. If still uncertain, do not invent
a result. Provide manual checks and mark automated tests `not run`.

## Partial quality gate

When one or more checks pass but other categories are skipped, report the gate as
`partial`, list skipped categories, and do not summarize it as fully passed.

## Repository too large

Read instructions, manifests, top-level structure, and task-relevant call paths.
Search by symbol or feature. Record that context may be incomplete.

## Benchmark unavailable

Do not claim improvement. Preserve the proposed benchmark command, environment, and
expected metric; mark the result `unverified`.

## User unavailable

Continue through non-blocking assumptions. Stop before a blocking, destructive, or
externally visible action.

## Tool failure

Capture the exact failure, try a safe equivalent path, and distinguish tooling
failure from product failure.
