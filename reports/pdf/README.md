# Weekly evidence PDFs

One PDF per week/folder, plus a combined pack for the marker.

| PDF | Week | Contents | Source folder |
|---|---|---|---|
| [`week6.pdf`](week6.pdf) | Week 6 | AI Baseline, Coverage and Static Analysis | `week6` |
| [`week7.pdf`](week7.pdf) | Week 7 | Mutation Testing v1 and Risk-Based Prioritisation | `week7` |
| [`week8.pdf`](week8.pdf) | Week 8 | TDD Cycles and BDD Acceptance Scenarios | `week8` |
| [`week9.pdf`](week9.pdf) | Week 9 | Performance, Usability and Exploratory Testing | `docs/week9` |
| [`week10.pdf`](week10.pdf) | Week 10 | Metrics, Defect Density and RTM Completeness | `reports/week10` |
| [`week11.pdf`](week11.pdf) | Week 11 | Mutation v2, TDD and Property-Based Testing | `week11` |
| [`week12.pdf`](week12.pdf) | Week 12 | CI/CD Pipeline, Quality Gates and Final Evidence | `reports/week12` |
| [`COMP441_GroupA_Weekly_Evidence.pdf`](COMP441_GroupA_Weekly_Evidence.pdf) | All | Combined pack with bookmarks for every week | all folders |

## What is printed

Each pack prints the week's README/report, key summary tables, small raw outputs, and an inventory of the folder.
Large raw artefacts (full mutmut output, coverage JSON, HTML coverage, kill matrices) are listed in the inventory
and remain in the repository as evidence; they are not printed page-for-page.

Items tagged `[AI-only]` or `[v1 baseline]` are deliberately excluded from the printed pages. They are the AI
baseline's raw output, not the final hybrid result. They are still in the repository because the brief requires
the AI-only baseline and v1 mutation evidence.

See [`AI_ONLY_EXCLUDED.md`](AI_ONLY_EXCLUDED.md) for the full list and the reason each item is kept.

## Rebuild

```bash
python reports/build_week_pdfs.py
```
