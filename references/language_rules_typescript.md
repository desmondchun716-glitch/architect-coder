# TypeScript and React Rules

- Preserve strong types; avoid `any` unless isolated and justified.
- Separate domain types, transport types, and UI state.
- Keep calculations pure and move side effects into services or focused hooks.
- Keep API access centralized rather than scattered across components.
- Model loading, empty, error, and retry states explicitly.
- Keep component boundaries aligned with ownership and change frequency.
- Do not refactor unrelated UI while implementing a feature.
- Centralize environment and runtime configuration.
- Put replaceable search, ranking, provider, or AI fallback logic behind a small
  adapter or strategy boundary outside the UI.
- Add tests at pure logic, hook/service, and user-visible behavior boundaries as
  appropriate.
