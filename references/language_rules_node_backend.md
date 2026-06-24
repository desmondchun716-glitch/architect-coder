# Node Backend Rules

- Preserve controller/service/repository boundaries when they exist; do not impose
  them mechanically on tiny modules.
- Validate and normalize all external input.
- Keep internal stack traces, SQL, tokens, and filesystem paths out of responses.
- Treat schema changes as migrations with rollback and compatibility analysis.
- Set explicit timeouts for external calls; add retry only for safe idempotent cases.
- Use fallback or circuit-breaking only when failure semantics are understood.
- Include correlation identifiers in logs without recording sensitive values.
- Version or otherwise protect public API changes.
- Make transaction boundaries and partial-failure behavior explicit.
