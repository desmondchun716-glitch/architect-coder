# architect-coder

Architecture-aware coding workflow for real repositories.

`architect-coder` helps AI coding agents make safer changes in growing codebases.
It guides the agent to inspect the project, choose the right files, plan small
reversible patches, run proportionate checks, and finish with evidence-backed
acceptance.

`architect-coder` 适合真实仓库、长期项目和需要持续维护的产品。它让 Coding Agent
在动手改代码前先理解项目结构、约束、测试方式和架构边界，再用最小可逆的方式完成
实现、重构、迁移或优化。

## What it helps with

- Repository understanding before edits
- Boundary-respecting implementation and refactors
- Bug fixes with reproduction and regression checks
- PR and code review with file, line, severity, and evidence
- Performance work with baseline and before/after comparison
- Agent-ready ADRs for durable architecture decisions
- Safe Obsidian architecture memory with preview, hash, and secret checks
- Token-first routing so agents read only the references needed for the task

核心能力可以概括为：少读无关内容、读准关键文件、改小补丁、跑真实检查、给出可复核
证据。

## When to use it

Use `architect-coder` when a real repository task needs judgment, not just
keystrokes:

- feature work and multi-file implementation
- bug fixes and regressions
- refactors and migrations
- performance optimization
- security, code, or PR review
- architecture decisions and ADRs
- quality gates and evidence-backed acceptance
- Obsidian architecture knowledge sync

当任务涉及多文件影响、架构边界、测试验证、安全风险、性能指标或长期决策时，使用
这个 Skill。

Skip it for simple explanations, isolated snippets, translations, exam writing,
or one-off shell commands.

## Core workflow

```text
scan → route → plan → change → verify → accept → remember
```

1. Scan project instructions, manifests, nearby code, tests, and CI.
2. Route to the smallest set of task-specific references.
3. Plan the smallest reversible change.
4. Edit only after reading full affected files and relevant callers, tests,
   schemas, migrations, configuration, and public interfaces.
5. Run focused checks and report skipped or unavailable checks honestly.
6. Finish with changed files, evidence, risks, rollback, and acceptance items.
7. Record durable decisions as ADRs or safe Obsidian notes when useful.

先读仓库，再选择需要的 reference；先确认影响面，再修改；最后用测试、检查、benchmark
或手动验证说明结果。

## Token-first routing

Normal task target:

```text
SKILL.md + 1–3 references
```

| Task | Read |
|---|---|
| Code change | [coding_rules.md](references/coding_rules.md) + one matching language guide |
| Bug fix | [debugging_protocol.md](references/debugging_protocol.md) + coding rules |
| PR or code review | [review_protocol.md](references/review_protocol.md) |
| Performance | [optimization_playbook.md](references/optimization_playbook.md) |
| Durable decision | [adr_agent_ready.md](references/adr_agent_ready.md) |
| Obsidian write | relevant Obsidian references + preview/write helpers |

The agent should not pre-read every reference. Bundled scripts can be executed
without reading their source; source is needed only when changing or debugging
the script.

普通任务的目标是少读、读准。不要为了保险把所有 reference 都读进上下文。

## Context rule

Summaries, repository maps, search results, script output, and notes are navigation
tools. They help identify candidate files, but they are not authority for an edit.

Before changing code, read the complete affected files and relevant callers,
tests, schemas, migrations, configuration, or public interfaces. Refresh stale
summaries after edits.

摘要、搜索结果和 repo map 只能用来找方向。真正修改代码前，必须阅读完整相关文件和
测试。

## Quick start

For repository implementation:

```text
Use architect-coder for this change. Inspect the repository first, then give a
small reversible plan with the exact files you need to read or edit, the checks
you will run, and the rollback path.
```

```text
请用 architect-coder 处理这个仓库任务。先检查项目结构和相关文件，再给出最小可逆
计划，说明要读或修改哪些文件、运行哪些检查、如何回滚。
```

For bug fixes:

```text
Use the architect-coder debugging protocol. Reproduce the failure or explain why
it cannot run, isolate the smallest failing scope, show evidence, apply the fix,
and add a regression check.
```

```text
请按 architect-coder 的 debugging protocol 修复这个 bug：先复现或说明无法复现的
原因，再定位最小失败范围，给出证据，做最小修复，并补充回归检查。
```

For reviews:

```text
Use the architect-coder review protocol. Each finding needs status, severity,
file, line, evidence, realistic trigger, smallest safe fix, and verification.
```

```text
请按 architect-coder 的 review protocol 评审这个 PR。每个 finding 都要有状态、
严重度、文件、行号、证据、真实触发场景、最小安全修复和验证方式。
```

## Install

### Claude Code

Personal skill:

```bash
git clone https://github.com/desmondchun716-glitch/architect-coder.git ~/.claude/skills/architect-coder
```

Project skill:

```bash
git submodule add https://github.com/desmondchun716-glitch/architect-coder.git .claude/skills/architect-coder
```

Invoke it with `/architect-coder`.

### Codex

Project skill:

```bash
git submodule add https://github.com/desmondchun716-glitch/architect-coder.git .agents/skills/architect-coder
```

You can also clone or copy the directory to `.agents/skills/architect-coder`.
Invoke it with `$architect-coder` or a repository task that matches the Skill
description.

### Other Agent Skills clients

Place the folder in the client's skills search path and keep the directory layout
intact. See [agent_portability.md](references/agent_portability.md) for supported
placements and invocation patterns.

## Validate

Run before publishing changes:

```bash
python scripts/eval_contract_check.py --eval-dir evals --format markdown
python -m compileall scripts
git diff --check
```

Remove or leave `scripts/__pycache__/` untracked after compilation.

## Design principles

- Read enough context before editing.
- Use summaries and repository maps for navigation only.
- Make small coherent patches and reuse existing patterns.
- Preserve public behavior unless a break is explicitly approved.
- Test changed behavior and realistic failure paths.
- Label checks as `passed`, `failed`, `partial`, `skipped`, `not run`, or
  `unverified`.
- Stop before migrations, public API breaks, new dependencies, destructive
  actions, or external writes without authority.
- Keep durable architecture decisions traceable.

## Repository notes

- `SKILL.md` is the portable runtime contract.
- `agents/openai.yaml` contains Codex display metadata.
- `references/` contains task-specific guidance loaded on demand.
- `scripts/` contains deterministic helpers that can run without being loaded
  into model context.
- `AGENTS.md` and `CLAUDE.md` are thin repository instruction bridges.
