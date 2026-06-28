# Debugging Protocol

Use only for bugs, failing tests, regressions, crashes, unexpected behavior, or noisy logs that require root-cause isolation.

## Evidence loop

1. **Observed failure**: record expected versus actual behavior and the exact failing command.
2. **Reproduction**: reproduce safely; if not run, state reason, risk, and next verification.
3. **Minimal failing scope**: reduce to the smallest input, test, module, or call path that still fails.
4. **Hypothesis**: name a falsifiable cause, not a patch guess.
5. **Evidence**: inspect the full affected path and use focused instrumentation or tests to confirm or reject it.
6. **Fix**: make the smallest change that addresses the verified cause.
7. **Regression**: add or run a focused check that fails before and passes after, then run proportionate adjacent checks.
8. **Remaining uncertainty**: record untested paths, environmental gaps, or competing explanations.

Do not change production code before establishing reproduction or a documented not-run reason. Do not broaden scope merely because nearby cleanup is tempting.

## Log compaction

Preserve:

- exact failing command and environment detail needed to reproduce it
- first failing assertion or stack trace
- affected file and line
- minimal relevant surrounding output
- final focused check result

Compress repeated warnings, duplicate stack frames, unrelated passing logs, and large generated output. If root cause is uncertain, retain more raw output instead of compressing away evidence.

## Stop conditions

Stop and request direction when evidence points to an unauthorized migration, public break, dependency, destructive action, sensitive-data exposure, or materially wider rewrite. After two failed fix cycles, return to the hypothesis and evidence stages; do not keep stacking speculative patches.

## Completion evidence

Report the reproduction, root cause, changed files, regression check, broader checks, checks not run, and remaining uncertainty. A passing unrelated test is not proof of the fix.
