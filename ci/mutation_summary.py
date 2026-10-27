#!/usr/bin/env python3
"""Summarise ``mutmut results`` output for the CI dashboard.

Usage::

    python ci/mutation_summary.py \
        --results reports/mutation/mutmut_results.txt \
        --out reports/mutation/mutation_summary.json \
        --survivors reports/mutation/survivors.txt \
        --scope "tomlkit/ (full hybrid suite)"
"""

from __future__ import annotations

import argparse
import json

from collections import Counter
from datetime import datetime
from datetime import timezone
from pathlib import Path


STATUS_KEYS = {
    "killed": "killed",
    "survived": "survived",
    "timeout": "timeout",
    "no tests": "no_tests",
    "not checked": "not_checked",
    "suspicious": "suspicious",
    "skipped": "skipped",
    "untested": "no_tests",
}


def module_of(mutant: str) -> str:
    parts = mutant.split(".")
    if len(parts) > 1:
        return parts[1]
    return "unknown"


def parse_results(path: Path) -> list[tuple[str, str, str]]:
    if not path.is_file():
        raise SystemExit(f"mutation results not found: {path}")

    rows: list[tuple[str, str, str]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        mutant, status = line.rsplit(":", 1)
        status = status.strip().lower()
        key = STATUS_KEYS.get(status)
        if key is None:
            continue
        mutant = mutant.strip()
        rows.append((mutant, module_of(mutant), key))
    return rows


def add_scores(counter: Counter[str]) -> dict[str, float | int]:
    total = int(counter.get("total", 0))
    detected = int(counter.get("killed", 0)) + int(counter.get("timeout", 0))
    no_tests = int(counter.get("no_tests", 0))
    covered = total - no_tests
    return {
        "total": total,
        "killed": int(counter.get("killed", 0)),
        "timeout": int(counter.get("timeout", 0)),
        "survived": int(counter.get("survived", 0)),
        "no_tests": no_tests,
        "suspicious": int(counter.get("suspicious", 0)),
        "score": round(100.0 * detected / total, 1) if total else 0.0,
        "covered_score": round(100.0 * detected / covered, 1) if covered else 0.0,
    }


def summarise(rows: list[tuple[str, str, str]], scope: str) -> dict[str, object]:
    totals: Counter[str] = Counter()
    by_module: dict[str, Counter[str]] = {}
    for _mutant, module, status in rows:
        totals[status] += 1
        totals["total"] += 1
        counter = by_module.setdefault(module, Counter(total=0))
        counter[status] += 1
        counter["total"] += 1

    summary: dict[str, object] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": scope,
        "runner": "mutmut 3.8.0",
        "TOTAL": add_scores(totals),
        "modules": {
            module: add_scores(counter) for module, counter in sorted(by_module.items())
        },
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--survivors", type=Path, default=None)
    parser.add_argument("--scope", default="full suite")
    args = parser.parse_args()

    rows = parse_results(args.results)
    summary = summarise(rows, args.scope)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    if args.survivors is not None:
        survivors = sorted(
            mutant for mutant, _module, status in rows if status == "survived"
        )
        args.survivors.parent.mkdir(parents=True, exist_ok=True)
        args.survivors.write_text(
            "\n".join(survivors) + ("\n" if survivors else ""), encoding="utf-8"
        )

    total = summary["TOTAL"]
    assert isinstance(total, dict)
    print(
        f"mutants={total['total']} killed={total['killed']} "
        f"timeout={total['timeout']} survived={total['survived']} "
        f"no_tests={total['no_tests']} score={total['score']}% "
        f"covered_score={total['covered_score']}%"
    )


if __name__ == "__main__":
    main()
