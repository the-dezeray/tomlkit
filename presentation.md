# Presentation notes — COMP 441 Group A

Simple speaking notes for **AI-Augmented Testing of TOML Kit**.

Use the slide headline as your main point, then support it with one or two numbers. Do not read the slide word for word.

---

## Slide 1 — Title

**On the slide:** The project title, the team, COMP 441 Group A / Track D, and the repo card for `python-poetry/tomlkit`.

**How to explain it:**

- Introduce the project in one sentence: we used AI to help test a real Python library.
- Explain that TOML Kit reads and edits TOML config files without destroying comments or formatting.
- Say that the question for the project was: can AI write a useful test suite for a real library?

---

## Slide 2 — The project

**On the slide:** What TOML Kit does, the project size, and the Track D focus.

**How to explain it:**

- TOML Kit is a style-preserving TOML library: it keeps comments and whitespace when a file is edited.
- The codebase is about 4,158 lines of Python, with 1,058 tests already written by the maintainers.
- Track D is the developer-library track; our specialist stream is property-based testing with Hypothesis.
- We worked on a fork of the public repo at a fixed base commit.

---

## Slide 3 — Our approach

**On the slide:** The five-stage timeline from Week 6 to Week 12.

**How to explain it:**

- Week 6: the AI generated the first test suite — 388 tests from seven logged prompts.
- We then measured it with coverage, an assertion audit and static analysis.
- Week 7: mutation testing planted 5,389 small bugs to see how many the tests would catch.
- Weeks 7–9: we closed the gaps with manual, property-based, TDD, BDD and integration tests.
- Weeks 10–12: we put coverage and traceability gates into CI. Mutation testing runs nightly.
- Close with the important point: every claim comes from a script we can re-run, not from the AI describing its own tests.

---

## Slide 4 — Week 6 AI baseline

**On the slide:** AI-only coverage compared with the maintainers' coverage.

**How to explain it:**

- The AI suite reached 81.7% statement coverage, but only 66.3% branch coverage.
- The maintainers' tests reached 89.5% statements and 83.1% branches.
- The biggest gap was `container.py` branches: 58.2% for the AI suite versus 83.6% for the maintainers.
- `Container.append` is the worst spot: complexity 74, and 32 of its lines were never executed by the AI tests.
- The point: the AI covered the easy paths, not the complex code that protects formatting.

---

## Slide 5 — Assertion quality

**On the slide:** A breakdown of 305 AI-written test functions by assertion strength.

**How to explain it:**

- 69% of the tests had strong assertions: exact values, exact output or the exact exception.
- 15% were partial, and 16% were weak.
- Give the example: `assert boolean("yes") is False` locks in current behaviour, even if that behaviour is questionable.
- The point: AI tests often describe what the code currently does, not what it should do.

---

## Slide 6 — Static analysis and requirements

**On the slide:** Complexity results, linter findings, CrossHair, and the requirements traceability matrix.

**How to explain it:**

- Average complexity is 3.0, but 13 functions rank D to F. `Container.append` at 74 is the worst.
- Pylint reported 11 style findings in `api.py`. The substantive defects came from tests, CrossHair and exploratory testing.
- CrossHair broke the rule that `date()` never returns a datetime in under 60 seconds, using `0001-10-30 00:00`.
- Of 16 requirements, 8 were covered after the AI baseline, 4 partly covered, 3 failing and 1 untested.

---

## Slide 7 — Week 7 mutation testing v1

**On the slide:** The AI-only mutation score and per-module results.

**How to explain it:**

- We planted 5,389 mutants with mutmut. The AI-only suite killed 57.8%, against a 70% target.
- 1,890 mutants survived; 386 were in code the AI suite never reached.
- The three largest modules hold 86% of all mutants, and all three were below target.
- The weak modules are `parser`, `items`, `container` and `exceptions`.

---

## Slide 8 — Module-level mutation results

**On the slide:** A chart comparing v1 (AI-only) and v2 (hybrid suite) for each module.

**How to explain it:**

- Every module improved when we moved from the AI-only suite to the hybrid suite.
- The biggest gains were in the large modules: `container` went from 47.2% to 75.7%, `items` from 54.1% to 73.5%, and `parser` from 64.0% to 83.4%.
- `exceptions` is still the weakest module at 43.7%.
- If asked: v2 measures the shipped suite, including the maintainers' existing tests, not only our tests.

---

## Slide 9 — Detection curve

**On the slide:** A line chart comparing risk-based ordering with pytest's default order.

**How to explain it:**

- The same tests are run; only the order changes.
- Risk-based ordering finds mutants much earlier than the default order.
- At 50 tests, risk ordering has detected about 72% of the sampled mutants, compared with about 49% for the default order.
- This is why CI runs the hybrid suite in risk order.

---

## Slide 10 — Overall mutation result

**On the slide:** A bar chart showing the library-wide mutation score.

**How to explain it:**

- The AI-only suite scored 57.8%.
- The final hybrid suite scored 77.4%.
- That is a gain of 19.6 percentage points, and it clears our 70% target.
- Keep the caveat ready: the v2 run measures the full shipped suite, so the gain is not purely our contribution.

---

## Slide 11 — Why mutants survived

**On the slide:** Four patterns in the AI-written tests and the fix for each.

**How to explain it:**

- Loose assertions: the only position test said `col >= 4`, so an off-by-one column survived. We now assert the exact line and column.
- One example per class: the AI tested `\n` but not `\r` in comments. We used equivalence partitioning.
- Missing boundaries: offsets like `+05:30` and `-08:00` hid a parser bug. `+10:00` exposes it.
- Untested combinations: `sort_keys` was tested on tables but not arrays of tables. We used a decision table.
- We then wrote 11 manual tests, one per root cause, and checked that each one fails on the mutant and passes on the real code.

