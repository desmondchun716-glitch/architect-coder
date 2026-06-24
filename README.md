# architect-coder

Architecture-aware coding for agents that need to change real repositories
without losing the plot.

`architect-coder` turns a coding agent into a repo-aware engineering partner:
one that reads the codebase before touching it, makes tradeoffs explicit, keeps
changes small and reversible, and closes with tests, benchmarks, or honest
evidence.

中文：把“会写代码的 Agent”，升级成“会读仓库、会做取舍、会拿证据收尾的架构师搭档”。
它不是普通聊天模板，而是给 Codex、Claude Code 和兼容 Agent Skills 的其他 Agent
使用的技能包：先看项目真实地形，再处理架构边界、兼容性、测试、性能、知识库同步和
验收证据。

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
