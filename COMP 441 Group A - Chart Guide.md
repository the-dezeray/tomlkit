# COMP 441 Group A — Chart guide

How to explain the seven charts in **`COMP 441 Group A - Presentation Charts.xlsx`**.

The workbook has one chart per sheet. Chart titles are deliberately off, so they do not duplicate the slide headlines. Axis titles are on. The `Data` sheet is hidden; unhide it if you need to edit a number.

**To use a chart:** open its sheet → click the chart border → `Ctrl+C` → in PowerPoint paste as **Picture** (or **Keep Source Formatting**).

---

## Quick map

| Chart sheet | Slide | One-line takeaway |
|---|---|---|
| `1 Coverage` | 4 | The AI suite covered the common paths; the maintainers covered the hard branches. |
| `2 Mutation v1` | 7 | 57.8% of planted bugs were caught; the complex modules are where the AI suite fell short. |
| `3 Mutation v1 v2` | 14 / 16 | Every module improved; `container` gained the most, `exceptions` is still weak. |
| `4 Overall` | 14 / 16 | The final suite moved the library-wide score from 57.8% to 77.4%. |
| `5 Detection curve` | 10 | Risk ordering finds the same mutants with far fewer tests. |
| `6 Detection speed` | 10 | Half the sampled mutants: 16 tests with risk order vs 51 in default order. |
| `7 Defects` | 11 | AI found half the defects; the other half needed other techniques. |

---

## 1. Coverage — AI-only vs maintainers vs final hybrid

**Axis titles:** x = Coverage type, y = % covered.

**Say:**
> The AI-only suite reached 81.7% statement and 66.3% branch coverage. The maintainers' existing suite reached 89.5% and 83.1%. The final hybrid suite reaches 91.6% and 85.6%. The interesting gap is branch coverage: the AI wrote lots of example tests but missed the unusual paths.

**Key numbers:** Statement `81.7 → 89.5 → 91.6`; branch `66.3 → 83.1 → 85.6`. The weakest AI branch area was `container.py` at 58.2% versus 83.6% for the maintainers.

**If asked:** Coverage is necessary but not sufficient. The next chart shows what coverage hid.

---

## 2. Mutation v1 — AI-only suite by module

**Axis titles:** x = Module, y = % mutants killed.

**Say:**
> We planted 5,389 small bugs with mutmut. The AI-only suite killed 3,087, timed out on 26, and missed 1,890; 386 were in code it never reached. That is 57.8% overall, or 62.2% of the code it did reach. The blue bars clear our 70% target; the orange bars do not. The three large modules — `container`, `items`, `parser` — hold 86% of all mutants and all three were below target.

**Key numbers:** `_utils` 95.0, `api` 83.9, `source` 82.7, `toml_file` 72.6, `parser` 64.0, `items` 54.1, `container` 47.2, `exceptions` 33.3.

**If asked:** A surviving mutant is a change the tests did not notice. Some are equivalent, but most are real gaps. Our 11 targeted manual tests each killed a named survivor.

---

## 3. Mutation v1 vs v2 — module-level improvement

**Axis titles:** x = Module, y = % mutants killed. Pale = AI-only v1, blue = final hybrid v2, orange = still below target.

**Say:**
> The final suite lifts every module. `container` gained 28.5 points, `items` and `parser` 19.4 each. The remaining weak spot is `exceptions` at 43.7%, where survivors are mostly exact-message checks.

**Key numbers:** `container 47.2 → 75.7`, `items 54.1 → 73.5`, `parser 64.0 → 83.4`, `exceptions 33.3 → 43.7`. Overall `57.8 → 77.4` (+19.6 points); covered-code score `62.2 → 81.3`.

**If asked — important caveat:** v2 measures the **shipped suite** (project tests plus our 53 group tests), not only our tests, and v1 ran on an earlier commit. The gain is real but it is not purely our contribution. Say this before anyone else does.

---

## 4. Overall mutation — 57.8% to 77.4%

