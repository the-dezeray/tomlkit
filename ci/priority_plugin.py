"""Run the Week 7 risk-ranked tests first.

The Week 7 prioritisation script produced ``week7/priority_order.csv``.  This
plugin reorders collected tests so the highest-risk tests execute first while
leaving every other test in its normal, stable order.  It is useful in CI
because a failure in a high-risk area is reported earlier and the execution
order is recorded as a downloadable artifact.

Enable with::

    pytest -p ci.priority_plugin

Disable with ``--no-priority-order`` or point at another CSV with
``--priority-order path/to/order.csv``.  The plugin never removes tests.
"""

from __future__ import annotations

import csv
import json

from pathlib import Path

import pytest


DEFAULT_ORDER = Path("week7/priority_order.csv")
DEFAULT_REPORT = Path("reports/priority_order.json")


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("comp441", "COMP 441 test prioritisation")
    group.addoption(
        "--priority-order",
        action="store",
        default=str(DEFAULT_ORDER),
        metavar="PATH",
        help="CSV produced by Week 7 prioritisation (default: %(default)s)",
    )
    group.addoption(
        "--priority-report",
        action="store",
        default=str(DEFAULT_REPORT),
        metavar="PATH",
        help="JSON file describing the executed priority order (default: %(default)s)",
    )
    group.addoption(
        "--no-priority-order",
        action="store_true",
        default=False,
        help="Do not reorder tests; useful for comparing with collection order",
    )


def _load_rank(path: Path) -> dict[str, int]:
    if not path.is_file():
        return {}

    rank: dict[str, int] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            test = (row.get("test") or "").strip()
            if not test:
                continue
            try:
                rank[test] = int(row["rank"])
            except (KeyError, TypeError, ValueError):
                continue
    return rank


def _normalize_nodeid(nodeid: str) -> str:
    """Normalise path separators without touching escape sequences in params."""

    if "::" in nodeid:
        path, rest = nodeid.split("::", 1)
        return path.replace("\\", "/") + "::" + rest
    return nodeid.replace("\\", "/")


def _rank_for(nodeid: str, rank: dict[str, int]) -> int | None:
    """Match a pytest node id against a Week 7 priority CSV entry.

    The CSV was built from ``pytest --collect-only`` output.  Match the exact
    node id first, then the parametrised base id.  Do not compare bare function
    tails: two different modules can share a function name, and a false match
    would put an unrelated test at the front of the run.
    """

    normalized = _normalize_nodeid(nodeid)
    if normalized in rank:
        return rank[normalized]

    base = normalized.split("[", 1)[0]
    if base in rank:
        return rank[base]

    for test, value in rank.items():
        candidate = _normalize_nodeid(test)
        candidate_base = candidate.split("[", 1)[0]
        if candidate_base == base:
            return value
        if normalized.endswith(candidate) or candidate.endswith(normalized):
            return value
    return None


def pytest_collection_modifyitems(
    session: pytest.Session,
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    if config.getoption("--no-priority-order"):
        return

    order_path = Path(config.getoption("--priority-order"))
    rank = _load_rank(order_path)
    if not rank:
        return

    ranked: list[tuple[int, int, int, pytest.Item]] = []
    matched = 0
    for index, item in enumerate(items):
        value = _rank_for(item.nodeid, rank)
        if value is None:
            ranked.append((1, 0, index, item))
        else:
            matched += 1
            ranked.append((0, value, index, item))

    ranked.sort(key=lambda row: (row[0], row[1], row[2]))
    items[:] = [row[3] for row in ranked]

    apfd = None
    evaluation = Path("week7/prioritisation_eval.json")
    if evaluation.is_file():
        try:
            apfd = json.loads(evaluation.read_text(encoding="utf-8")).get(
                "apfd_risk_based"
            )
        except (OSError, ValueError):
            apfd = None

    report = {
        "priority_file": str(order_path),
        "available": True,
        "collected": len(items),
        "matched": matched,
        "unmatched": len(items) - matched,
        "apfd_risk_based": apfd,
        "execution_order_first_50": [item.nodeid for item in items[:50]],
    }
    report_path = Path(config.getoption("--priority-report"))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
