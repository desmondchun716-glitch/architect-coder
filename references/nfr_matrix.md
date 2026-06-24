# Non-functional Requirements

Inspect only relevant dimensions:

| Dimension | Typical evidence | Do not invent |
|---|---|---|
| Performance | P50/P95/P99, throughput, build time | exact targets |
| Scalability | workload shape, resource curve, queue depth | future traffic |
| Reliability | error rate, retries, recovery tests | availability claims |
| Security | threat boundaries, authz tests, secret scan | compliance status |
| Observability | logs, metrics, traces, request IDs | monitoring coverage |
| Maintainability | coupling, ownership, tests, complexity | numeric quality gains |
| Compatibility | API/schema/format regression tests | hidden consumer behavior |
| Cost | compute, storage, vendor and maintenance cost | precise spend |

For each relevant dimension record current evidence, desired outcome, validation
method, risk, and whether missing information blocks implementation.

Use `assets/templates/nfr_matrix.md` for architecture-impacting work.
