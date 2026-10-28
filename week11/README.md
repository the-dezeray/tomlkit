# Week 11 — Track D milestone

**Group A · tomlkit · branch `week11-track-d`**

Week 11 for **Track D (Developer Tooling / API Library)** has two mandatory
deliverables. Track D's specialised stream — property-based testing with
Hypothesis — was delivered in Weeks 6–7 and is summarised here for the final
report. No Track E work is included: Track E is a different scenario track for
AI/LLM-integrated applications.

## Deliverables

| # | Deliverable | File | Status |
|---|---|---|---|
| 1 | Mutation Testing Report v2 (final hybrid suite) | `week11/mutation_v2/mutation_v2_report.md` | Complete |
| 2 | Completed TDD log (3 test-first features) | `week11/TDD_LOG.md` | Complete |
| — | Track D property-based testing summary | `week11/property/PROPERTY_CHECKPOINT.md` | Complete (supporting) |

## Headline result

| Metric | Week 7 v1 (AI-only) | Week 11 v2 (final hybrid) |
|---|---|---|
| Mutants | 5,389 | 5,389 |
| Mutation score | 57.8% | **77.4%** (+19.6 pp) |
| Covered-code score | 62.2% | 81.3% |
| Tests in suite | 388 (AI-only) | 1,507 collected (1,502 passed, 5 xfailed) |

The full suite is green on the frozen commit:

```
1502 passed, 5 xfailed
```

## What changed since Week 7

- The TDD cycles C1–C3 fixed D1 (`date()` accepted datetime strings), D7
  (multiline strings emitted a bare CR) and D6 (`comment()` emitted a bare CR).
- The final suite adds manual survivor-killing tests, BDD acceptance scenarios,
  integration tests, property-based tests and TDD regression tests.
- The mutation run includes the whole project suite, so the v2 score measures
  the suite that actually ships, not just the AI-only baseline.

## Files

```
week11/
  README.md
  TDD_LOG.md
  full_suite.txt
  tdd_runs/                 # raw red/green/refactor pytest output
  Week11_TrackD_Findings.xlsx   # chart dashboard
  mutation_v2/
    README.md
    mutation_v2_report.md
    survivor_rootcause_v2.md
    mutmut_results_v2.txt
    mutation_v2_summary.json
    v1_vs_v2.csv
    survivors_v2.txt
    scripts/summarise_v2.py
    scripts/build_excel.py
  property/
    PROPERTY_CHECKPOINT.md
    pytest_property.txt
```

## Reproduce

```bash
python -m pytest -q tests tests_ai tests_manual tests_bdd \
  tests_integration tests_property tests_tdd
```

Mutation reproduction is documented in `week11/mutation_v2/README.md`.
