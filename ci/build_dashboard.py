#!/usr/bin/env python3
"""Build the COMP 441 CI dashboard from test, coverage, RTM and mutation evidence.

The dashboard is plain Markdown plus CSV so it can be uploaded as a workflow
artifact and appended to ``$GITHUB_STEP_SUMMARY`` without a third-party service.
Every input is optional except coverage/JUnit; missing optional evidence is
reported as "not available" rather than failing the job.
"""

from __future__ import annotations

import argparse
import csv
import json
import os

from collections import Counter
from datetime import datetime
from datetime import timezone
from pathlib import Path
from xml.etree import ElementTree


def read_json(path: Path) -> dict[str, object] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def percentage(covered: int, total: int) -> float:
    return 100.0 * covered / total if total else 100.0


def read_junit(path: Path) -> dict[str, object] | None:
    if not path.is_file():
        return None
    try:
        root = ElementTree.parse(path).getroot()
    except (OSError, ElementTree.ParseError):
        return None

    suites = root.findall("testsuite") if root.tag == "testsuites" else [root]
    totals: Counter[str] = Counter()
    for suite in suites:
        for key in ("tests", "failures", "errors", "skipped"):
            totals[key] += int(suite.get(key, 0) or 0)
        totals["time_ms"] += int(float(suite.get("time", 0) or 0) * 1000)

    if totals["tests"] == 0:
        totals["tests"] = sum(1 for _ in root.iter("testcase"))

    skipped = totals["skipped"]
    xfailed = 0
    for testcase in root.iter("testcase"):
        skipped_node = testcase.find("skipped")
        if skipped_node is None:
            continue
        message = (skipped_node.get("message") or "").lower()
        kind = (skipped_node.get("type") or "").lower()
        if "xfail" in kind or "xfail" in message or "expected failure" in message:
            xfailed += 1

    passed = totals["tests"] - totals["failures"] - totals["errors"] - skipped
    return {
        "tests": totals["tests"],
        "passed": passed,
        "failures": totals["failures"],
        "errors": totals["errors"],
        "skipped": skipped,
        "xfailed": xfailed,
        "time_seconds": round(totals["time_ms"] / 1000.0, 2),
    }


def read_coverage(path: Path) -> dict[str, object] | None:
    data = read_json(path)
    if data is None:
        return None
    totals = data.get("totals", {})
    if not isinstance(totals, dict):
        return None
    statements = int(totals.get("num_statements", 0))
    covered_lines = int(totals.get("covered_lines", 0))
    branches = int(totals.get("num_branches", 0))
    covered_branches = int(totals.get("covered_branches", 0))

    modules: list[dict[str, object]] = []
    files = data.get("files", {})
    if isinstance(files, dict):
        for filename, payload in files.items():
            if not isinstance(payload, dict):
                continue
            summary = payload.get("summary", {})
            if not isinstance(summary, dict):
                continue
            modules.append(
                {
                    "file": str(filename).replace("\\", "/"),
                    "statement": round(float(summary.get("percent_covered", 0.0)), 1),
                    "covered_lines": int(summary.get("covered_lines", 0)),
                    "statements": int(summary.get("num_statements", 0)),
                }
            )
    modules.sort(key=lambda row: (row["statement"], row["file"]))

    return {
        "statement": {
            "covered": covered_lines,
            "total": statements,
            "percent": round(percentage(covered_lines, statements), 2),
        },
        "branch": {
            "covered": covered_branches,
            "total": branches,
            "percent": round(percentage(covered_branches, branches), 2),
        },
        "combined": round(float(totals.get("percent_covered", 0.0)), 2),
        "weakest_modules": modules[:5],
    }


def read_mutation(path: Path) -> dict[str, object] | None:
    data = read_json(path)
    if data is None:
        return None
    total = data.get("TOTAL")
    if not isinstance(total, dict):
        return None
    return {
        "scope": data.get("scope", "unknown"),
        "runner": data.get("runner", "unknown"),
        **total,
    }


def read_priority(path: Path) -> dict[str, object] | None:
    return read_json(path)


