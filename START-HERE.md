# COMP 441 Group A — start here

**Project:** AI-Augmented Test Suite for TOML Kit  
**Track:** D — Developer Tooling / API Library  
**Repository:** [github.com/the-dezeray/tomlkit](https://github.com/the-dezeray/tomlkit)

## Read the evidence

- **Weekly evidence PDFs:** [`reports/pdf/README.md`](reports/pdf/README.md)
- **Combined PDF (all weeks):** [`reports/pdf/COMP441_GroupA_Weekly_Evidence.pdf`](reports/pdf/COMP441_GroupA_Weekly_Evidence.pdf)
- **Final report:** [`COMP 441 Group A - Final Report.docx`](COMP%20441%20Group%20A%20-%20Final%20Report.docx)
- **Presentation notes:** [`presentation.md`](presentation.md)
- **Chart guide:** [`COMP 441 Group A - Chart Guide.md`](COMP%20441%20Group%20A%20-%20Chart%20Guide.md)

## Key evidence

| What | Where |
|---|---|
| AI-only baseline (388 tests) | `tests_ai/`, `week6/` |
| Mutation v1 (57.8%) | `week7/` |
| Final hybrid suite (1,507 tests) | `tests/`, `tests_ai/`, `tests_manual/`, `tests_bdd/`, `tests_integration/`, `tests_property/`, `tests_tdd/` |
| Mutation v2 (77.4%) | `week11/mutation_v2/` |
| TDD and BDD | `week8/`, `week11/TDD_LOG.md`, `tests_bdd/features/` |
| Performance, usability, exploratory | `docs/week9/` |
| CI/CD and quality gates | `.github/workflows/ci.yml`, `docs/ci-cd.md`, `reports/week12/ci-evidence.md` |
| Defect log | `reports/defects.csv` |
| Requirements traceability | `week6/rtm/rtm_week6.csv`, `ci/validate_rtm.py` |

## Rebuild the PDFs

```bash
python reports/build_week_pdfs.py
```

AI-only raw logs are kept as evidence but are not printed page-for-page in the weekly packs. See [`reports/pdf/AI_ONLY_EXCLUDED.md`](reports/pdf/AI_ONLY_EXCLUDED.md).
