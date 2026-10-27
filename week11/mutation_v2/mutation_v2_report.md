# Mutation Testing Report v2 — final hybrid suite

**Group A · Track D (Developer Tooling / API Library) · tomlkit**

- Repository: `the-dezeray/tomlkit` (fork of `python-poetry/tomlkit`)
- Commit under test: `6b8884f`
- Date: 27 October 2026 (Week 11 milestone: 03 November 2026)
- Runner: mutmut 3.8.0, Ubuntu (WSL2), Python 3.13.14, pytest 9.1.1
- Final suite: `tests/`, `tests_ai/`, `tests_manual/`, `tests_bdd/`,
  `tests_integration/`, `tests_property/`, `tests_tdd/`

---

## Executive summary

The final hybrid suite scores **77.4%** on the Week 11 mutation run
(4,136 killed + 34 timeout out of 5,389 mutants), compared with **57.8%** for
the Week 7 AI-only baseline. The covered-code score is **81.3%**. This is a
**+19.6 percentage-point** improvement on the same 5,389-mutant scope.

The improvement is large but must be read carefully: the v2 run measures the
**shipped suite** (1,507 collected tests), while v1 measured the **AI-only
suite** (388 tests). The increase therefore combines three effects: the manual/BDD/
integration/property/TDD tests added after Week 7, the pre-existing project
tests, and the three TDD fixes (D1, D6, D7) that changed the code under test.
The report separates these where the evidence allows and records the
limitation explicitly in §4.

The most important residual finding is that **exception and formatting
branches remain the weak spot**: `exceptions` scores only 43.7%, and 218 of the
931 survivors shared with v1 are exception-message or exception-construction
mutations. The remaining survivors are concentrated in `items` (331),
`container` (251) and `parser` (230); the highest-value next tests are listed
in §3.

---

## 1. Scope and method

### 1.1 Source scope

Mutated: `tomlkit/` (10 source files, 5,389 mutants).

Excluded:

- `tomlkit/_compat.py` — platform compatibility shim; mutation would test
  import mechanics rather than library behaviour.
- `tomlkit/_types.py` — covered by the separate Week 10 `_types.py` exercise
  (mutmut 2.5.1, 10 mutants). Excluding it here keeps the v2 scope identical to
  the Week 7 v1 scope.

This makes the overall score directly comparable in scope, though not in code
version or suite composition.

### 1.2 Suite composition

| Suite | Tests | Role |
|---|---:|---|
| `tests/` | 1,065 | Pre-existing project tests plus the Week 10 `_types`/property additions |
| `tests_ai/` | 388 | Week 6 AI-generated baseline (3 strict xfails) |
| `tests_manual/` | 19 | Week 7/9 manual survivor-killing tests |
| `tests_bdd/` | 3 | Gherkin acceptance scenarios (pytest-bdd) |
| `tests_integration/` | 5 | Week 9 integration tests |
| `tests_property/` | 10 | Track D Hypothesis properties |
| `tests_tdd/` | 17 | TDD regression tests for C1–C3 |
| **Total** | **1,507 collected** | 1,502 passed, 5 strict xfailed |

One test is deselected from the mutation run only:
`tests/test_api.py::test_parse_rejects_deeply_nested_documents`. mutmut's
trampoline adds stack frames to the deliberately deep nesting and triggers
`RecursionError` before the mutant is evaluated. The test remains in the normal
suite and passes there. This is a tooling limitation, not a test failure.

### 1.3 Metrics

- Mutation score: `(killed + timeout) / total × 100`
- Covered-code score: `(killed + timeout) / (total − no_tests) × 100`
- Timeouts are counted as detected, following the Week 7 convention.
- `no_tests` means the mutated line was never executed.

### 1.4 Reproducibility

The exact commands, environment and `[tool.mutmut]` configuration are in
`week11/mutation_v2/README.md`. The raw per-mutant status is in
`mutmut_results_v2.txt`; the summary is in `mutation_v2_summary.json`.

---

## 2. Results

### 2.1 Overall

| Metric | v1 (Week 7, AI-only) | v2 (Week 11, final hybrid) |
|---|---:|---:|
| Total mutants | 5,389 | 5,389 |
| Killed | 3,087 | 4,136 |
| Timeout | 26 | 34 |
| Survived | 1,890 | 956 |
| No tests | 386 | 263 |
| **Mutation score** | **57.8%** | **77.4%** |
| Covered-code score | 62.2% | 81.3% |

### 2.2 Per module

