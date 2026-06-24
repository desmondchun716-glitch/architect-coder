# Agent-Ready ADRs

Use this guide when a durable architecture decision should guide future agents,
not only explain past reasoning.

## Trigger gate

Create or update an ADR when at least one condition is true:

- the decision is hard to reverse;
- a public API, schema, dependency, infrastructure, auth, data model, or
  cross-module boundary changes;
- plausible alternatives exist and one or more were rejected;
- future agents need the rationale to avoid undoing the decision;
- the decision affects architecture, compatibility, reliability, security,
  privacy, operability, or rollback behavior.

Do not create a new ADR for:

- routine bug fixes;
- local implementation details;
- formatting or style choices covered by tooling;
- one-off experiments or throwaway prototypes;
- a decision already covered by an existing ADR. Update or supersede that ADR
  instead.

## Minimum structure

Use this structure for agent-ready ADRs:

- Decision summary
- Context and constraints
- Options considered, including `Option 0: Do nothing`
- Decision drivers
- Decision made
- Consequences
- Non-goals
- Implementation contract
- Lifecycle status

## Option 0 baseline

For durable decisions, include `Option 0: Do nothing / keep current design`.

Explain:

- current cost of doing nothing;
- risk of doing nothing;
- evidence that change is justified now;
- what would make no-change the better option.

## Implementation contract

Future agents should be able to act from the ADR without rediscovering the whole
decision. Include:

- affected files or modules;
- existing patterns to follow;
- patterns explicitly avoided;
- required tests, checks, or benchmarks;
- verification evidence already collected;
- rollback or reversal path;
- compatibility or migration constraints;
- open assumptions that must be rechecked.

## Lifecycle

Use one of these statuses:

- `Proposed`
- `Accepted`
- `Superseded`
- `Deprecated`

When an ADR conflicts with current code facts, treat the ADR as historical
context until the code path and project owner confirm an update.

## ADR metadata

Prefer this frontmatter for durable ADR notes:

```yaml
decision_id: ""
decision_scope: "local|repository|cross-system"
reversibility: "low|medium|high"
risk_level: "low|medium|high"
governed_files: []
supersedes: []
superseded_by: ""
verification_status: "unverified|partial|verified"
```

Use `governed_files` only for files or modules that the decision meaningfully
constrains. Do not add code comments or metadata to local helper functions just
to create a link.

Optional code comment for long-lived constraints:

```text
Governed by ADR-0004: Session revocation strategy
```

## Overengineering boundary

Do not introduce RACI, approval workflows, organization hierarchy, complex ADR
numbering, graph databases, bulk code-comment insertion, or default visual
dashboards. Keep the ADR useful, light, and tied to evidence.
