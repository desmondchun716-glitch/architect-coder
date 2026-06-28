# Coding Rules

1. Before editing, read complete affected files plus relevant callers, tests, schemas, and public interfaces.
2. Maps, search, snippets, summaries, and notes are navigation only; refresh stale views after edits.
3. Make the smallest coherent patch and avoid unrelated cleanup.
4. Preserve public behavior unless a break is explicitly authorized.
5. Add dependencies only for a concrete need and with required approval; consult exact-version primary docs or source when their contract affects correctness.
6. Keep external I/O behind testable boundaries.
7. Validate inputs at trust boundaries and return safe, actionable errors.
8. Never log secrets, credentials, private data, raw tokens, or unsafe payloads.
9. Prefer configuration for real variation; reject magic values and speculative flags.
10. Test behavior, failure paths, and justified seams; never weaken tests to hide wrong behavior.
11. Keep rollback possible for migrations and high-risk changes.
12. Explain architecture and compatibility impact after implementation.

## Complex implementation plan

Use only for multi-file, cross-module, migration, security, performance, debugging, or review-triggered work:

- `Task`: concrete result.
- `Why`: evidence or dependency that makes it necessary.
- `Uses`: exact files, never directories; include relevant callers, tests, schemas, migrations, configuration, or interfaces.
- `Change type`: add, modify, remove, or verify.
- `Validation`: focused proof and proportionate regression check.
- `Scope boundary`: intentionally untouched behavior and files.

Narrow single-file changes do not need this structure.

## Testing ladder

- Unit: pure logic, boundaries, and failure cases.
- Integration: module boundaries, data flow, persistence, and API contracts.
- End-to-end or manual: critical user flow or unavailable automation.
- Benchmark: every performance claim, with comparable before/after conditions.
- Not run: state reason, risk, and the next verification step.

Select the lowest sufficient rung, adding broader checks with blast radius. For review-only work, follow [review_protocol.md](review_protocol.md); do not fix without a request.
