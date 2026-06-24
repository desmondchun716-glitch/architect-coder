# Clarification Protocol

## Classify uncertainty

Ask before acting when the answer changes authority, compatibility, stored data,
security, external state, cost, or the success metric.

Blocking examples:

- Which latency, memory, cost, reliability, or maintainability metric defines “faster”?
- May a public API or serialized format break?
- May a dependency be added?
- May a database schema or user data be migrated?
- May files be deleted, overwritten, published, or written outside the repository?
- May an Obsidian vault be changed?

Usually non-blocking:

- names and file placement inferable from repository conventions
- test location and formatting inferable from adjacent code
- small implementation details that do not change behavior or authority

## Ask well

Ask one compact question that exposes the decision and its consequence. Offer a
recommended default when safe. Do not turn routine implementation into an interview.

If a blocking answer is unavailable, stop before the risky action and provide the
safe design, patch boundary, or validation plan. If a non-blocking answer is
unavailable, record `Assumption: ...` and proceed.

## Mid-flight reclassification

Reclassify an assumption as blocking when new evidence reveals a public break,
migration, dependency, destructive operation, security concern, external write, or
material scope increase.