**Axis titles:** x = Suite, y = % mutants killed.

**Say:**
> This is the headline: 57.8% for the AI-only suite, 77.4% for the final hybrid suite. The final run killed 4,136 mutants, with 34 timeouts, 956 survivors and 263 never reached. Covered-code score is 81.3%.

**If asked:** Formula is `(killed + timeout) / total`. Timeouts count as detected, following the Week 7 convention. Do not hide the 263 no-test mutants; they are the reason the covered-code score is higher.

---

## 5. Detection curve — risk-based vs default order

**Axis titles:** x = Tests run, y = % mutants detected. Blue = risk-based, orange = default order.

**Say:**
> We ranked the AI tests by complexity-weighted, two-year churn risk. The risk order detects 43% of the sampled mutants in 10 tests; the default order needs about 35 tests for the same. At 50 tests it is 72.1% versus 49.2%. APFD is 0.772 versus 0.637; the random mean is 0.691.

**Key numbers:** 258 sampled mutants; half detected in 16 tests (risk) vs 51 (default). Mutation outcomes were excluded from the ranking, so the comparison is out-of-sample.

**If asked:** This is a test-ordering result, not a claim that the suite is better. The same tests run; only the order changes.

---

## 6. Detection speed — tests to reach half the mutants

**Axis titles:** x = Order, y = Tests to detect 50%.

**Say:**
> This is the same result reduced to one number: 16 tests instead of 51. In CI, that means a regression is exposed roughly three times sooner, without removing a single test.

**If asked:** This is why the CI hybrid job runs with the Week 7 priority plugin, and why `priority_order.json` is uploaded with the run.

---

## 7. Defects — where the 8 confirmed defects came from

**Axis titles:** x = Discovery source, y = Defects found.

**Say:**
> We confirmed eight defects. The AI baseline found four: D1, D2, D3 and D5. Manual mutation follow-up found D6, Hypothesis found D7, the exploratory session found D8, and the Week 10 mutation run found M1. Three are fixed test-first: D1, D6, D7. Five remain open and are pinned by strict xfails or listed in the RTM. That is the balanced story: AI found half, but not the other half.

**Key numbers:** AI baseline 4; manual mutation follow-up 1; property-based 1; exploratory 1; mutation 1. Defect density 1.92 per KLOC (8 / 4.158).

**If asked:** D4 is **not** in our evidence; do not present nine defects. The confirmed count is eight.

---

## The 60-second story

1. The AI wrote 388 tests quickly and reached 81.7% statement coverage.
2. Mutation testing showed 1,890 survivors: the suite was broad but shallow.
3. Manual, property, BDD, integration and TDD tests closed the gaps: 57.8% → 77.4%.
4. Risk ordering finds half the mutants in 16 tests instead of 51.
5. The pipeline publishes coverage, JUnit, mutation, RTM and dashboard evidence on every run.
6. AI is a fast first draft, not ground truth.

---

## Claims to avoid

- **“v2 is only our tests.”** It is the shipped suite, including the project's existing tests.
- **“Nine defects.”** Eight are confirmed. D4 has no evidence in the repo.
- **“Mutation blocks every PR.”** Mutation is nightly evidence; coverage and RTM block the PR.
- **“The AI suite caught 57.8% of all bugs.”** It killed 57.8% of planted mutants; 386 were never reached.
- **“The AI found the important bugs.”** It found four of eight; the other four needed other techniques.

---

## Sources

- `week6/cov_ai.json`, `week6/cov_existing.json` — coverage
- `week7/mutation_v1_summary.json`, `week7/mutmut_results_v1.txt` — v1 mutation
- `week7/prioritisation_eval.json`, `week7/priority_order.csv` — ordering and APFD
- `week11/mutation_v2/mutation_v2_summary.json` — v2 mutation
- `reports/defects.csv` — eight confirmed defects
- `reports/week12/ci-evidence.md` — final CI run and dashboard
