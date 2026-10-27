#!/usr/bin/env python3
"""Validate the Week 6 requirements traceability matrix against collected tests.

The RTM lives in ``week6/rtm/rtm_week6.csv``.  This script checks that every
test reference in the matrix still resolves to at least one collected pytest
node id, that requirement IDs are unique, and that R01-R16 are all present.
It writes machine-readable and human-readable evidence for the CI artifact.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path


DEFAULT_RTM = Path("week6/rtm/rtm_week6.csv")
DEFAULT_COLLECTED = Path("reports/collected_tests.txt")
DEFAULT_OUT = Path("reports/rtm")
TEST_COLUMN = "AI-baseline tests (tests_ai/)"
STATUS_COLUMN = "Status after AI baseline"


@dataclass
class Requirement:
    req_id: str
    status: str
    test_refs: list[str]
    matched: list[str]
    missing: list[str]


def normalize_nodeid(nodeid: str) -> str:
    if "::" in nodeid:
        path, rest = nodeid.split("::", 1)
        return path.replace("\\", "/") + "::" + rest
    return nodeid.replace("\\", "/")


def read_collected(path: Path) -> list[str]:
    if not path.is_file():
        raise SystemExit(f"collected test list not found: {path}")

    raw = path.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        text = raw.decode("utf-16", errors="replace")
    else:
        text = raw.decode("utf-8-sig", errors="replace")

    nodeids: list[str] = []
    for line in text.splitlines():
        line = line.strip().strip("\x00")
        if "::" in line and not line.startswith(("=", "!")):
            nodeids.append(normalize_nodeid(line))
    # Preserve order while removing duplicates.
    return list(dict.fromkeys(nodeids))


def is_placeholder(ref: str) -> bool:
    return ref.strip() in {"", "-", "\u2014", "\u2013", "\ufffd", "N/A", "n/a"}


def ref_matches(ref: str, nodeids: list[str]) -> list[str]:
    ref = ref.strip().replace("\\", "/")
    return [nodeid for nodeid in nodeids if ref in nodeid]


def read_rtm(path: Path, nodeids: list[str]) -> tuple[list[Requirement], list[str]]:
    if not path.is_file():
        raise SystemExit(f"RTM not found: {path}")

    requirements: list[Requirement] = []
    problems: list[str] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            req_id = (row.get("Req ID") or "").strip()
            if not req_id:
                continue
            status = (row.get(STATUS_COLUMN) or "").strip()
            refs = [
                ref.strip()
                for ref in (row.get(TEST_COLUMN) or "").split(";")
                if not is_placeholder(ref)
            ]
            matched: list[str] = []
            missing: list[str] = []
            for ref in refs:
                found = ref_matches(ref, nodeids)
                if found:
                    matched.extend(found)
                else:
                    missing.append(ref)
                    problems.append(f"{req_id}: test reference not collected: {ref}")
            requirements.append(
                Requirement(
                    req_id=req_id,
                    status=status,
                    test_refs=refs,
                    matched=sorted(set(matched)),
                    missing=missing,
                )
            )

    ids = [requirement.req_id for requirement in requirements]
    duplicates = sorted(req_id for req_id, count in Counter(ids).items() if count > 1)
    if duplicates:
        problems.append(f"duplicate requirement IDs: {', '.join(duplicates)}")

    expected = {f"R{number:02d}" for number in range(1, 17)}
    missing_ids = sorted(expected - set(ids))
    extra_ids = sorted(set(ids) - expected)
    if missing_ids:
        problems.append(f"missing requirement IDs: {', '.join(missing_ids)}")
    if extra_ids:
        problems.append(f"unexpected requirement IDs: {', '.join(extra_ids)}")

    return requirements, problems


def status_bucket(status: str) -> str:
    lowered = status.lower()
    if lowered.startswith("covered"):
        return "covered"
    if lowered.startswith("partial"):
        return "partial"
    if lowered.startswith("fails"):
        return "fails"
    if lowered.startswith("untested"):
        return "untested"
    return "other"


def write_outputs(
    out_dir: Path,
    requirements: list[Requirement],
    problems: list[str],
    nodeids: list[str],
    rtm_path: Path,
) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    counts = Counter(status_bucket(requirement.status) for requirement in requirements)
    with_tests = sum(1 for requirement in requirements if requirement.test_refs)
    fully_matched = sum(
        1
        for requirement in requirements
        if requirement.test_refs and not requirement.missing
    )
    total_refs = sum(len(requirement.test_refs) for requirement in requirements)
    matched_refs = sum(len(requirement.matched) for requirement in requirements)

    payload: dict[str, object] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rtm": str(rtm_path),
        "collected_tests": len(nodeids),
        "requirements": len(requirements),
        "requirements_with_at_least_one_test": with_tests,
        "requirements_with_all_refs_resolved": fully_matched,
        "test_references": total_refs,
        "matched_node_ids": matched_refs,
        "status_counts": dict(sorted(counts.items())),
        "problems": problems,
        "ok": not problems,
        "details": [
            {
                "req_id": requirement.req_id,
                "status": requirement.status,
                "status_bucket": status_bucket(requirement.status),
                "test_refs": requirement.test_refs,
                "matched_node_ids": requirement.matched,
                "missing_refs": requirement.missing,
            }
            for requirement in requirements
        ],
    }
    (out_dir / "rtm_validation.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Requirements Traceability Matrix validation",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- RTM: `{rtm_path}`",
        f"- Collected tests: **{len(nodeids)}**",
        f"- Requirements: **{len(requirements)}**",
        f"- Requirements with at least one collected test: **{with_tests}**",
        f"- Requirements whose references all resolve: **{fully_matched}**",
        f"- Test references: **{total_refs}** ({matched_refs} node id matches)",
        f"- Status counts: {dict(sorted(counts.items()))}",
        "",
        "## Requirements",
        "",
        "| Requirement | Status | Test refs | Resolved | Missing refs |",
        "|---|---|---:|---:|---|",
    ]
    for requirement in requirements:
        missing = ", ".join(f"`{ref}`" for ref in requirement.missing) or "-"
        lines.append(
            f"| {requirement.req_id} | {requirement.status} | "
            f"{len(requirement.test_refs)} | {len(requirement.matched)} | {missing} |"
        )
    lines.extend(["", "## Problems", ""])
    if problems:
        lines.extend(f"- {problem}" for problem in problems)
    else:
        lines.append("No broken references or missing requirement IDs.")
    (out_dir / "rtm_validation.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rtm", type=Path, default=DEFAULT_RTM)
    parser.add_argument("--collected", type=Path, default=DEFAULT_COLLECTED)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    nodeids = read_collected(args.collected)
    requirements, problems = read_rtm(args.rtm, nodeids)
    payload = write_outputs(args.out_dir, requirements, problems, nodeids, args.rtm)

    print(
        f"RTM: {payload['requirements']} requirements, "
        f"{payload['requirements_with_all_refs_resolved']} with all references resolved, "
        f"{payload['test_references']} references checked"
    )
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
