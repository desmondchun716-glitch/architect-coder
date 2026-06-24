# Optimization Playbook

## Evidence loop

1. Define one primary target metric and relevant guardrails.
2. Record baseline command, environment, dataset, warm-up, and run count.
3. Locate the bottleneck with profiler, query plan, trace, bundle analysis, or
   controlled experiment.
4. Predict why a focused change should affect the metric.
5. Change one major variable at a time.
6. Compare before and after under equivalent conditions.
7. Run behavior and compatibility regression checks.
8. Keep a benchmark or test that detects meaningful regression.

Report variance and sample size. Treat noisy results as inconclusive. If the
benchmark cannot run, label performance `unverified` and provide a command the user
can run.

Never substitute lower code complexity for measured runtime improvement, or vice
versa; state which dimension improved.
