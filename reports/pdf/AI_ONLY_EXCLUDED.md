# AI-only artifacts: what is excluded from the weekly PDFs

The COMP 441 brief requires an **AI-only baseline** (rubric: *AI-Generated Baseline Suite & Coverage*, 8 marks) and a **v1 mutation run** (rubric: *Mutation Testing v1 → v2*, 12 marks). Those artifacts are evidence, so they stay in the repository. They are **not printed page-for-page** in the weekly packs; each pack prints the human-readable report, the summary tables, and the small outputs that a marker needs, then lists the raw files in its inventory.

## AI-only artifacts kept as evidence

| Artifact | Why it is AI-only | Printed in the weekly PDF? |
|---|---|---|
| `tests_ai/` | The 388-test AI-generated baseline suite | No — it is test code, not a report; Week 6 prints the coverage and assertion summary |
| `tests_ai/PROMPT_LOG.md` | The seven prompts and repair loop | No — it belongs in the final report appendix; Week 6 links to it |
| `week6/cov_ai.json` | AI-only coverage data | Summary table only |
| `week6/assertion_audit.csv` | Per-test assertion audit of the AI suite | Summary table only |
| `week6/htmlcov_ai/` | AI-only HTML coverage report | No — generated, reproducible from `cov_ai.json` |
| `week7/mutmut_results_v1.txt` | Raw v1 mutant status (5,389 lines) | Summary and representative survivors only |
| `week7/survivor_categories_v1.csv` | v1 survivor classification | Category summary only |
| `week7/kill_matrix.json` | v1 300-mutant kill matrix | No — Week 7 prints the APFD summary |
| `week7/mutation-testing-report-v1.pdf` | Original v1 PDF report | No — it duplicates the Week 7 README and uses legacy font encoding |
| `week11/mutation_v2/mutmut_results_v2.txt` | Raw v2 mutant status (5,389 lines) | Summary and representative survivors only |
| `week11/mutation_v2/survivors_v2.txt` | v2 survivor names | No — Week 11 prints the root-cause analysis |
| `week11/mutation_v2/survivors_v1_v2.csv` | v1/v2 survivor comparison | No — the module table is printed |
| `week11/mutation_v2/survivor_candidates.csv` | Candidate survivors for triage | No |
| `week11/Week11_TrackD_Findings.xlsx` | Chart workbook | No — the PNG chart is embedded in Week 11 |
| `reports/final/build_report.py` | Final report generator | No — the final report is a separate deliverable |

## Root clutter removed or moved

| Item | Action |
|---|---|
| `~$MP 441 Group A - Final Report.docx` | Removed — Word lock file, not a deliverable |
| `final.txt` | Moved to `docs/brief/COMP441_Group_Project_Brief.txt` — the extracted project brief, not a submission artifact |
| `COMP 441 Group A - AI-Augmented Testing of TOML Kit (1) - ORIGINAL.pptx` | Moved to `docs/archive/COMP441_GroupA_Presentation_ORIGINAL.pptx` — duplicate original deck |
| `__pycache__/`, `.pytest_cache/` | Removed — generated caches |
| `~$*` | Added to `.gitignore` |

## Why not delete the AI-only evidence?

Deleting `tests_ai/`, `week6/cov_ai.json`, `week7/mutmut_results_v1.txt`, or the v1 summary would remove the evidence for two rubric rows and make the report's 57.8% → 77.4% comparison unverifiable. The safe approach is to keep the raw evidence, keep it out of the printed packs, and make the boundary explicit here.