---

## Slide 12 — Property-based testing

**On the slide:** The properties we tested, the shrunk counterexample, and the result.

**How to explain it:**

- Instead of writing examples, we wrote rules that must hold for every input.
- Hypothesis generates hundreds of inputs and tries to break those rules.
- It found a lone carriage return in multiline strings: TOML Kit writes the character, then cannot parse its own output.
- Hypothesis shrank the input to a single character.
- All 10 property tests pass on the final code.

---

## Slide 13 — Risk-based prioritisation

**On the slide:** A comparison of tests needed to detect half the sampled mutants.

**How to explain it:**

- Risk-based order needs 16 tests to detect half the sampled mutants; the default order needs 51.
- The risk score is complexity multiplied by recent churn. Each next test covers the highest remaining risk.
- APFD is 0.772 for risk order versus 0.637 for the default order.
- It beat all 200 random orders, and mutation data was excluded from the ranking, so the comparison is fair.

---

## Slide 14 — Defects

**On the slide:** A table of the eight confirmed defects, how each was found, and its status.

**How to explain it:**

- We confirmed eight defects in a library that already had 1,058 passing tests.
- Three are fixed test-first: D1, D6 and D7.
- Five remain open: D2, D3, D5, D8 and M1. Each open defect is pinned by a strict xfail test or recorded in the RTM.
- Defect density is 1.92 per KLOC (8 defects / 4.158 KLOC).
- Do not present nine defects. D4 is not in our evidence, so it is excluded.

---

## Slide 15 — TDD and BDD

**On the slide:** Three red–green–refactor cycles and one BDD acceptance scenario.

**How to explain it:**

- C1: `date()` now rejects datetime strings.
- C2: strings never emit a lone carriage return.
- C3: comments split on a lone carriage return.
- The refactors merged both CR fixes into one rule, and the full suite passed at C3 with 1,489 tests.
- The BDD scenario bumps the version and checks that the file on disk is otherwise unchanged.
- We also verified the scenario can fail: a save that drops comments makes it fail.

---

## Slide 16 — Beyond unit tests

**On the slide:** Integration, exploratory, performance and usability testing.

**How to explain it:**

- Five integration tests drive real files through the parser, container and serialiser.
- The exploratory session with an AI co-pilot isolated D8: inserting at index 0 causes spacing problems that compound.
- Performance: about 2,386 operations per second over 25,000 operations, with every round trip correct.
- Usability: error messages are a strength because they give line and column. The main issue is inconsistent spacing after insertion at index 0.

---

## Slide 17 — Final quality dashboard

**On the slide:** Final coverage, RTM completeness, defect density and suite size.

**How to explain it:**

- Statement coverage is 91.6%, against an 87% gate; the AI-only baseline was 81.7%.
- Branch coverage is 85.6%, against an 82% gate; the AI-only baseline was 66.3%.
- RTM completeness is 88%: 14 of 16 requirements, with R15 and R16 still open.
- Defect density is 1.92 per KLOC.
- 1,502 tests pass across seven suites, with five strict xfails pinning open defects.
- The library-wide v2 mutation score is 77.4%.

---

## Slide 18 — CI/CD pipeline

**On the slide:** The GitHub Actions pipeline and its blocking and non-blocking jobs.

**How to explain it:**

- On every push and pull request: quality checks with ruff and mypy, a 3 OS × 3 Python unit matrix, the 388 AI baseline tests, the 1,502-test hybrid suite in risk order, and the coverage/RTM gate.
- Nightly, non-blocking: mutation testing, performance testing with Locust, and security checks with pip-audit and bandit.
- Every run uploads coverage, JUnit, mutation, RTM and dashboard evidence.
- Merge is blocked if statement coverage is below 87%, branch coverage below 82%, any test fails, or an RTM reference is unresolved.

---

## Slide 19 — Quality gate and final results

**On the slide:** The gate conditions, the mutation improvement, and the defects fixed.

**How to explain it:**

- The blocking gates are coverage and RTM. Mutation is nightly evidence, not a merge blocker.
- The library-wide mutation score moved from 57.8% to 77.4%.
- Three of the eight defects are resolved: D1, D6 and D7.
- The live demonstration pushes a seeded regression and shows the coverage gate blocking it.

---

## Slide 20 — What we learned

**On the slide:** Three lessons and our working rule.

**How to explain it:**

- AI was genuinely useful for speed: 388 tests in minutes, 81.7% statement coverage and three confirmed defects on the first run.
- Coverage can mask weak tests. Mutation testing showed that 42% of planted mutants survived.
- Test design mattered more than test volume: eleven targeted tests closed eleven representative survivors, and Hypothesis found a defect in seconds.
- Our working practice: use AI for drafting, then use mutation scores, properties and test-design techniques to judge completeness.

---

## Slide 21 — Questions

**On the slide:** The repo link and the team roles.

**How to explain it:**

- Thank the audience.
- Point them to `github.com/the-dezeray/tomlkit` for the code and evidence.
- Offer to take questions on any part of the project.

---

# Quick Q&A prep

**“Did the AI write the whole suite?”**
No. It wrote the 388-test baseline. We then added manual, property-based, TDD, BDD and integration tests.

**“Is the 77.4% only your work?”**
No. The v2 run measures the full shipped suite, including the maintainers' existing tests. The honest comparison is 57.8% AI-only versus 77.4% hybrid.

**“Why are there still open defects?”**
They are recorded and pinned by strict xfail tests or listed in the RTM. We did not hide them.

**“Why does mutation not block the merge?”**
It takes too long for every pull request, so it runs nightly as evidence. Coverage and RTM block the merge.

**“How many defects did you find?”**
Eight confirmed defects. D4 is not in our evidence, so do not count it.