| Module | v1 score | v2 score | Δ (pp) | v2 killed | v2 survived | v2 no tests |
|---|---:|---:|---:|---:|---:|---:|
| `_utils` | 95.0 | 95.9 | +0.9 | 204 | 9 | 0 |
| `api` | 83.9 | 88.6 | +4.7 | 132 | 17 | 0 |
| `container` | 47.2 | 75.7 | +28.5 | 951 | 251 | 55 |
| `exceptions` | 33.3 | 43.7 | +10.4 | 76 | 88 | 10 |
| `items` | 54.1 | 73.5 | +19.4 | 1,471 | 331 | 198 |
| `parser` | 64.0 | 83.4 | +19.4 | 1,135 | 230 | 0 |
| `source` | 82.7 | 87.4 | +4.7 | 108 | 16 | 0 |
| `toml_file` | 72.6 | 80.8 | +8.2 | 59 | 14 | 0 |
| **TOTAL** | **57.8** | **77.4** | **+19.6** | **4,136** | **956** | **263** |

### 2.3 Interpretation

- The largest absolute gains are in `container` (+28.5 pp), `items` (+19.4 pp)
  and `parser` (+19.4 pp), where the final suite exercises branches that the
  AI-only suite never reached.
- `no_tests` fell from 386 to 263. The remaining 263 are concentrated in
  `items` (198, mostly formatting/rendering branches) and `container` (55).
- `exceptions` remains the weakest module at 43.7%, despite improving by
  10.4 pp. Its survivors are dominated by exact exception-message and
  exception-construction mutations (218 of the 931 shared survivors).

### 2.4 Group-authored contribution

The group authored 442 of the 1,507 collected tests: 388 AI-generated tests,
19 manual survivor-killing tests, 3 BDD scenarios, 5 integration tests,
10 property tests and 17 TDD tests. That is 54 more group-authored tests than
the 388-test AI-only baseline.

The v2 score is for the **shipped suite**, which also includes 1,065 tests in
`tests/`. The +19.6 pp therefore cannot be attributed to the group's 54 extra
tests alone. The group-specific contribution is visible in the targeted work:

- the manual K1–K11 tests target exact v1 survivors (messages, boundaries,
  stepped slices, AoT ordering, CRLF normalisation);
- TDD C1–C3 fixed D1, D6 and D7, which also removes the mutants on those lines;
- Hypothesis properties P3/P5 found D1 and D7 before the TDD fixes;
- BDD and integration tests exercise file-level round-trips and acceptance
  behaviour rather than single functions.

A same-commit AI-only rerun was not performed, so the exact group-only delta is
left as a limitation rather than estimated.

## 3. Survivor analysis

### 3.1 Overview

The v2 run leaves **956** survivors. Of these, **931** were already surviving
in v1; **25** are new (mostly because the code changed around them). The most
common categories are:

| Category | Survivors | Share of 956 |
|---|---:|---:|
| Argument dropped or set to `None` | 334 | 34.9% |
| Exception message or construction | 218 | 22.8% |
| String literal changed (`XX..XX` / case) | 93 | 9.7% |
| Boolean logic (`and`/`or`, `True`/`False`, `not`) | 89 | 9.3% |
| Boundary / off-by-one (`<` vs `<=`, `+1`, index) | 67 | 7.0% |
| Arithmetic / assignment operator | 65 | 6.8% |
| Control flow (`continue`/`break`/`return`) | 38 | 4.0% |
| Other | 27 | 2.8% |
| New since v1 (not in the v1 category file) | 25 | 2.6% |

### 3.2 Root causes

The ten highest-value survivors are analysed below. Each row names the mutant,
the mutation, why the final suite misses it, and the test that would close the
gap. The full candidate list is in `survivor_candidates.csv`.

| # | Mutant | Mutation | Why the final suite misses it | Category | Proposed test | Priority |
|---|---|---|---|---|---|---|
| 1 | `Parser._parse_table` `mutmut_10` | `parse_error(UnexpectedEofError)` → `parse_error(None)` | Tests assert `ParseError` but not the specific error class/cause, so dropping the error type is invisible | Exception construction | `parse("[table")` at EOF; assert `UnexpectedEofError` (or its message/cause) | High |
| 2 | `AoT.insert` `mutmut_10` | `index < 0` → `index <= 0` | No test inserts at index 0 into an AoT; only append and negative positions are covered | Boundary | Insert a table at index 0; assert order, length and round-trip | High |
| 3 | `Container.append` `mutmut_109` | `_validate_out_of_order_table(key)` → `(None)` | Out-of-order validation is tested indirectly; no test expects the conflict error when appending | Argument dropped | Append a table whose key conflicts with a later out-of-order table; assert `KeyAlreadyPresent`/`TOMLKitError` | High |
| 4 | `InlineTable.as_string` `mutmut_102` | `needs_separator = False` → `None` | `None` is falsy, so the mutant is behaviourally equivalent; no test can distinguish it | Likely equivalent | Mark equivalent after dataflow triage; no test proposed | Low |
| 5 | `Container._validate_table_candidate` `mutmut_10` | `"Redefinition of an existing table"` → lowercase | Test checks the exception type only, not the exact message | String literal | Assert the exact message for a dotted-table redefinition | Medium |
| 6 | `Array.__delitem__` `mutmut_101` | `replace(",", "", 1)` → `replace(",", "", )` | Tests delete single commas; no test uses an indent containing two commas, so removing all commas is not observed | Boundary | Delete from an array whose trivia contains two commas; assert only the first is removed and output reparses | High |
| 7 | `Container._replace_at` `mutmut_10` | `k.is_dotted() and (...)` → `or (...)` | No test replaces a non-dotted key with a `Table`/`AoT`, where the `and`/`or` difference matters | Boolean logic | Replace a non-dotted key with a table/AoT; assert header and round-trip | High |
| 8 | `Array.add_line` `mutmut_11` | `"Comment cannot contain line breaks"` → `"XX...XX"` | Test asserts `ValueError` only, not the exact message | String literal | Assert the exact message for `add_line(comment="a\nb")` | Medium |
| 9 | `Parser._parse_string` `mutmut_103` | `close = ""` → `None` | `close` is reassigned on the multiline path, so the mutated value appears unreachable in the tested paths | Likely equivalent | Confirm dataflow; no test if unreachable | Low |
| 10 | `Container._render_table` `mutmut_26` | `open_, close = "[[", "]]"` → `None` | No test renders an AoT element through `as_string()` and asserts the exact `[[...]]` header | Argument dropped | Render a document containing an AoT; assert exact header and reparse | High |

