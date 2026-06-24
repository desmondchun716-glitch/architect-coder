# Architecture Playbook

## Minimum useful architecture

Cover this chain:

`goal -> system boundary -> constraints -> options -> decision -> tradeoffs -> risks -> verification`

Map business outcomes to components and observable acceptance criteria. Identify
callers, data ownership, trust boundaries, failure modes, and rollback paths.

## Choose the artifact

- Use a short inline decision for a local, reversible choice.
- Use `assets/templates/design_doc.md` for a multi-module or high-risk change.
- Use `assets/templates/adr.md` for a durable decision whose alternatives and costs
  should survive the current task.
- Read `references/adr_agent_ready.md` when the ADR should guide future agents.
- Use `assets/templates/nfr_matrix.md` when non-functional requirements drive design.

## Decision quality

Compare at least two plausible options when the choice is consequential. Include
`Option 0: Do nothing / keep current design` when it is realistic. Prefer the
least complex option that satisfies known constraints.

For each decision, state:

- what changes and what remains stable;
- why this boundary belongs here;
- operational and maintenance cost;
- compatibility and migration impact;
- failure and rollback behavior;
- how the decision will be tested.

Use recommendation strength for architecture reviews and proposals:

- `Strong`: evidence is concrete, impact is clear, risk is bounded, and the
  smallest useful fix is known.
- `Worth exploring`: the signal is real but needs a spike, measurement, or
  focused review.
- `Speculative`: plausible but insufficient evidence; do not implement without
  more data.

Do not move `Speculative` recommendations into an implementation plan. Do not
claim production readiness from document review alone.

## Decision stress test

Use this only for high-impact decisions: migrations, public API or schema breaks,
new dependencies, security or privacy choices, external writes, reliability
tradeoffs, or hard-to-reverse module boundaries.

Ask:

- What fails first?
- What assumption would make this decision wrong?
- What quality attribute are we sacrificing?
- What would make us revisit this in 3-6 months?
- Who or what system is affected?
- How expensive is reversal?
- What is the smallest reversible step?

Record at least one failure mode and a rollback or reversal path before treating
the decision as ready to implement.

## Architecture friction scan

Use this when reviewing an existing repository for architecture problems. Cite
real files, modules, callers, or tests.

Look for:

- concept scattering: one concept spread across too many files or modules;
- shallow module: abstraction adds indirection but little simplification;
- leaking boundary: callers need internal details;
- test pain: behavior is hard to verify through public boundaries;
- locality loss: understanding behavior requires jumping across too many layers;
- dependency direction smell: low-level modules import high-level concerns;
- deletion test: removing an abstraction concentrates complexity or only moves it.

Report each finding as:

```text
Friction signal:
- Type:
- Evidence location:
- Why it matters:
- Smallest useful fix:
- Recommendation strength: Strong / Worth exploring / Speculative
```

Do not recommend broad rewrites without evidence and a smallest useful patch or
verification path.
