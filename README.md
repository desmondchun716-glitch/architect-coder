# architect-coder

When a product grows, code generation is no longer enough. You need decisions
that survive future changes, refactors that respect existing boundaries, tests
that mean something, and architecture memory that future agents can actually use.

`architect-coder` is a portable Agent Skill for that stage of building. It guides
coding agents through architecture-aware repository work: reading the terrain,
stress-testing decisions, planning reversible changes, implementing narrowly,
validating honestly, and turning important decisions into agent-ready ADRs and
safe Obsidian knowledge assets.

如果你想做的不是一次性 demo，而是一个真正会长期迭代的大项目、大产品，
`architect-coder` 就是给 Coding Agent 加上的架构师工作流。它不会让 AI 一上来就
乱改文件，而是先读懂仓库地形，识别风险、边界和取舍，再用最小可逆的方式完成实现、
重构、迁移或优化。

每一次关键修改都要有检查、有证据、有验收；每一个长期架构决策都可以沉淀为
Agent-ready ADR 和安全的 Obsidian 架构记忆。它的目标不是让 AI 更快地堆代码，
而是让你的产品越做越大时，依然清晰、稳定、可维护。

## When To Use

Use this skill when a patch needs judgment, not just keystrokes: architecture
decisions, feature implementation, refactors, migrations, diagnostics,
optimization, code review, Obsidian knowledge sync, or evidence-backed
acceptance.

Avoid it for simple explanations, isolated snippets, translations, exam writing,
or one-off shell commands.

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

Invoke it with `/architect-coder` when a task needs architecture plus code.

### Codex

Project skill:

```bash
git submodule add https://github.com/desmondchun716-glitch/architect-coder.git .agents/skills/architect-coder
```

You can also clone or copy this directory to `.agents/skills/architect-coder`.
Invoke it by mentioning `$architect-coder` or by asking for architecture-led
repository engineering work.

### Other Agent Skills Clients

Place this folder in the client's skills search path. The portable core is:

- `SKILL.md`
- `references/`
- `assets/`
- `scripts/`

Keep the directory layout intact because the skill uses relative links.

## Validate

Run these checks before publishing changes:

```bash
python scripts/eval_contract_check.py --eval-dir evals --format markdown
python -m compileall scripts
```

If `compileall` creates `scripts/__pycache__/`, leave it untracked or remove it
before committing.

## Repository Notes

- `SKILL.md` is the portable runtime contract.
- `agents/openai.yaml` is Codex display metadata.
- `AGENTS.md` and `CLAUDE.md` are thin repository instruction bridges.
- `references/agent_portability.md` explains how to keep future changes
  usable across agent runtimes.
