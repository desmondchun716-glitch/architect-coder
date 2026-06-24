# Python Rules

- Use `pathlib` for paths and resolve untrusted paths before access.
- Add type hints to public and non-trivial functions.
- Prefer small pure functions; isolate filesystem, network, process, and database I/O.
- Use `argparse` for dependency-free CLIs; include help, clear exit codes, and JSON
  output when automation benefits.
- Validate configuration fields and fail with actionable messages.
- Avoid global mutable state and import-time side effects.
- Use atomic or append-only writes for important files.
- Prefer `pytest` conventions when the repository already uses pytest.
- Keep code compatible with configured Ruff, Black, mypy, or project tooling.
- Never expose secrets or unnecessary absolute paths in errors.
