# 10-minute live CI/CD demonstration

**Audience:** COMP 441 assessors and Q&A panel  
**Goal:** prove that the pipeline runs, that it gates the hybrid suite, and that
the report evidence is downloadable rather than "a green tick".

## Before the session

Run this checklist 30–60 minutes before the demo.

```bash
# 1. Confirm the fork's workflows are enabled and a green run exists.
gh run list --workflow=ci.yml --limit 5

# 2. Produce a fresh run without needing a commit.
gh workflow run ci.yml --ref master \
  -f run_mutation=none \
  -f run_performance=false

# 3. Wait for it and note the run id.
gh run watch
gh run list --workflow=ci.yml --limit 1

# 4. Download the evidence once, so the demo does not depend on live downloads.
mkdir -p demo-artifacts
gh run download <run-id> -n dashboard -D demo-artifacts/dashboard
gh run download <run-id> -n hybrid-evidence -D demo-artifacts/hybrid
gh run download <run-id> -n rtm-evidence -D demo-artifacts/rtm
gh run download <run-id> -n mutation-evidence -D demo-artifacts/mutation

# 5. If the latest scheduled mutation run is older, note its run id for the demo.
gh run list --workflow=ci.yml --event=schedule --limit 3
```

Also prepare:

- One open PR from a branch in the main fork (not another user's fork) so
  checks run without first-time-contributor approval.
- A browser tab on the repository **Actions** page.
- A terminal in the repository root.
- A fallback screen recording of the green run and artifact download.
- Optional: a throwaway draft PR with one deliberately failing test for the
  red-gate segment. Close it immediately after the demo.

Do **not** run the full mutation job live: it takes 20–30 minutes. Show the
artifact from the latest scheduled or manually dispatched mutation run.

## Timeline

### 0:00–0:45 — What the pipeline is

Say:

> This is one pipeline, not a collection of scripts. It runs the hybrid suite,
> enforces coverage and traceability gates, and publishes every number used in
> the report as an artifact. The expensive mutation and upstream-compatibility
> jobs run nightly or on demand.

Show the job graph in `.github/workflows/ci.yml` or the Mermaid diagram in
`docs/ci-cd.md`.

### 0:45–2:00 — Actions tab and green run

```bash
gh run list --workflow=ci.yml --limit 5
gh run view <run-id>
```

Point out:

- `quality`, `unit`, `ai-baseline`, `hybrid`, `rtm`, `security`, `dashboard`.
- The unit matrix across Ubuntu/Windows/macOS and Python 3.9/3.12/3.14.
- The full mutation job is absent from this PR run by design; it is scheduled.

### 2:00–3:15 — Pull request checks

```bash
gh pr checks <pr-number>
```

Open the PR in the browser and show the checks list. Explain that
`hybrid` runs the Week 7 risk order and that coverage/RTM are required checks.
If the draft failing PR is available, show the red check and the blocking merge
button, then switch back to the green PR. This is the "gate" part of CI/CD, not
just a test runner.

### 3:15–4:30 — Artifacts: coverage HTML and JUnit

```bash
gh run download <run-id> -n hybrid-evidence -D demo-artifacts/hybrid
start demo-artifacts/hybrid/htmlcov/index.html   # macOS: open ...
```

Show:

- `coverage.xml` for tooling and `coverage.json` used by the gate script.
- `htmlcov/index.html` for line-by-line evidence.
- `junit.xml` for the machine-readable test result.
- `coverage_gate.json` with the statement and branch thresholds and `passed`.

Say:

> The report does not rely on a screenshot of a terminal. The HTML coverage
> report, JUnit XML and gate JSON are attached to the run and can be downloaded
> by any reviewer.

### 4:30–5:30 — Dashboard

```bash
gh run download <run-id> -n dashboard -D demo-artifacts/dashboard
type demo-artifacts\dashboard\dashboard.md   # macOS/Linux: cat ...
```

Show the run summary page too. Point out:

- Test counts and xfails.
- Statement/branch coverage and the weakest modules.
- RTM references and status counts.
- Week 10 baseline comparison.
- Mutation status (from the last mutation artifact).
- Defect density from `reports/defects.csv`.

### 5:30–6:30 — Week 7 priority order in action

```bash
gh run download <run-id> -n hybrid-evidence -D demo-artifacts/hybrid
python -m json.tool demo-artifacts/hybrid/priority_order.json
```

Point out `matched`, `collected`, `apfd_risk_based`, and the first 50 node ids.
Say:

> The Week 7 ranking was not just a report table. The same `priority_order.csv`
> now drives execution order in CI, so the highest-risk tests run first. Every
> test still runs; only the order changes. The unranked tests keep a stable
> order.

Optional comparison:

```bash
poetry run python -m pytest -q --no-priority-order
```

### 6:30–7:30 — RTM validation

```bash
gh run download <run-id> -n rtm-evidence -D demo-artifacts/rtm
type demo-artifacts\rtm\rtm\rtm_validation.md
```

Show:

- All 16 requirement IDs present.
- Every referenced test resolves to a collected node id.
- The status distribution and the two known incomplete requirements (R15 and
  R16).
- The collected test list used to validate the references.

Say:

> Renaming or deleting a test now fails CI instead of silently leaving the RTM
> stale.

### 7:30–8:30 — Mutation evidence

```bash
gh run list --workflow=ci.yml --event=schedule --limit 3
gh run download <mutation-run-id> -n mutation-evidence -D demo-artifacts/mutation
type demo-artifacts\mutation\mutation_summary.json
```

Show total, killed, survived, score and the survivor list. Explain:

- Mutation is nightly/dispatch because it takes 20–30 minutes.
- The Week 11 final run uses the full hybrid suite and mutmut 3.8.0.
- `ci/mutation_summary.py` turns raw `mutmut results` into the same JSON shape
  consumed by the dashboard.
- The authoritative Week 11 report is `week11/mutation_v2/mutation_v2_report.md`
  (PR #4): **77.4%** v2 versus **57.8%** v1 (+19.6 pp), covered-code score
  **81.3%**. Show `week11/mutation_v2/v1_vs_v2.png` or `v1_vs_v2.csv` for the
  module-level gains.

### 8:30–9:15 — Security and release/CD

Show the `security-evidence` artifact (`pip-audit.json`, `bandit.txt`) and the
`Release` workflow. Explain:

- Security is evidence-first today; high/critical findings are triaged before
  it becomes blocking.
- CD for a library is verified build + distribution artifact + GitHub release,
  not a server deployment.
- PyPI publishing is guarded to the upstream repository; the student fork does
  not attempt to publish.

### 9:15–10:00 — Close and Q&A

One-slide summary:

- One pipeline, tiered by cost.
- Hybrid suite + coverage + RTM are required.
- Mutation, performance, security and upstream compatibility are evidence
  jobs.
- Every report number is downloadable.
- Week 7 priority order is executable, not just documentation.

Likely questions and short answers:

| Question | Answer |
|---|---|
| Why not run mutation on every PR? | 20–30 minutes and 5,389 mutants; it would dominate feedback time. It runs nightly and on demand. |
| Why is coverage not 100%? | The gate is a ratchet near the measured baseline; 100% would reward trivial tests. Weak modules are visible in the dashboard. |
| Why is security non-blocking? | Advisory noise in dev dependencies; findings are collected and triaged. The job can be promoted once high/critical findings are clean. |
| What happens if Actions is disabled on the fork? | The Actions tab banner enables workflows; `workflow_dispatch` then produces a run without a new commit. |
| Does the priority plugin skip tests? | No. It only reorders; `collected` equals the full hybrid suite. |

## Fallback if the live run is unavailable

Use the downloaded artifacts and the screen recording:

```bash
gh run list --workflow=ci.yml --limit 10
gh run view <last-green-run-id>
```

Then open `demo-artifacts/dashboard/dashboard.md`, `demo-artifacts/hybrid/htmlcov/index.html`
and `demo-artifacts/rtm/rtm_validation.md` locally. The technical content is the
same; do not spend demo time debugging the network.