def read_defects(path: Path, sloc_file: Path | None) -> dict[str, object] | None:
    rows = read_csv_rows(path)
    if not rows:
        return None

    sloc = 4158
    if sloc_file is not None and sloc_file.is_file():
        raw = read_json(sloc_file)
        if raw is not None and isinstance(raw.get("total"), dict):
            sloc = int(raw["total"].get("sloc", sloc))

    statuses = Counter((row.get("status") or "unknown").strip().lower() for row in rows)
    return {
        "count": len(rows),
        "statuses": dict(sorted(statuses.items())),
        "sloc": sloc,
        "density": round(len(rows) / (sloc / 1000.0), 2) if sloc else 0.0,
    }


def read_baseline(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    return {
        (row.get("Indicator") or "").strip(): (row.get("Week 10 value") or "").strip()
        for row in rows
        if row.get("Indicator")
    }


def yes_no(value: bool) -> str:
    return "PASS" if value else "FAIL"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", type=Path, default=Path("reports/coverage.json"))
    parser.add_argument("--junit", type=Path, default=Path("reports/junit.xml"))
    parser.add_argument(
        "--rtm", type=Path, default=Path("reports/rtm/rtm_validation.json")
    )
    parser.add_argument(
        "--coverage-gate", type=Path, default=Path("reports/coverage_gate.json")
    )
    parser.add_argument(
        "--mutation", type=Path, default=Path("reports/mutation/mutation_summary.json")
    )
    parser.add_argument(
        "--mutation-fallback",
        type=Path,
        default=Path("week11/mutation_v2/mutation_v2_summary.json"),
        help="Committed Week 11 mutation summary used when no CI artifact exists",
    )
    parser.add_argument(
        "--priority", type=Path, default=Path("reports/priority_order.json")
    )
    parser.add_argument("--defects", type=Path, default=Path("reports/defects.csv"))
    parser.add_argument("--sloc", type=Path, default=Path("reports/radon_raw.json"))
    parser.add_argument(
        "--baseline", type=Path, default=Path("reports/week10/dashboard.csv")
    )
    parser.add_argument(
        "--v1-mutation", type=Path, default=Path("week7/mutation_v1_summary.json")
    )
    parser.add_argument("--out", type=Path, default=Path("reports/dashboard.md"))
    parser.add_argument("--csv", type=Path, default=Path("reports/dashboard.csv"))
    args = parser.parse_args()

    coverage = read_coverage(args.coverage)
    junit = read_junit(args.junit)
    rtm = read_json(args.rtm)
    gate = read_json(args.coverage_gate)
    mutation = read_mutation(args.mutation)
    mutation_source = str(args.mutation)
    if mutation is None and args.mutation_fallback.is_file():
        mutation = read_mutation(args.mutation_fallback)
        mutation_source = str(args.mutation_fallback)
        if mutation is not None:
            mutation["scope"] = f"committed Week 11 evidence ({mutation_source})"
            mutation["runner"] = "mutmut 3.8.0 (Week 11 evidence)"
    priority = read_priority(args.priority)
    defects = read_defects(args.defects, args.sloc)
    baseline = read_baseline(args.baseline)
    v1 = read_mutation(args.v1_mutation)

    tests_ok = bool(junit and junit["failures"] == 0 and junit["errors"] == 0)
    coverage_ok = bool(gate and gate.get("passed"))
    rtm_ok = bool(rtm and rtm.get("ok"))
    overall_ok = tests_ok and coverage_ok and rtm_ok

    generated = datetime.now(timezone.utc).isoformat()
    run_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repository = os.environ.get("GITHUB_REPOSITORY", "the-dezeray/tomlkit")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    run_url = f"{run_url}/{repository}/actions/runs/{run_id}" if run_id else run_url
    commit = os.environ.get("GITHUB_SHA", "local")
    ref = os.environ.get("GITHUB_REF_NAME", "local")

    lines: list[str] = [
        "# COMP 441 CI dashboard",
        "",
        f"- Generated: `{generated}`",
        f"- Commit: `{commit[:12]}` on `{ref}`",
        f"- Run: {run_url}",
        f"- **Overall CI gate: {yes_no(overall_ok)}**",
        "",
        "## Gate summary",
        "",
        "| Gate | Result | Evidence |",
        "|---|---|---|",
        f"| Tests | {yes_no(tests_ok)} | "
        f"{junit['tests'] if junit else 'no JUnit report'} tests |",
        f"| Coverage | {yes_no(coverage_ok)} | "
        f"{coverage['statement']['percent'] if coverage else 'no coverage report'}% statement |",
        f"| RTM references | {yes_no(rtm_ok)} | "
        f"{rtm.get('test_references', '?') if rtm else 'no RTM report'} references |",
        "",
    ]

    if junit:
        lines.extend(
            [
                "## Test results",
                "",
                "| Metric | Value |",
                "|---|---:|",
                f"| Collected / run | {junit['tests']} |",
                f"| Passed | {junit['passed']} |",
                f"| Failed | {junit['failures']} |",
                f"| Errors | {junit['errors']} |",
                f"| Skipped / xfailed | {junit['skipped']} ({junit['xfailed']} xfail) |",
                f"| Duration | {junit['time_seconds']} s |",
                "",
            ]
        )

    if coverage:
        lines.extend(
            [
                "## Coverage",
                "",
                "| Metric | Covered | Total | Percent |",
                "|---|---:|---:|---:|",
                f"| Statements | {coverage['statement']['covered']} | "
                f"{coverage['statement']['total']} | {coverage['statement']['percent']}% |",
                f"| Branches | {coverage['branch']['covered']} | "
                f"{coverage['branch']['total']} | {coverage['branch']['percent']}% |",
                "",
                "Weakest modules by statement coverage:",
                "",
                "| Module | Statement coverage | Lines |",
                "|---|---:|---:|",
            ]
        )
        for module in coverage["weakest_modules"]:
            lines.append(
                f"| `{module['file']}` | {module['statement']}% | "
                f"{module['covered_lines']}/{module['statements']} |"
            )
        lines.append("")

    if rtm:
        counts = rtm.get("status_counts", {})
        lines.extend(
            [
                "## Requirements traceability",
                "",
                "| Metric | Value |",
                "|---|---:|",
                f"| Requirements | {rtm.get('requirements', '?')} |",
                f"| Collected tests | {rtm.get('collected_tests', '?')} |",
                f"| Test references | {rtm.get('test_references', '?')} |",
                f"| Requirements with at least one test | "
                f"{rtm.get('requirements_with_at_least_one_test', '?')} |",
                f"| All references resolved | "
                f"{rtm.get('requirements_with_all_refs_resolved', '?')} |",
                f"| Status counts | {counts} |",
                "",
            ]
        )
        problems = rtm.get("problems", [])
        if problems:
            lines.append("Problems:")
            lines.extend(f"- {problem}" for problem in problems)
            lines.append("")

    if mutation:
        lines.extend(
            [
                "## Mutation testing",
                "",
                f"- Scope: `{mutation.get('scope', 'unknown')}`",
                f"- Runner: `{mutation.get('runner', 'unknown')}`",
                "",
                "| Metric | Value |",
                "|---|---:|",
                f"| Mutants | {mutation.get('total', '?')} |",
                f"| Killed | {mutation.get('killed', '?')} |",
                f"| Timeout (detected) | {mutation.get('timeout', '?')} |",
                f"| Survived | {mutation.get('survived', '?')} |",
                f"| No tests | {mutation.get('no_tests', '?')} |",
                f"| Score | {mutation.get('score', '?')}% |",
                f"| Covered score | {mutation.get('covered_score', '?')}% |",
                "",
            ]
        )
        if v1:
            lines.append(
                f"Week 7 v1 baseline: {v1.get('score', '?')}% "
                f"({v1.get('total', '?')} mutants, AI-only suite)."
            )
            lines.append("")
    else:
        lines.extend(
            [
                "## Mutation testing",
                "",
                "Not run in this workflow. The mutation job runs on `schedule` or "
                "`workflow_dispatch`; download its artifact from that run.",
                "",
            ]
        )

    if defects:
        lines.extend(
            [
                "## Quality metrics",
                "",
                "| Metric | Value | Note |",
                "|---|---:|---|",
                f"| Defects recorded | {defects['count']} | `reports/defects.csv` |",
                f"| SLOC | {defects['sloc']} | radon raw total |",
                f"| Defect density | {defects['density']} / KLOC | "
                f"{defects['count']} / {defects['sloc'] / 1000.0:.3f} |",
                "",
            ]
        )

    if priority:
        apfd = priority.get("apfd_risk_based")
        lines.extend(
            [
                "## Week 7 risk-based priority order",
                "",
                f"- Priority file: `{priority.get('priority_file', 'unknown')}`",
                f"- Collected tests: {priority.get('collected', '?')}",
                f"- Tests matched to a Week 7 rank: {priority.get('matched', '?')}",
                f"- APFD from the Week 7 evaluation: "
                f"{apfd if apfd is not None else 'not available'}",
                "",
            ]
        )

    if baseline:
        lines.extend(
            [
                "## Week 10 baseline vs this run",
                "",
                "| Indicator | Week 10 | This run |",
                "|---|---:|---:|",
            ]
        )
        comparisons = [
            ("Statement coverage", "statement", "percent"),
            ("Branch coverage", "branch", "percent"),
            ("Defect density (per KLOC)", "defects", "density"),
        ]
        for label, section, key in comparisons:
            if section == "defects":
                current = str(defects[key]) if defects else "not available"
            elif coverage:
                current = f"{coverage[section][key]}%"
            else:
                current = "not available"
            lines.append(f"| {label} | {baseline.get(label, '-')} | {current} |")
        lines.extend(
            [
                "",
                "Mutation is not compared in this table because the Week 10 value is "
                "for `_types.py` only; the Week 7 v1 baseline is shown in the mutation "
                "section. Compare mutation scores only within the same scope.",
                "",
            ]
        )

    lines.extend(
        [
            "## Reproducibility",
            "",
            "- Python: `3.12` for the canonical hybrid job",
            "- Poetry: `2.5.1` (the version that generated `poetry.lock`)",
            "- Test runner: `pytest 7.4.4`",
            "- BDD: `pytest-bdd 9.0.0` (Python >= 3.10; skipped on the 3.9 unit job)",
            "- Mutation runner: `mutmut 3.8.0` in a separate Python 3.12 tool environment",
            "- Coverage: statement and branch, from `coverage.json`",
            "",
            "## Artifacts",
            "",
            "| Artifact | Contents |",
            "|---|---|",
            "| `hybrid-evidence` | `coverage.xml`, `coverage.json`, `coverage_gate.json`, "
            "`junit.xml`, `htmlcov/`, `priority_order.json` |",
            "| `ai-baseline-evidence` | AI-only coverage and JUnit XML |",
            "| `rtm-evidence` | `rtm_validation.json`, `rtm_validation.md`, collected test IDs |",
            "| `mutation-evidence` | raw `mutmut results`, summary JSON, survivor list |",
            "| `dashboard` | this `dashboard.md` and `dashboard.csv` |",
            "| `security-evidence` | `pip-audit.json`, `bandit.txt` |",
            "",
        ]
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    csv_rows: list[tuple[str, str, str]] = [
        ("Overall CI gate", yes_no(overall_ok), "tests + coverage + RTM references"),
    ]
    if junit:
        csv_rows.extend(
            [
                ("Tests", str(junit["tests"]), "from junit.xml"),
                ("Passed", str(junit["passed"]), "from junit.xml"),
                ("Failed", str(junit["failures"]), "from junit.xml"),
                (
                    "Skipped/xfailed",
                    f"{junit['skipped']} ({junit['xfailed']} xfail)",
                    "from junit.xml",
                ),
            ]
        )
    if coverage:
        csv_rows.extend(
            [
                (
                    "Statement coverage",
                    f"{coverage['statement']['percent']}%",
                    "coverage.json",
                ),
                (
                    "Branch coverage",
                    f"{coverage['branch']['percent']}%",
                    "coverage.json",
                ),
                ("Combined coverage", f"{coverage['combined']}%", "coverage.json"),
            ]
        )
    if rtm:
        csv_rows.extend(
            [
                (
                    "RTM references",
                    str(rtm.get("test_references", "")),
                    "rtm_validation.json",
                ),
                (
                    "RTM requirements",
                    str(rtm.get("requirements", "")),
                    "rtm_validation.json",
                ),
                (
                    "RTM all references resolved",
                    str(rtm.get("requirements_with_all_refs_resolved", "")),
                    "",
                ),
            ]
        )
    if mutation:
        csv_rows.extend(
            [
                (
                    "Mutation score",
                    f"{mutation.get('score')}%",
                    str(mutation.get("scope", "")),
                ),
                ("Mutation killed", str(mutation.get("killed", "")), ""),
                ("Mutation survived", str(mutation.get("survived", "")), ""),
            ]
        )
    if defects:
        csv_rows.extend(
            [
                ("Defects recorded", str(defects["count"]), "reports/defects.csv"),
                ("Defect density (per KLOC)", str(defects["density"]), ""),
            ]
        )

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Indicator", "Value", "Notes"])
        writer.writerows(csv_rows)

    print(f"dashboard written to {args.out} and {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
