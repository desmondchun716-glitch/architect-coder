# architect-coder SPEC

## Scope

`architect-coder` is one integrated skill for non-trivial repository engineering
work where architecture, implementation, validation, optimization, Obsidian
knowledge sync, and acceptance evidence need to stay connected.

## v0.2.3 contract

The skill now treats durable architecture decisions as agent-ready artifacts:

- durable ADRs include trigger boundaries, `Option 0`, non-goals, implementation
  contract, verification criteria, rollback path, and lifecycle status;
- architecture reviews use concrete evidence locations and recommendation
  strength: `Strong`, `Worth exploring`, or `Speculative`;
- speculative findings do not enter implementation plans without more evidence;
- review findings are hypotheses until checked against the real code path;
- Obsidian ADR metadata can link decisions to governed files and verification
  status without creating a graph database or bulk code annotations.

## v0.2.4 hardening contract

The skill hardens safety and reliability without expanding runtime scope:

- Obsidian read summaries must not expose secret-like content from otherwise
  allowed Markdown notes;
- benchmark extraction metadata must redact secret-like matched text even on
  successful runs;
- executable eval contract IDs must be unique;
- high-confidence token scanning should cover common modern token forms without
  noisy entropy heuristics;
- partial quality gates must be clearly distinguishable from fully passed gates.

## v0.2.5 token-first execution routing contract

The skill keeps `SKILL.md` as a compact runtime router:

- normal tasks target `SKILL.md` plus one to three task-relevant references;
- summaries, repository maps, snippets, script output, and notes are navigation
  only;
- full affected files and relevant callers, tests, schemas, migrations,
  configuration, and public interfaces must be read before editing;
- bundled scripts can run without loading their source; read script source only
  when changing or debugging that script;
- debugging and review protocols are conditional references, not default runtime
  load.

Regex contracts are deterministic smoke checks. Token savings, reference read
sets, and coding-quality retention require paired trace or forward-test evidence.

## Portability contract

The skill is distributed as a portable Agent Skills package, not a Codex-only
prompt. `SKILL.md` remains the runtime contract; provider-specific files are thin
bridges:

- `AGENTS.md` for repository-level agent instructions;
- `CLAUDE.md` for Claude Code project memory and `AGENTS.md` import;
- `agents/openai.yaml` for Codex display metadata.

Cross-agent changes must preserve relative paths, avoid duplicating the workflow
into provider-specific files, and keep installation guidance in
`references/agent_portability.md`.

## Non-goals

- Do not split the skill into architecture, coding, review, or Obsidian child
  skills.
- Do not add LLM Council roles or voting to runtime guidance.
- Do not turn the skill into a general Obsidian or PKM tool.
- Do not add enterprise governance workflows, RACI, approval chains, or visual
  dashboards by default.

## Validation

Before releasing a change to this skill, run the deterministic eval contract
checker and Python compilation for scripts. When possible, also run focused
script checks for changed helpers and inspect generated Markdown/Base output.
