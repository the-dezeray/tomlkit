"""Build the Week 11 findings workbook (charts + minimal text).

Usage (from the repository root):
    python week11/mutation_v2/scripts/build_excel.py

Output:
    week11/Week11_TrackD_Findings.xlsx
"""

import csv
import json
from collections import Counter
from pathlib import Path

import xlsxwriter

ROOT = Path(__file__).resolve().parents[3]
M = ROOT / "week11" / "mutation_v2"
OUT = ROOT / "week11" / "Week11_TrackD_Findings.xlsx"

NAVY = "#1F3864"
BLUE = "#2E75B6"
LIGHT = "#D9E2F3"
GREY = "#A5A5A5"
GREEN = "#70AD47"
ORANGE = "#ED7D31"
RED = "#C00000"
PALE = "#F2F2F2"


def load():
    v1 = json.loads((ROOT / "week7" / "mutation_v1_summary.json").read_text())
    v2 = json.loads((M / "mutation_v2_summary.json").read_text())
    return v1, v2


def survivor_rows():
    with open(M / "survivors_v1_v2.csv", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    v1, v2 = load()
    survivors = survivor_rows()

    modules = sorted(
        (m for m in v2 if m != "TOTAL"),
        key=lambda m: v2[m]["survived"],
        reverse=True,
    )

    module_survivors = Counter(r["module"] for r in survivors)
    cat_counts = Counter(
        r["v1_category"] for r in survivors if r["also_survived_v1"] == "yes"
    )
    new_count = sum(1 for r in survivors if r["also_survived_v1"] != "yes")

    with open(M / "survivor_candidates.csv", newline="", encoding="utf-8") as fh:
        top_funcs = list(csv.DictReader(fh))[:10]

    wb = xlsxwriter.Workbook(OUT)
    wb.set_properties(
        {
            "title": "Week 11 Track D findings",
            "subject": "Mutation testing v2 — tomlkit",
            "author": "Group A",
            "comments": "Charts generated from committed mutation results.",
        }
    )

    f_title = wb.add_format({"bold": True, "font_size": 20, "font_color": NAVY})
    f_sub = wb.add_format({"font_size": 10, "font_color": "#595959"})
    f_kpi_label = wb.add_format(
        {"font_size": 9, "font_color": "#595959", "align": "center"}
    )
    f_kpi = wb.add_format(
        {
            "font_size": 22,
            "bold": True,
            "font_color": NAVY,
            "align": "center",
            "valign": "vcenter",
            "bg_color": PALE,
            "border": 1,
            "border_color": "#D9D9D9",
        }
    )
    f_kpi_pct = wb.add_format(
        {
            "font_size": 22,
            "bold": True,
            "font_color": NAVY,
            "align": "center",
            "valign": "vcenter",
            "num_format": "0.0%",
            "bg_color": PALE,
            "border": 1,
            "border_color": "#D9D9D9",
        }
    )
    f_kpi_good = wb.add_format(
        {
            "font_size": 22,
            "bold": True,
            "font_color": "white",
            "align": "center",
            "valign": "vcenter",
            "num_format": '+0.0" pp";-0.0" pp"',
            "bg_color": GREEN,
            "border": 1,
            "border_color": "#D9D9D9",
        }
    )
    f_header = wb.add_format(
        {
            "bold": True,
            "font_color": "white",
            "bg_color": NAVY,
            "align": "center",
            "border": 1,
            "border_color": "#BFBFBF",
        }
    )
    f_cell = wb.add_format({"border": 1, "border_color": "#D9D9D9"})
    f_cell_c = wb.add_format(
        {"border": 1, "border_color": "#D9D9D9", "align": "center"}
    )
    f_pct = wb.add_format(
        {
            "border": 1,
            "border_color": "#D9D9D9",
            "align": "center",
            "num_format": '0.0"%"',
        }
    )
    f_note = wb.add_format({"font_size": 9, "font_color": "#595959"})

    # ---------------- Dashboard ----------------
    ws = wb.add_worksheet("Dashboard")
    ws.hide_gridlines(2)
    ws.set_column("A:H", 15)
    ws.set_column("I:P", 13)
    ws.set_row(0, 34)

    ws.merge_range("A1:H1", "Week 11 — Track D — Mutation Testing v2", f_title)
    ws.merge_range("A2:H2", "tomlkit · final hybrid suite · 5,389 mutants", f_sub)

    ws.write("A4", "Mutation score v1", f_kpi_label)
    ws.write("B4", 0.578, f_kpi_pct)
    ws.write("C4", "Mutation score v2", f_kpi_label)
    ws.write("D4", 0.774, f_kpi_pct)
    ws.write("E4", "Improvement", f_kpi_label)
    ws.write("F4", 0.196, f_kpi_good)

    ws.write("A6", "Tests collected", f_kpi_label)
    ws.write("B6", 1507, f_kpi)
    ws.write("C6", "Survivors", f_kpi_label)
    ws.write("D6", 956, f_kpi)
    ws.write("E6", "No tests", f_kpi_label)
    ws.write("F6", 263, f_kpi)

    # Overall data used by the chart (hidden on the dashboard)
    for r in range(30, 35):
        ws.set_row(r, None, None, {"hidden": True})
    ws.write_row(30, 0, ["Suite", "Score"], f_header)
    ws.write_row(31, 0, ["v1 AI-only", 57.8], f_cell)
    ws.write_row(32, 0, ["v2 hybrid", 77.4], f_cell)

    chart = wb.add_chart({"type": "column"})
    chart.add_series(
        {
            "name": "Mutation score",
            "categories": ["Dashboard", 31, 0, 32, 0],
            "values": ["Dashboard", 31, 1, 32, 1],
            "fill": {"color": BLUE},
            "data_labels": {"value": True, "num_format": '0.0"%"'},
        }
    )
    chart.set_title({"name": "Overall mutation score", "name_font": {"size": 12}})
    chart.set_legend({"none": True})
    chart.set_y_axis(
        {"min": 0, "max": 100, "major_gridlines": {"visible": True, "line": {"color": "#E7E6E6"}}}
    )
    chart.set_size({"width": 520, "height": 300})
    chart.set_style(10)
    ws.insert_chart("A9", chart)

    # Outcomes doughnut
    ws.write_row(30, 4, ["Outcome", "v2"], f_header)
    for i, (k, label) in enumerate(
        [("killed", "Killed"), ("timeout", "Timeout"), ("survived", "Survived"), ("no_tests", "No tests")],
        start=31,
    ):
        ws.write_row(i, 4, [label, v2["TOTAL"][k]], f_cell)

    dough = wb.add_chart({"type": "doughnut"})
    dough.add_series(
        {
            "name": "v2 outcomes",
            "categories": ["Dashboard", 31, 4, 34, 4],
            "values": ["Dashboard", 31, 5, 34, 5],
            "points": [
                {"fill": {"color": GREEN}},
                {"fill": {"color": ORANGE}},
                {"fill": {"color": RED}},
                {"fill": {"color": GREY}},
            ],
            "data_labels": {"percentage": True, "font": {"size": 9}},
        }
    )
    dough.set_title({"name": "v2 outcomes", "name_font": {"size": 12}})
    dough.set_legend({"position": "bottom"})
    dough.set_size({"width": 520, "height": 300})
    dough.set_style(10)
    ws.insert_chart("I9", dough)

    ws.merge_range(
        "A27:P27",
        "Score = (killed + timeout) / total. v2 = shipped suite; v1 = AI-only at an earlier commit.",
        f_note,
    )

    # ---------------- Scores ----------------
    scores = wb.add_worksheet("Scores")
    scores.hide_gridlines(2)
    scores.set_column("A:A", 24)
    scores.set_column("B:D", 13)
    scores.set_column("F:Q", 11)
    scores.write_row(0, 0, ["Module", "v1 %", "v2 %", "Delta pp"], f_header)

    for i, m in enumerate(modules, start=1):
        scores.write(i, 0, m, f_cell)
        scores.write_number(i, 1, v1.get(m, {}).get("score", 0), f_pct)
        scores.write_number(i, 2, v2[m]["score"], f_pct)
        scores.write_number(
            i, 3, round(v2[m]["score"] - v1.get(m, {}).get("score", 0), 1), f_cell_c
        )
    total_row = len(modules) + 1
    scores.write(total_row, 0, "TOTAL", f_header)
    scores.write_number(total_row, 1, v1["TOTAL"]["score"], f_pct)
    scores.write_number(total_row, 2, v2["TOTAL"]["score"], f_pct)
    scores.write_number(
        total_row,
        3,
        round(v2["TOTAL"]["score"] - v1["TOTAL"]["score"], 1),
        f_cell_c,
    )
    scores.conditional_format(
        1, 3, len(modules), 3, {"type": "data_bar", "bar_color": GREEN}
    )
    scores.write_row(12, 0, ["Overall", "Score"], f_header)
    scores.write_row(13, 0, ["v1 AI-only", 57.8], f_cell)
    scores.write_row(14, 0, ["v2 hybrid", 77.4], f_cell)

    ch = wb.add_chart({"type": "column"})
    ch.add_series(
        {
            "name": "v1 AI-only",
            "categories": ["Scores", 1, 0, len(modules), 0],
            "values": ["Scores", 1, 1, len(modules), 1],
            "fill": {"color": GREY},
        }
    )
    ch.add_series(
        {
            "name": "v2 hybrid",
            "categories": ["Scores", 1, 0, len(modules), 0],
            "values": ["Scores", 1, 2, len(modules), 2],
            "fill": {"color": BLUE},
            "data_labels": {"value": True, "num_format": '0.0"%"', "font": {"size": 8}},
        }
    )
    ch.set_title({"name": "Mutation score by module", "name_font": {"size": 12}})
    ch.set_y_axis(
        {"min": 0, "max": 100, "major_gridlines": {"visible": True, "line": {"color": "#E7E6E6"}}}
    )
    ch.set_legend({"position": "bottom"})
    ch.set_size({"width": 760, "height": 340})
    ch.set_style(10)
    scores.insert_chart("F2", ch)

    ch2 = wb.add_chart({"type": "bar"})
    ch2.add_series(
        {
            "name": "Delta pp",
            "categories": ["Scores", 1, 0, len(modules), 0],
            "values": ["Scores", 1, 3, len(modules), 3],
            "fill": {"color": GREEN},
            "data_labels": {"value": True, "num_format": '+0.0;-0.0', "font": {"size": 8}},
        }
    )
    ch2.set_title({"name": "Improvement vs v1 (pp)", "name_font": {"size": 12}})
    ch2.set_legend({"none": True})
    ch2.set_size({"width": 560, "height": 340})
    ch2.set_style(10)
    scores.insert_chart("F20", ch2)

    # ---------------- Outcomes ----------------
    out = wb.add_worksheet("Outcomes")
    out.hide_gridlines(2)
    out.set_column("A:B", 20)
    out.set_column("C:C", 12)
    out.set_column("E:L", 12)
    out.write_row(0, 0, ["Outcome", "v1", "v2"], f_header)
    outcome_rows = [
        ("Killed", v1["TOTAL"]["killed"], v2["TOTAL"]["killed"]),
        ("Timeout", v1["TOTAL"]["timeout"], v2["TOTAL"]["timeout"]),
        ("Survived", v1["TOTAL"]["survived"], v2["TOTAL"]["survived"]),
        ("No tests", v1["TOTAL"]["no_tests"], v2["TOTAL"]["no_tests"]),
    ]
    for i, row in enumerate(outcome_rows, start=1):
        out.write_row(i, 0, list(row), f_cell)

    och = wb.add_chart({"type": "column"})
    och.add_series(
        {
            "name": "v1",
            "categories": ["Outcomes", 1, 0, 4, 0],
            "values": ["Outcomes", 1, 1, 4, 1],
            "fill": {"color": GREY},
        }
    )
    och.add_series(
        {
            "name": "v2",
            "categories": ["Outcomes", 1, 0, 4, 0],
            "values": ["Outcomes", 1, 2, 4, 2],
            "fill": {"color": BLUE},
            "data_labels": {"value": True, "font": {"size": 8}},
        }
    )
    och.set_title({"name": "Outcome composition", "name_font": {"size": 12}})
    och.set_legend({"position": "bottom"})
    och.set_size({"width": 520, "height": 320})
    och.set_style(10)
    out.insert_chart("E2", och)

    dch = wb.add_chart({"type": "doughnut"})
    dch.add_series(
        {
            "name": "v2",
            "categories": ["Outcomes", 1, 0, 4, 0],
            "values": ["Outcomes", 1, 2, 4, 2],
            "points": [
                {"fill": {"color": GREEN}},
                {"fill": {"color": ORANGE}},
                {"fill": {"color": RED}},
                {"fill": {"color": GREY}},
            ],
            "data_labels": {"percentage": True, "font": {"size": 9}},
        }
    )
    dch.set_title({"name": "v2 share", "name_font": {"size": 12}})
    dch.set_legend({"position": "bottom"})
    dch.set_size({"width": 420, "height": 320})
    dch.set_style(10)
    out.insert_chart("E21", dch)

    # ---------------- Survivors ----------------
    surv = wb.add_worksheet("Survivors")
    surv.hide_gridlines(2)
    surv.set_column("A:A", 22)
    surv.set_column("B:B", 12)
    surv.set_column("D:J", 12)
    surv.write_row(0, 0, ["Module", "Survivors"], f_header)
    for i, (m, n) in enumerate(module_survivors.most_common(), start=1):
        surv.write_row(i, 0, [m, n], f_cell)

    mch = wb.add_chart({"type": "bar"})
    mch.add_series(
        {
            "name": "Survivors",
            "categories": ["Survivors", 1, 0, len(module_survivors), 0],
            "values": ["Survivors", 1, 1, len(module_survivors), 1],
            "fill": {"color": RED},
            "data_labels": {"value": True, "font": {"size": 8}},
        }
    )
    mch.set_title({"name": "Survivors by module", "name_font": {"size": 12}})
    mch.set_legend({"none": True})
    mch.set_size({"width": 520, "height": 300})
    mch.set_style(10)
    surv.insert_chart("D2", mch)

    cat_start = len(module_survivors) + 3
    surv.write_row(cat_start, 0, ["Category", "Survivors"], f_header)
    cat_items = cat_counts.most_common()
    for i, (c, n) in enumerate(cat_items, start=cat_start + 1):
        surv.write_row(i, 0, [c, n], f_cell)
    if new_count:
        row = cat_start + 1 + len(cat_items)
        surv.write_row(row, 0, ["New since v1", new_count], f_cell)
        cat_items = cat_items + [("New since v1", new_count)]

    cch = wb.add_chart({"type": "bar"})
    cch.add_series(
        {
            "name": "Survivors",
            "categories": ["Survivors", cat_start + 1, 0, cat_start + len(cat_items), 0],
            "values": ["Survivors", cat_start + 1, 1, cat_start + len(cat_items), 1],
            "fill": {"color": ORANGE},
            "data_labels": {"value": True, "font": {"size": 8}},
        }
    )
    cch.set_title({"name": "Survivor categories", "name_font": {"size": 12}})
    cch.set_legend({"none": True})
    cch.set_size({"width": 620, "height": 320})
    cch.set_style(10)
    surv.insert_chart("D19", cch)

    fn_start = cat_start + len(cat_items) + 3
    surv.write_row(fn_start, 0, ["Function", "Survivors"], f_header)
    labels = []
    for i, r in enumerate(top_funcs, start=fn_start + 1):
        fn = r["function"].replace("..", ".").replace("tomlkit.", "")
        parts = fn.split(".")
        label = ".".join(parts[-2:]) if len(parts) >= 2 else fn
        labels.append(label)
        surv.write_row(i, 0, [label, int(r["survivors"])], f_cell)

    fch = wb.add_chart({"type": "bar"})
    fch.add_series(
        {
            "name": "Survivors",
            "categories": ["Survivors", fn_start + 1, 0, fn_start + len(top_funcs), 0],
            "values": ["Survivors", fn_start + 1, 1, fn_start + len(top_funcs), 1],
            "fill": {"color": NAVY},
            "data_labels": {"value": True, "font": {"size": 8}},
        }
    )
    fch.set_title({"name": "Top functions by survivors", "name_font": {"size": 12}})
    fch.set_legend({"none": True})
    fch.set_size({"width": 680, "height": 360})
    fch.set_style(10)
    surv.insert_chart(f"M{fn_start + 2}", fch)

    # ---------------- Suite ----------------
    suite = wb.add_worksheet("Suite")
    suite.hide_gridlines(2)
    suite.set_column("A:A", 26)
    suite.set_column("B:B", 12)
    suite.set_column("D:J", 12)
    suite.write_row(0, 0, ["Suite", "Tests"], f_header)
    suites = [
        ("tests/ (project)", 1065),
        ("tests_ai", 388),
        ("tests_manual", 19),
        ("tests_bdd", 3),
        ("tests_integration", 5),
        ("tests_property", 10),
        ("tests_tdd", 17),
    ]
    for i, row in enumerate(suites, start=1):
        suite.write_row(i, 0, list(row), f_cell)

    sch = wb.add_chart({"type": "column"})
    sch.add_series(
        {
            "name": "Tests",
            "categories": ["Suite", 1, 0, len(suites), 0],
            "values": ["Suite", 1, 1, len(suites), 1],
            "fill": {"color": BLUE},
            "data_labels": {"value": True, "font": {"size": 8}},
        }
    )
    sch.set_title({"name": "Tests by suite", "name_font": {"size": 12}})
    sch.set_legend({"none": True})
    sch.set_size({"width": 620, "height": 320})
    sch.set_style(10)
    suite.insert_chart("D2", sch)

    gstart = len(suites) + 3
    suite.write_row(gstart, 0, ["Group", "Tests"], f_header)
    suite.write_row(gstart + 1, 0, ["Group-authored", 442], f_cell)
    suite.write_row(gstart + 2, 0, ["Project tests", 1065], f_cell)

    gch = wb.add_chart({"type": "doughnut"})
    gch.add_series(
        {
            "name": "Tests",
            "categories": ["Suite", gstart + 1, 0, gstart + 2, 0],
            "values": ["Suite", gstart + 1, 1, gstart + 2, 1],
            "points": [
                {"fill": {"color": GREEN}},
                {"fill": {"color": GREY}},
            ],
            "data_labels": {"value": True, "font": {"size": 9}},
        }
    )
    gch.set_title({"name": "Group-authored vs project", "name_font": {"size": 12}})
    gch.set_legend({"position": "bottom"})
    gch.set_size({"width": 460, "height": 320})
    gch.set_style(10)
    suite.insert_chart("D20", gch)

    # ---------------- Notes ----------------
    notes = wb.add_worksheet("Notes")
    notes.hide_gridlines(2)
    notes.set_column("A:A", 110)
    notes.write("A1", "Reading notes", f_title)
    notes.write("A3", "• v2 is the shipped suite (1,507 collected tests); v1 is the 388-test AI-only baseline on an earlier commit.", f_note)
    notes.write("A4", "• Score = (killed + timeout) / total. 956 survivors; 263 no-tests; 34 timeouts.", f_note)
    notes.write("A5", "• Weakest module: exceptions (43.7%), dominated by exact-message survivors.", f_note)
    notes.write("A6", "• Root causes: exact oracle gaps, index-0 boundaries, AoT rendering, dotted-key replacement.", f_note)
    notes.write("A7", "• Full report: week11/mutation_v2/mutation_v2_report.md", f_note)

    wb.close()
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
