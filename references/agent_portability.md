# Agent Portability

Use this reference when installing, packaging, or adapting `architect-coder`
outside its original Codex environment.

## Portable Core

- `SKILL.md` is the runtime contract and should stay compatible with the Agent
  Skills format.
- `references/`, `assets/`, `scripts/`, and `evals/` are addressed by relative
  paths from the skill root.
- Provider-specific metadata should be additive. Do not move core workflow rules
  into a single provider's config file.

## Install Targets

| Runtime | Recommended placement | Invocation |
|---|---|---|
| Claude Code personal skill | `~/.claude/skills/architect-coder` | `/architect-coder` |
| Claude Code project skill | `.claude/skills/architect-coder` | `/architect-coder` |
| Codex project skill | `.agents/skills/architect-coder` | `$architect-coder` or implicit trigger |
| Generic Agent Skills client | the client's configured skills directory | client-specific |
| Manual agent fallback | any readable checkout | ask the agent to read `SKILL.md` first |

For manual fallback, give the agent this instruction:

```text
Read SKILL.md in this folder first. Follow its progressive-disclosure routing:
load only the referenced files needed for the task, keep relative paths intact,
and treat scripts/assets as local helpers rather than hidden instructions.
```

## Provider-Specific Files

- `agents/openai.yaml` is Codex display metadata. Other agents may ignore it.
- `AGENTS.md` gives repository-level instructions for Codex and other agents
  that read `AGENTS.md`.
- `CLAUDE.md` imports `AGENTS.md` and adds only Claude Code placement guidance.
- `.architect-coder.json` is local runtime configuration for optional Obsidian
  and quality-gate helpers. Do not commit personal vault paths.

## Compatibility Rules

- Keep `SKILL.md` frontmatter conservative: `name`, `description`, and portable
  compatibility metadata are safe; provider-only controls need a SPEC note.
- Prefer a new file in `references/` over long provider-specific instructions in
  `AGENTS.md` or `CLAUDE.md`.
- If a provider supports extra tool allowlists or invocation controls, configure
  them outside the portable core unless all supported clients can ignore them.
- Validate changes with the eval contract checker and Python compilation before
  pushing.
