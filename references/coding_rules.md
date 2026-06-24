# Coding Rules

1. Read adjacent code and tests before editing.
2. Make the smallest coherent patch; avoid unrelated cleanup.
3. Preserve public behavior unless a break is explicitly authorized.
4. Do not add dependencies without a concrete need and approval when required.
5. Keep external I/O behind testable boundaries.
6. Validate inputs at trust boundaries and return safe, actionable errors.
7. Do not log secrets, credentials, private data, raw tokens, or unsafe payloads.
8. Prefer configuration for real variation; reject magic values and speculative flags.
9. Add or update tests for behavior, failure paths, and extension seams.
10. Do not weaken tests to make incorrect behavior pass.
11. Keep a rollback path for migrations and high-risk changes.
12. Explain architecture and compatibility impact after implementation.

When reviewing rather than changing code, report concrete defects with file and line
evidence. Do not implement fixes unless requested.
