# Week 12 CI/CD evidence snapshot

**Group A · tomlkit · COMP 441 AI-Augmented Test Suite**

This is the CI/CD evidence snapshot for the final submission. It is not a
duplicate of the Week 11 mutation report: the authoritative mutation analysis
is `week11/mutation_v2/mutation_v2_report.md` (PR #4). This file records the
pipeline, the green run and the downloadable evidence.

## Green run

| Field | Value |
|---|---|
| Workflow | `COMP 441 CI` |
| Run | [40412867639](https://github.com/the-dezeray/tomlkit/actions/runs/40412867639) |
| Commit | `30ad2f0f8b05` (`master`, after PRs #4 and #5) |
| Result | **success** |
| Jobs | 15 successful; mutation and performance correctly skipped on a PR run |
| Pipeline PR | [#5](https://github.com/the-dezeray/tomlkit/pull/5) |
| Mutation v2 PR | [#4](https://github.com/the-dezeray/tomlkit/pull/4) |

## Headline metrics

| Metric | Value | Source |
|---|---:|---|
| Tests collected | 1,507 | `junit.xml` |
| Passed / xfailed | 1,502 / 5 | `junit.xml` |
| Statement coverage | 91.62% | `coverage.json` |
| Branch coverage | 85.62% | `coverage.json` |
| Combined coverage | 89.88% (local canonical run) | `coverage.json` |
| Mutation score v2 | 77.4% | `week11/mutation_v2/mutation_v2_summary.json` |
| Covered-code mutation score | 81.3% | same |
| Mutation v1 baseline | 57.8% | `week7/mutation_v1_summary.json` |
| RTM references | 16 requirements, 35 references, 15 with tests | `rtm_validation.json` |
| Week 7 priority APFD | 0.7722 | `week7/prioritisation_eval.json` |
| Defect density | 1.92 / KLOC | `reports/defects.csv` + radon |

The combined coverage in the downloaded CI dashboard is 91.62% statement /
85.62% branch (platform-dependent rounding and Python version can move the
last decimal); the local canonical run reported 89.88% combined. The gate is
evaluated against explicit statement and branch thresholds, not the rounded
display value.

## Downloadable artifacts

From the green run:

```bash
gh run download 40412867639 -n dashboard
gh run download 40412867639 -n hybrid-evidence
gh run download 40412867639 -n ai-baseline-evidence
gh run download 40412867639 -n rtm-evidence
gh run download 40412867639 -n quality-evidence
gh run download 40412867639 -n security-evidence
gh run download 40412867639 -n junit-unit-ubuntu-latest-3.12
```

Mutation evidence is produced by the nightly/manual mutation job:

```bash
gh workflow run ci.yml --ref master -f run_mutation=full
gh run download <mutation-run-id> -n mutation-evidence
```

## What the pipeline proves

- The **hybrid suite**, not only `tests/`, is the merge gate.
- The **Week 7 risk order** is executable in CI (`priority_order.json`).
- Coverage, RTM references and test failures are blocking.
- Mutation, performance, security and upstream compatibility are evidence
  jobs, kept off the fast PR path.
- Every report number is downloadable; the dashboard is also written to the
  run summary.
- The release workflow builds, checks and attaches a distribution artifact and
  cannot publish to PyPI from the student fork.

See `docs/ci-cd.md` for the job map, quality gates and mapping to the COMP 441
brief, and `docs/ci-cd-demo.md` for the 10-minute live demonstration.
