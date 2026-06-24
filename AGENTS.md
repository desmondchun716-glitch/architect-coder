# Agent Instructions

## Scope

- This repository is an Agent Skills package. Keep `SKILL.md` as the portable runtime contract.
- Keep provider-specific entrypoints thin and reference-backed; do not fork the workflow into divergent Codex, Claude, or generic-agent copies.
- Do not add LLM Council runtime, child skills, enterprise governance, or default visual dashboards.

## Commands

| Task | Command |
|---|---|
| Eval contract schema | `python scripts/eval_contract_check.py --eval-dir evals --format markdown` |
| Compile scripts | `python -m compileall scripts` |
| Inspect files | `rg --files` |

## External References

| Need | File |
|---|---|
| Portable install guidance | `references/agent_portability.md` |
| Skill contract | `SPEC.md` |
| Source/provenance | `SOURCES.md` |
| ADR quality rules | `references/adr_agent_ready.md` |

## Key Conventions

- Use relative paths from the skill root in `SKILL.md` and references.
- Put runtime depth in `references/`, templates in `assets/templates/`, and deterministic helpers in `scripts/`.
- After `compileall`, remove or ignore `scripts/__pycache__/`.
- Treat `.architect-coder.json` and `CLAUDE.local.md` as local-only files.
