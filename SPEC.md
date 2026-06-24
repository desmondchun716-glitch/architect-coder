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
