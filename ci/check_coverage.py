#!/usr/bin/env python3
"""Check statement and branch coverage from a coverage.py JSON report."""

from __future__ import annotations

import argparse
import json
import sys

from datetime import datetime
from datetime import timezone
from pathlib import Path


def percentage(covered: int, total: int) -> float:
    return 100.0 * covered / total if total else 100.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", type=Path, default=Path("reports/coverage.json"))
    parser.add_argument("--min-statement", type=float, default=87.0)
    parser.add_argument("--min-branch", type=float, default=82.0)
    parser.add_argument("--min-combined", type=float, default=0.0)
    parser.add_argument("--out", type=Path, default=Path("reports/coverage_gate.json"))
    args = parser.parse_args()

    if not args.coverage.is_file():
        print(f"coverage JSON not found: {args.coverage}", file=sys.stderr)
        return 2

    data = json.loads(args.coverage.read_text(encoding="utf-8"))
    totals = data.get("totals", {})
    statements = int(totals.get("num_statements", 0))
    covered_lines = int(totals.get("covered_lines", 0))
    branches = int(totals.get("num_branches", 0))
    covered_branches = int(totals.get("covered_branches", 0))
    combined = float(totals.get("percent_covered", 0.0))

    statement_pct = percentage(covered_lines, statements)
    branch_pct = percentage(covered_branches, branches)
    checks = {
        "statement": statement_pct >= args.min_statement,
        "branch": branch_pct >= args.min_branch,
        "combined": combined >= args.min_combined,
    }
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "coverage_file": str(args.coverage),
        "statement": {
            "covered": covered_lines,
            "total": statements,
            "percent": round(statement_pct, 2),
            "minimum": args.min_statement,
            "passed": checks["statement"],
        },
        "branch": {
            "covered": covered_branches,
            "total": branches,
            "percent": round(branch_pct, 2),
            "minimum": args.min_branch,
            "passed": checks["branch"],
        },
        "combined": {
            "percent": round(combined, 2),
            "minimum": args.min_combined,
            "passed": checks["combined"],
        },
        "passed": all(checks.values()),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(
        f"statement {statement_pct:.2f}% (min {args.min_statement:.1f}%) | "
        f"branch {branch_pct:.2f}% (min {args.min_branch:.1f}%) | "
        f"combined {combined:.2f}%"
    )
    if not result["passed"]:
        print("coverage gate failed", file=sys.stderr)
        return 1
    print("coverage gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