Eight of the ten are test gaps; two (`InlineTable.as_string` and
`Parser._parse_string`) look behaviourally equivalent and should not be chased
without a dataflow check. The detailed notes, including two further
exception-message survivors, are in `survivor_rootcause_v2.md`.

### 3.3 Equivalent and untested mutants

No full equivalence triage was performed. In the ten-case sample, two mutants
(`InlineTable.as_string` and `Parser._parse_string`) appear behaviourally
equivalent; the other eight are genuine test gaps. If that 20% rate held across
all 956 survivors, roughly 190 would be equivalent and the adjusted score would
be about 80%, but this is illustrative only and is not claimed as a measured
figure.

The 263 `no_tests` mutants are a separate category: they are not undetected
behaviour changes, but lines the suite never executes. They are concentrated in
`items` (198) and `container` (55), mostly formatting/rendering branches. The
34 timeouts are counted as detected under the Week 7 convention; they are
mostly slow parser loops rather than silent survivors.

---

## 4. Threats to validity

1. **Code changed since v1.** v1 ran at `8c959b5`; v2 runs at `6b8884f` after
   TDD C1–C3 fixed D1, D6 and D7. The score delta is therefore not a pure
   test-suite effect. A same-commit AI-only rerun was not performed; the v1
   figure is historical context.
2. **Suite composition changed.** v2 includes 1,065 project tests in `tests/`
   plus 442 group-authored tests; v1 included only 388 AI tests. The v2 score
   measures the shipped suite, not the group's marginal contribution. The
   manual/BDD/TDD tests were written specifically against v1 survivors, so
   their contribution is real but not separately quantified here.
3. **One test deselected.** The deep-nesting recursion test cannot run under
   mutmut's trampoline. It is green in the normal suite; its exclusion could
   hide at most the mutants it would have killed.
4. **Timeouts.** Timeouts are counted as detected. The report lists the count
   but does not distinguish a genuine hang from a very slow mutant.
5. **Equivalent mutants.** Some survivors are behaviourally equivalent and
   cannot be killed. No full equivalence triage was performed; §3.3 gives a
   conservative reading.
6. **Single project, single runner.** Results are specific to tomlkit and
   mutmut 3.8.0; they should not be generalised to other codebases.
7. **Sampling in survivor analysis.** The ten root causes are selected from the
   highest-risk functions, not a random sample; they illustrate failure modes
   rather than estimate the survivor population.

---

## 5. Recommendations

1. Add targeted tests for the ten survivors in §3.2; the proposed techniques are
   boundary value analysis, equivalence partitioning and exact-message checks.
2. Prioritise `container` and `items`, which hold most residual survivors.
3. Keep the final suite in CI with a mutation-score floor; a floor just below
   the current score prevents regression without blocking unrelated work.
4. Re-run v2 with a same-commit AI-only baseline in the final report so the
   group-authored contribution can be isolated cleanly.

---

## Appendix A — Files

| File | Purpose |
|---|---|
| `mutmut_results_v2.txt` | Raw status for every mutant |
| `mutation_v2_summary.json` | Overall and per-module counts/scores |
| `v1_vs_v2.csv` | v1 vs v2 by module |
| `v1_vs_v2.png` | Score comparison chart |
| `survivors_v2.txt` | Surviving mutant names |
| `survivors_v1_v2.csv` | Survivors joined to Week 7 categories |
| `survivor_candidates.csv` | Survivors grouped by function |
| `survivor_rootcause_v2.md` | Detailed root-cause notes |
| `../Week11_TrackD_Findings.xlsx` | Excel dashboard with native charts |
| `scripts/` | Summary, comparison, chart and workbook scripts |
