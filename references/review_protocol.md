# Review Protocol

Use for code, PR, architecture, or security review and for review-triggered fixes. Review-only requests do not authorize edits.

## Finding contract

Each actionable finding must include:

- `status`: `confirmed`, `suspected`, `follow-up`, or `stop-and-escalate`
- `severity`: `blocker`, `high`, `medium`, or `low`
- `file` and `lines`
- `evidence`
- `realistic trigger`
- `smallest safe fix`
- `verification`

Sort findings by severity. If there are no findings, say so and name residual testing or context gaps.

## Verification policy

- A diff-only finding is `suspected` unless the defect is fully contained and provable in the diff.
- `confirmed` requires verification against the real code path.
- Read the full affected file and inspect relevant callers, tests, public contracts, data flow, or security boundary as applicable.
- Separate observed facts from inference. Do not inflate style preferences into defects.
- For security findings, describe a realistic attacker capability and trigger; avoid unsupported exploit claims.

## Scope governor

Freeze the original task boundary before fixing findings. Address in-scope blockers and high-severity defects first. Classify adjacent improvements as `follow-up` unless required for correctness.

Use `stop-and-escalate` when the smallest safe fix requires a migration, public API break, broad rewrite, release-process change, new dependency, destructive action, external authority, or sensitive-data decision. After two failed fix cycles, stop, preserve evidence, and reclassify instead of widening the patch repeatedly.

## Review-triggered fixes

When fixes are requested, verify each finding before editing, follow [coding_rules.md](coding_rules.md), and add a focused check for the realistic trigger. Report findings rejected by evidence as well as those fixed. A review summary or automated comment is navigation, not edit authority.
