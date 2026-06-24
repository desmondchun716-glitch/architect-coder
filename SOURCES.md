# Sources

## Local design inputs

| Source | Trust tier | Contribution | Usage constraints |
|---|---|---|---|
| `architect-coder_v0.2.3_improvement_discussion.md` | user-provided design input | Proposed agent-ready ADRs, trigger gate, `Option 0`, stress test, friction scan, recommendation strength, ADR metadata, and review-finding verification. | Adapted into compact runtime rules; no Council protocol, child skills, enterprise governance, or general PKM workflow adopted. |
| `architect-coder-review-context.md` | local project review context | Confirmed current v0.2.2 structure, validation history, and intentional constraints. | Used to preserve one integrated skill and avoid README/CHANGELOG/Council expansion. |

## Runtime guidance inputs

| Source | Trust tier | Contribution | Usage constraints |
|---|---|---|---|
| Local `skill-writer` skill | installed skill-authoring guidance | Required reference-backed layout, provenance capture, focused references, and validation expectations for material skill changes. | Applied only to this maintenance patch; no provider-specific mechanics added. |

## Portability inputs

| Source | Trust tier | Contribution | Usage constraints |
|---|---|---|---|
| [Agent Skills specification](https://agentskills.io/specification) | public open specification | Confirmed portable skill shape: `SKILL.md` frontmatter plus optional `references/`, `assets/`, and `scripts/`. | Keep the portable core provider-neutral; add runtime-specific files only as thin bridges. |
| [Codex skills documentation](https://developers.openai.com/codex/skills) | official current docs | Confirmed Codex project skill discovery through `.agents/skills/` and the role of `agents/openai.yaml`. | Do not make OpenAI metadata mandatory for other clients. |
| [Codex AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md) | official current docs | Confirmed `AGENTS.md` as the project instruction file Codex reads. | Keep root instructions concise and repository-specific. |
| [Claude Code skills documentation](https://code.claude.com/docs/en/skills) | official current docs | Confirmed Claude Code skill packaging, invocation, and project/personal skill placement. | Avoid Claude-only controls in the portable `SKILL.md` unless SPEC records why. |
| [Claude Code memory documentation](https://code.claude.com/docs/en/memory) | official current docs | Confirmed `CLAUDE.md` project memory and `@AGENTS.md` import strategy. | Use `CLAUDE.md` as a bridge instead of duplicating `AGENTS.md`. |
