"""Build the COMP 441 Group A final report as a Word document.

Run from the repository root:
    python reports/final/build_report.py
"""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "COMP 441 Group A - Final Report.docx"

NAVY = RGBColor(0x1F, 0x38, 0x64)
GREY = RGBColor(0x59, 0x59, 0x59)
HEADER_FILL = "1F3864"


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_margins(table, top=25, bottom=25, left=65, right=65):
    tbl_pr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for side, value in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        node = OxmlElement(f"w:{side}")
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")
        mar.append(node)
    tbl_pr.append(mar)


def add_rich_text(paragraph, text, size=None, color=None, italic=False):
    """Add text with **bold** markers."""
    for i, part in enumerate(text.split("**")):
        if not part:
            continue
        run = paragraph.add_run(part)
        run.bold = i % 2 == 1
        run.italic = italic
        if size is not None:
            run.font.size = Pt(size)
        if color is not None:
            run.font.color.rgb = color
    return paragraph


def para(text="", size=11, bold=False, italic=False, align=None, space_after=4,
         space_before=0, color=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing = 1.0
    if align is not None:
        p.alignment = align
    if text:
        if bold:
            run = p.add_run(text)
            run.bold = True
            run.font.size = Pt(size)
            if color is not None:
                run.font.color.rgb = color
        else:
            add_rich_text(p, text, size=size, color=color, italic=italic)
    return p


def bullet(text, size=11):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    add_rich_text(p, text, size=size)
    return p


def h1(text):
    p = doc.add_heading(text, level=1)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    return p


def h2(text):
    p = doc.add_heading(text, level=2)
    p.paragraph_format.space_before = Pt(7)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    return p


def caption(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = GREY
    return p


def figure(number, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(1)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("[[]]")
    run.bold = True
    run.font.size = Pt(16)
    run.font.color.rgb = GREY
    caption(f"Figure {number}. {text}")


def table(headers, rows, widths, size=8.5, header_size=8.5):
    tbl = doc.add_table(rows=1, cols=len(headers))
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.allow_autofit = False
    set_cell_margins(tbl)

    hdr = tbl.rows[0]
    for i, header in enumerate(headers):
        cell = hdr.cells[i]
        cell.width = Cm(widths[i])
        set_cell_shading(cell, HEADER_FILL)
        cell.text = ""
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(header)
        run.bold = True
        run.font.size = Pt(header_size)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for row_data in rows:
        row = tbl.add_row()
        for i, value in enumerate(row_data):
            cell = row.cells[i]
            cell.width = Cm(widths[i])
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            add_rich_text(p, str(value), size=size)
    return tbl


def page_break():
    doc.add_page_break()


def add_field(paragraph, instr):
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = f" {instr} "
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr_el)
    run._r.append(fld_end)
    run.font.size = Pt(8.5)


# ---------------------------------------------------------------------------
# Document setup
# ---------------------------------------------------------------------------

doc = Document()
doc.core_properties.title = "AI-Augmented Test Suite for TOML Kit - Final Report"
doc.core_properties.author = "COMP 441 Group A"
doc.core_properties.subject = "COMP 441 Software Analysis and Testing - Group Project"
doc.core_properties.keywords = "AI testing, mutation testing, TOML Kit, Track D"

section = doc.sections[0]
section.page_width = Cm(21.0)
section.page_height = Cm(29.7)
section.top_margin = Cm(2.5)
section.bottom_margin = Cm(2.5)
section.left_margin = Cm(2.5)
section.right_margin = Cm(2.5)
section.different_first_page_header_footer = True

normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
normal.paragraph_format.space_after = Pt(4)
normal.paragraph_format.line_spacing = 1.0

for style_name, size, color in (("Heading 1", 15, NAVY), ("Heading 2", 12.5, NAVY)):
    style = doc.styles[style_name]
    style.font.name = "Calibri"
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = color
    style.paragraph_format.keep_with_next = True

# Header (not on the cover)
header = section.header
hp = header.paragraphs[0]
hp.text = ""
hp.paragraph_format.tab_stops.add_tab_stop(Cm(16.0), WD_TAB_ALIGNMENT.RIGHT)
run = hp.add_run("COMP 441 Group A  |  Final Report")
run.font.size = Pt(8.5)
run.font.color.rgb = GREY
hp.add_run("\t")
run = hp.add_run("TOML Kit  |  Track D")
run.font.size = Pt(8.5)
run.font.color.rgb = GREY

# Footer (not on the cover)
footer = section.footer
fp = footer.paragraphs[0]
fp.text = ""
fp.paragraph_format.tab_stops.add_tab_stop(Cm(16.0), WD_TAB_ALIGNMENT.RIGHT)
run = fp.add_run("COMP 441 Group A  |  AI-Augmented Test Suite")
run.font.size = Pt(8.5)
run.font.color.rgb = GREY
fp.add_run("\t")
run = fp.add_run("Page ")
run.font.size = Pt(8.5)
add_field(fp, "PAGE")
run = fp.add_run(" of ")
run.font.size = Pt(8.5)
add_field(fp, "NUMPAGES")


# ---------------------------------------------------------------------------
# Cover
# ---------------------------------------------------------------------------

for _ in range(5):
    para("", space_after=0)

para("COMP 441 — Software Analysis and Testing", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, color=NAVY, space_after=2)
para("Group Project: AI-Augmented Test Suite", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREY, space_after=20)
para("AI-Augmented Test Suite for TOML Kit", size=26, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, color=NAVY, space_after=4)
para("Final Report", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREY, space_after=18)
para("Track D — Developer Tooling / API Library", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, color=NAVY, space_after=4)
para("Repository: github.com/the-dezeray/tomlkit", size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
para("Fork of python-poetry/tomlkit  |  tomlkit 0.15.1  |  MIT licence", size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREY, space_after=24)
para("Group A", size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, color=NAVY, space_after=4)
para("Final submission: 10 November 2026", size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREY, space_after=2)
para("Prepared in accordance with Section 9 of the COMP 441 Group Project Brief", size=9.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREY)

page_break()


# ---------------------------------------------------------------------------
# 1. Executive summary
# ---------------------------------------------------------------------------

h1("1. Executive Summary")
bullet("**AI-only:** 388 tests from seven prompts; 81.7% statement / 66.3% branch coverage; mutation score **57.8%** (3,087 killed + 26 timed out of 5,389).")
bullet("**Final hybrid:** 1,507 tests (1,502 passed, 5 strict xfailed); 91.6% / 85.6% coverage; mutation **77.4%** (4,136 + 34), a **+19.6 pp** gain; covered-code score 81.3%.")
bullet("**Quality:** 8 confirmed defects (3 fixed test-first, 5 open/pinned), 1.92 defects/KLOC, RTM 88% (14/16), APFD 0.772 versus 0.637; half the sampled mutants found in 16 tests instead of 51.")
para("The AI suite covered common paths but missed boundaries, exact messages, combinations and formatting branches; 1,890 mutants survived. Eleven manual tests, designed with EP/BVA/decision tables, killed named survivors; Hypothesis found two real defects. AI was a fast first draft, not ground truth.")
para("**Caveat:** v1 measured the 388-test AI-only suite at `8c959b5`; v2 measured the shipped 1,507-test suite at `6b8884f`, including 1,065 pre-existing tests and after three TDD fixes. This is not a controlled experiment (Section 7.6).")


# ---------------------------------------------------------------------------
# 2. Methodology
# ---------------------------------------------------------------------------

h1("2. Methodology")
para("We froze the repository at **`8c959b5`** for the AI baseline and **`6b8884f`** for the final suite. Mutation testing covers the ten production modules in `tomlkit/` (5,389 mutants); `_compat.py` and `_types.py` were excluded to keep the v1 and v2 scopes identical.")
para("**Tools:** Claude claude-opus-5-5 via claude.ai (seven prompts); pytest 9.1.1 + pytest-cov; mutmut 3.8.0; Hypothesis 6.170.12; pytest-bdd 9.0.0; radon, Pylint, Ruff and CrossHair; GitHub Actions.")
para("**Measures:** mutation score = (killed + timeout) / total; covered-code score excludes no-test mutants; timeouts count as detected; coverage is coverage.py statement/branch; APFD is the weighted average test position at first kill; defect density = defects / KLOC; RTM completeness = requirements with a passing test / total.")


# ---------------------------------------------------------------------------
# 3. Test plan and risk register
# ---------------------------------------------------------------------------

h1("3. Test Plan and Risk Register")
para("**Scope:** the ten production modules, public API and file-level round-trip behaviour. **Entry:** repository builds, base commit frozen, AI baseline and RTM v1 complete. **Exit:** all blocking tests pass; statement coverage ≥87%; branch coverage ≥82%; all RTM references resolve; mutation ≥75% nightly; 3 TDD cycles, 3 BDD scenarios, 5 integration tests and 10 property tests complete.")
para("**Estimation:** three-point estimate for mutation and hybrid phases: optimistic 12 h, likely 20 h, pessimistic 30 h; expected = (12 + 4×20 + 30) / 6 = **20.3 h**. Mutation runs took ~20 minutes each on eight workers; human survivor analysis dominated.")
caption("Table 1. Top five project risks.")
table(
    ["Risk", "P", "I", "Mitigation"],
    [
        ["Mutation run too slow", "High", "High", "Fixed 10-module scope; eight workers; nightly schedule"],
        ["AI tests shallow/overfitted", "High", "High", "Assertion audit; mutation v1; 11 survivor tests; review every test"],
        ["Environment/version drift", "Medium", "High", "Frozen commits; pinned versions; raw logs; WSL2/Ubuntu"],
        ["Equivalent mutants distort score", "Medium", "Medium", "Sample triage; covered-code score; explicit caveat"],
        ["CI feedback too slow", "High", "Medium", "Fast PR gate; mutation/performance/security nightly"],
    ],
    [5.8, 1.3, 1.3, 7.6],
)


# ---------------------------------------------------------------------------
# 4. Requirements traceability
# ---------------------------------------------------------------------------

h1("4. Requirements Traceability Matrix")
para("We derived **16 requirements (R01–R16)** from the README, CHANGELOG, docstrings and reverse-engineered code. After the AI baseline: 8 covered, 4 partial, 3 failed (R08, R14, R15), 1 untested (R16). Final: **14/16 (88%)**.")
caption("Table 2. RTM summary by test level. Full matrix in Appendix A.")
table(
    ["Level", "Requirements covered", "Tests", "Result"],
    [
        ["AI unit baseline", "R01–R15", "388", "8 covered, 4 partial, 3 failing"],
        ["Manual survivor unit", "R03, R04, R05, R07, R12, R13, R14", "K1–K11", "11 named mutants killed"],
        ["Property / BDD / integration", "R01–R10, R13", "P1–P5, 3 BDD, IT1–IT5", "D1/D7 found; end-to-end file checks"],
        ["TDD regression", "R08, R10, R14", "C1–C3", "3 defects fixed"],
        ["**Final**", "**16**", "**1,507**", "**14 verified (88%)**"],
    ],
    [3.4, 5.8, 3.8, 3.0],
)
para("**Open gaps:** R15 — `key([])` still serialises to an unparseable key (pinned by strict xfail); R16 — no large-input scaling test (performance baseline only). Each manual test names its mutant/gap, and each BDD scenario names its RTM ids and test level.")


# ---------------------------------------------------------------------------
# 5. Static analysis
# ---------------------------------------------------------------------------

h1("5. Static Analysis")
para("Radon analysed **524 blocks**: average complexity **3.04 (A)**, but **13 functions rank D–F**, and `container`, `parser` and `items` have maintainability index **0.00 (C)**. Pylint rated the package **9.33/10**; its 11 `api.py` findings were mostly import aliases, shadowed names and protected access, not behavioural defects.")
caption("Table 3. Top ten static-analysis findings, triaged by risk.")
table(
    ["#", "Function / finding", "CC", "Evidence", "Triage"],
    [
        ["1", "Container.append", "74", "46 branches, 92 statements; formatting state machine", "High"],
        ["2", "Container._replace_at", "41", "17 branches; dotted/out-of-order replacement", "High"],
        ["3", "Parser._parse_string", "40", "25 branches, 64 statements; four string forms", "High"],
        ["4", "Parser._parse_table", "37", "30 branches, 81 statements; redefinition/out-of-order", "High"],
        ["5", "Array.__delitem__", "36", "19 branches; slice/comma handling", "High"],
        ["6", "Container._render_table", "31", "16 branches; AoT headers", "Medium"],
        ["7", "item()", "31", "24 branches; type dispatch", "Medium"],
        ["8", "InlineTable.as_string", "30", "20 branches, 59 statements", "Medium"],
        ["9", "Array.insert", "26", "15 branches; index-0 boundary", "Medium"],
        ["10", "Parser._parse_value", "25", "19 branches; value dispatch", "Medium"],
    ],
    [0.8, 4.6, 1.1, 7.3, 1.7],
)
para("**Linter vs LLM.** A focused Claude review of `container.py` agreed on the `Container.append` hotspot, but the linter flagged protected access/naming while the LLM highlighted semantic risks in `_replace_at`, `_render_table` and out-of-order validation. We treated these as hypotheses; two became tests (K10 and render/AoT work). Linters find structure; LLMs suggest behaviour; tests decide.")
para("**Symbolic analysis.** A CrossHair contract for `api.date()` returned **`0001-10-30 00:00`** in under 60 seconds — a datetime string accepted as a date. `datetime` is a subclass of `date`, and the code used `isinstance`; example tests had checked ordinary dates/datetimes but not the subtype boundary. This became D1 and TDD cycle C1.")


# ---------------------------------------------------------------------------
# 6. AI-only baseline
# ---------------------------------------------------------------------------

h1("6. AI-Only Baseline")
para("Claude claude-opus-5-5 via claude.ai, 18 October 2026, against `8c959b5`. Seven prompts covered role rules, public API, parser, items, container, utilities/errors and file I/O; the model saw module source and README only. **Run 1:** 387 collected, 379 passed, 8 failed. Five were AI assumptions (repaired); three were real defects kept as strict xfails: **D1** `date()` accepts datetime strings, **D2** `Bool.__eq__` returns `NotImplemented`, **D3** inline duplicate raises `KeyAlreadyPresent` not `ParseError`. **Run 2:** 388 collected, 385 passed, 3 xfailed.")
caption("Table 4. Coverage before and after the hybrid suite.")
table(
    ["Suite", "Tests", "Statement", "Branch"],
    [
        ["AI-only baseline", "388", "81.7%", "66.3%"],
        ["Maintainers' existing suite", "1,058", "89.5%", "83.1%"],
        ["Final hybrid suite", "1,507", "91.6%", "85.6%"],
    ],
    [7.8, 3.0, 2.6, 2.6],
)
figure(1, "Statement and branch coverage: AI-only, maintainers and final hybrid suite.")
para("The AI suite's weakest branch area was `container.py`: 58.2% versus 83.6% for the maintainers. It covered common paths, not the formatting state machine.")
para("**Assertion audit (305 test functions):** 209 strong (68.5%), 47 partial (15.4%), 48 weak (15.7%), 1 smoke. Examples: `assert boolean(\"yes\") is False` locks in current behaviour; broad `pytest.raises(ParseError)` lets a wrong subclass/message survive; type-only `item()` checks do not test `unwrap()`. The suite was **broad but shallow**: 81.7% coverage, but 1,890 survivors and 386 never-reached lines. The repair loop also risked changing expectations to match implementation; every repair was checked against source/docs, and D1–D3 were kept as defects.")


# ---------------------------------------------------------------------------
# 7. Mutation testing
# ---------------------------------------------------------------------------

h1("7. Mutation Testing")
para("mutmut 3.8.0 mutated the ten modules. v1 used only `tests_ai/` (388 tests); v2 used the shipped suite (1,507). Score = (killed + timeout) / 5,389; timeouts count as detected; “no tests” means the line was never executed.")
para("**v1:** 3,087 killed, 26 timed out, **1,890 survived**, 386 no tests — **57.8%** overall, **62.2%** covered. The three large modules held 86% of mutants and all were below the 70% target: `container` 47.2%, `items` 54.1%, `parser` 64.0%; `exceptions` 33.3%.")
caption("Table 5. Eight representative v1 survivors and the manual tests that killed them.")
table(
    ["ID", "Survivor / mutation", "Why the AI missed it", "Manual test (technique)"],
    [
        ["K1", "InvalidNumberError message (case)", "Checked type/position, not exact case", "Assert exact message and (1,6) (EP)"],
        ["K2", "Source._to_linecol `>` → `>=`", "No index exactly at a newline", "Advance 2/3; (1,2), (2,0) (BVA)"],
        ["K3", "_parse_escaped_char `and` → `or`", "Tested invalid letter, not backslash-space", "Reject `\"x\\ y\"`; allow multiline (EP)"],
        ["K4", "parse_rfc3339 `tz[1:]` → `tz[2:]`", "Offsets below 10 h hide lost zero", "`+10:00`, `-11:30`, `+23:59` (BVA)"],
        ["K5", "Time-only fraction truncation", "Tested datetime branch only", "7-digit fraction → 123456 µs (EP)"],
        ["K6", "Array.insert `pos < 0` → `pos <= 0`", "Tested 1 and -1, not 0", "Insert 0; values + reparse (BVA)"],
        ["K7", "Array.__delitem__ stepped slice", "Tested contiguous deletion only", "Even/odd slices; reparse (EP)"],
        ["K8", "Array.add_line CR check", "Tested `\\n` only", "Reject `\\n`, `\\r`, `\\r\\n` (EP)"],
    ],
    [1.1, 5.0, 5.3, 4.6],
)
para("All eleven K tests failed on their mutant and passed on the real code. K9–K11 covered `sort_keys` in an array of tables (decision table), a table split across three out-of-order fragments (BVA), and CRLF normalisation on write (EP).")
figure(2, "Mutation score of the AI-only suite by module (v1).")
para("**v2:** 4,136 killed, 34 timed out, **956 survived**, 263 no tests — **77.4%** overall, **81.3%** covered.")
caption("Table 6. Mutation score by module: v1 versus v2.")
table(
    ["Module", "v1", "v2", "Δ", "v2 survivors", "v2 no tests"],
    [
        ["_utils", "95.0", "95.9", "+0.9", "9", "0"],
        ["api", "83.9", "88.6", "+4.7", "17", "0"],
        ["container", "47.2", "75.7", "+28.5", "251", "55"],
        ["exceptions", "33.3", "43.7", "+10.4", "88", "10"],
        ["items", "54.1", "73.5", "+19.4", "331", "198"],
        ["parser", "64.0", "83.4", "+19.4", "230", "0"],
        ["source", "82.7", "87.4", "+4.7", "16", "0"],
        ["toml_file", "72.6", "80.8", "+8.2", "14", "0"],
        ["**Total**", "**57.8**", "**77.4**", "**+19.6**", "**956**", "**263**"],
    ],
    [4.0, 2.0, 2.0, 2.0, 3.0, 3.0],
)
para("Every module improved; `container` +28.5, `items`/`parser` +19.4. `exceptions` remains weakest at 43.7%. Of 956 survivors, 931 were already in v1; 25 are new. Dominant categories: dropped arguments (334), exception messages (218), string literals (93), boolean logic (89), boundaries (67), arithmetic (65). The 263 no-test mutants are mostly formatting/rendering in `items` (198) and `container` (55).")
figure(3, "Module-level mutation improvement from v1 to v2.")
figure(4, "Overall mutation score: 57.8% AI-only versus 77.4% final hybrid.")
h2("7.5 AI-guided prioritisation")
para("We ranked 149 AI tests by additional complexity-weighted, two-year-churn risk; shorter runtime broke ties. Mutation outcomes were excluded, so APFD is out-of-sample. On 258 sampled mutants, risk order scored **APFD 0.7722** versus **0.6369** default and **0.6911** for the mean of 200 random orders. It found half the mutants in **16 tests instead of 51**, and 90% in 106 instead of 120. This is a pure ordering change: in CI a regression surfaces roughly three times sooner.")
figure(5, "Detection curve: risk-based order versus default order.")
h2("7.6 Threats to validity")
bullet("**Code changed:** v1 at `8c959b5`, v2 at `6b8884f` after C1–C3; the delta is not a pure test effect. No same-commit AI-only rerun.")
bullet("**Suite changed:** v2 includes 1,065 project tests and 442 group tests, so it measures the shipped suite, not our marginal contribution.")
bullet("**One test deselected:** the deep-nesting test cannot run under mutmut's trampoline; it passes normally.")
bullet("**Timeouts/equivalents:** timeouts count as detected; no full equivalence triage. Two of the top ten survivors look equivalent; an ~80% adjusted score is illustrative only.")
bullet("**Single project/runner:** results are specific to tomlkit and mutmut 3.8.0.")


# ---------------------------------------------------------------------------
# 8. Hybrid suite design
# ---------------------------------------------------------------------------

h1("8. Hybrid Suite Design")
para("The final suite is **1,507 tests**: 1,065 project tests, 388 AI, 19 manual, 3 BDD, 5 integration, 10 property and 17 TDD. The group authored **442 (29.3%)**, 54 more than the AI baseline. We added tests by gap, not volume: exact messages (EP), boundaries for index 0, two-digit offsets, line boundaries and three-fragment tables (BVA), `sort_keys` × table/AoT (decision table), repeated insertion (state transition), parse/dump invariants and file-level acceptance scenarios. Each manual test names its mutant, technique and RTM id.")
para("The suite confirmed **eight defects**, not just mutants: AI found four (D1, D2, D3, D5); D1 was also exposed by CrossHair/P5, D7 by Hypothesis, D8 by exploratory testing, M1 by Week 10 mutation, and D6 by manual/exploratory follow-up. Three are fixed test-first (D1, D6, D7); five are open but pinned. Defect density is **1.92/KLOC**.")
caption("Table 7. Confirmed defects and status.")
table(
    ["ID", "Defect", "Found by", "Status"],
    [
        ["D1", "`date()` accepts datetime strings", "AI baseline / CrossHair / P5", "Fixed (C1)"],
        ["D2", "`Bool.__eq__` returns NotImplemented", "AI baseline", "Open, strict xfail"],
        ["D3", "Inline duplicate raises KeyAlreadyPresent", "AI baseline", "Open, strict xfail"],
        ["D5", "`key([])` serialises to an unparseable key", "AI baseline", "Open, strict xfail"],
        ["D6", "`comment()` writes invalid TOML for bare CR", "Manual/exploratory follow-up", "Fixed (C3)"],
        ["D7", "Multiline strings emit a bare CR", "Hypothesis P3", "Fixed (C2)"],
        ["D8", "Insert at 0 drops the following space", "Exploratory session", "Open, strict xfail (K6)"],
        ["M1", "`_CustomDict.__or__` drops existing keys", "Week 10 mutation", "Open, strict xfail"],
    ],
    [1.1, 7.6, 4.2, 3.1],
)
figure(6, "Confirmed defects by discovery source.")


# ---------------------------------------------------------------------------
# 9. TDD and BDD
# ---------------------------------------------------------------------------

h1("9. TDD and BDD Evidence")
para("Three test-first cycles, each red–green–refactor, with raw pytest output in `week8/tdd_runs/` and `week11/tdd_runs/`.")
caption("Table 8. TDD cycles.")
table(
    ["Cycle", "Defect", "Red", "Green", "Refactor"],
    [
        ["C1", "D1 — `date()` accepts datetime strings", "4 failed, 1 passed", "1,475 passed", "1,475 passed"],
        ["C2", "D7 — multiline strings emit a bare CR", "6 failed, 2 passed", "1,485 passed", "1,485 passed"],
        ["C3", "D6 — `comment()` with a bare CR", "2 failed, 2 passed", "1,489 passed", "1,489 passed"],
    ],
    [1.3, 6.5, 3.0, 2.6, 2.6],
)
para("C1 made `date()` check exact type; C2 escaped a lone CR in basic multiline strings and rejected it in literal strings while preserving CRLF; C3 split CR, LF and CRLF into one comment marker per line. Refactors shared the exact-type helper and bare-CR rule. No fourth cycle was added because the brief requires three and a late change would have moved the frozen v2 commit.")
para("**BDD:** three Gherkin scenarios automated with pytest-bdd 9.0.0 — (1) bump the version and keep every comment/blank line (acceptance, R03/R07, exact file on disk); (2) a typo is reported at line 3 (acceptance, R04, file unchanged); (3) a Windows file keeps CRLF (acceptance, R07). The first is end-to-end; all three use real files. We checked the scenario can fail: a save that drops comments breaks the exact-file assertion.")


# ---------------------------------------------------------------------------
# 10. Integration and acceptance
# ---------------------------------------------------------------------------

h1("10. Integration and Acceptance Testing")
para("Five integration tests combine real components, not mocks:")
bullet("**IT1 (R06):** `dump` → real text/binary file → `load`.")
bullet("**IT2 (R03/R07/R12):** TOMLFile + array/table editing + writer; comments survive.")
bullet("**IT3 (R13):** out-of-order proxy + container + renderer + parser; edit/add/delete and reparse.")
bullet("**IT4 (R01/R02):** builders → `dumps` → parser for document, table, inline table and AoT.")
bullet("**IT5 (R05):** `sort_keys` with nested AoT; header placement and key order reparse correctly.")
para("The BDD scenarios are the acceptance level (R03/R04/R07). Integration tests sit below acceptance but above unit: they catch component-contract failures that isolated unit tests miss. The `sort_keys`/AoT case is the clearest example — a value emitted after an AoT header would be absorbed into the table, so the test asserts order and reparse, not just the dictionary.")


# ---------------------------------------------------------------------------
# 11. Track D specialised stream and NFR checks
# ---------------------------------------------------------------------------

h1("11. Track D Specialised Stream and NFR Checks")
para("**Property-based testing (Track D stream).** Ten tests ran **200 generated examples each** with Hypothesis 6.170.12. P5 found **D1** (`date()` accepted a datetime string because `datetime` is a `date` subclass); P3 found **D7** (a lone CR in a multiline string produced output that did not round-trip). Both became TDD cycles. Hypothesis shrank D7 to a single character. Limits: 200 examples is a bounded search, not a proof; the strategy generates valid Python data, not arbitrary TOML text; no stateful testing.")
para("**Performance.** 25,000 parse–modify–serialise–reparse operations in five repeats of 5,000 on an Apple M2, Python 3.14.7: **2,385.87 ops/s**, repeat means 2,346.51–2,412.19 ops/s, total 10.478 s; every round-trip assertion passed. This is a throughput baseline, not a concurrent load test (one process, one document shape). A 20–50-user load test remains future work.")
para("**Usability.** A developer-facing heuristic evaluation found one medium and two low issues; error diagnosis was a strength (four invalid inputs each gave a specific exception with line/column).")
bullet("**Medium / consistency:** `Array.insert(0)` on `[1, 2]` renders `[0,1, 2]`; values and reparse are correct. Preserve the separator and add a regression test for `[0, 1, 2]`.")
bullet("**Low / documentation:** index clamping is not documented; add that indexes below 0 clamp to the start and above `len` clamp to the end.")
bullet("**Low / documentation:** `insert`/`append` help does not explain formatting preservation; add short before/after examples.")


# ---------------------------------------------------------------------------
# 12. Exploratory testing
# ---------------------------------------------------------------------------

h1("12. Exploratory Testing")
para("On 25 October 2026 we ran a time-boxed exploratory session with an AI co-pilot. **Charter:** how tomlkit preserves array formatting during insertion, deletion, serialisation and reparsing, focusing on boundary indexes, spacing styles, comments and D8.")
bullet("**Positions:** only insert at 0 on `[1, 2]` produced `[0,1, 2]`; all outputs reparsed correctly.")
bullet("**Spacing styles:** compact `[1,2]`, bracket-spaced `[ 1, 2 ]` and unusual spacing did not reproduce; the conventionally spaced array did.")
bullet("**Multiline/comments:** beginning insertion preserved layout and both inline comments; D8 did not reproduce.")
bullet("**Repetition:** repeated insert at 0 grew the no-space prefix cumulatively.")
bullet("**Deletion:** deleting the inserted values restored the original `[1, 2]` exactly.")
para("**AI co-pilot:** useful for comparing beginning/middle/end and repeating insertion; misleading when it implied permanent damage — test 5 disproved that. AI output is a test idea, not a finding. **Recommendation:** regression test `[1, 2]` + `insert(0, 0)` → `[0, 1, 2]`; keep semantic round-trip assertions. D8 remains open and is pinned by strict xfail K6.")


# ---------------------------------------------------------------------------
# 13. CI/CD and dashboard
# ---------------------------------------------------------------------------

h1("13. CI/CD Pipeline and Quality Dashboard")
para("The fork's GitHub Actions pipeline runs the fast gate on every push/PR: Ruff + mypy; a 3 OS × 3 Python matrix; the 388 AI tests; the 1,507-test hybrid suite in risk order; coverage/RTM gate. Nightly non-blocking jobs run mutation, performance and security checks (pip-audit, bandit). Every run uploads coverage, JUnit, mutation, RTM and dashboard evidence.")
caption("Table 9. Quality gates.")
table(
    ["Gate", "Threshold", "Rationale"],
    [
        ["Statement coverage", "≥87%", "Final 91.6%; above 81.7% AI baseline, with room for variation"],
        ["Branch coverage", "≥82%", "Final 85.6%; above 66.3% AI baseline"],
        ["All tests pass", "1,502 pass, 5 strict xfail", "xfail is explicit/reviewed, not a silent skip"],
        ["RTM references", "All test IDs resolve", "Prevents phantom traceability"],
        ["Mutation (nightly)", "≥75%", "Final 77.4%; just below to catch regression"],
    ],
    [4.5, 4.2, 7.3],
)
para("Thresholds sit just below the achieved scores: a gate at the current score would fail on ordinary refactoring and tempt weaker tests; a gate at the AI baseline would accept the shallow suite. **Mutation is nightly, not blocking**, because a full run takes ~20 minutes and would dominate PR feedback. This is a deliberate trade-off.")
caption("Table 10. Final quality dashboard.")
table(
    ["Indicator", "Value", "Note"],
    [
        ["Statement coverage", "91.6%", "AI baseline 81.7%; gate 87%"],
        ["Branch coverage", "85.6%", "AI baseline 66.3%; gate 82%"],
        ["Mutation score", "77.4%", "AI baseline 57.8%; covered-code 81.3%"],
        ["Defect density", "1.92 / KLOC", "8 defects / 4.158 KLOC"],
        ["RTM completeness", "88%", "14 of 16; R15/R16 open"],
        ["Tests", "1,507", "1,502 passed, 5 strict xfailed"],
    ],
    [4.2, 3.2, 8.6],
)
figure(7, "Final quality dashboard: coverage, mutation, RTM, defect density and suite size.")
para("The Week 13 demo pushes a seeded regression that removes a covered branch; the coverage gate blocks the merge, showing the gate is live.")


# ---------------------------------------------------------------------------
# 14. Reflection
# ---------------------------------------------------------------------------

h1("14. Reflection")
para("**Strengths:** AI produced 388 tests in minutes, 81.7% statement coverage and four of eight defects on the first run; it was good at boilerplate, public-API coverage and exploration ideas. The 1,890 survivors gave us a prioritised test list, and the assertion audit gave us a vocabulary for weak tests.")
para("**Limitations:** the suite was broad but shallow — many tests described current behaviour, not the contract; exact messages, boundaries, combinations and formatting branches were missed. The repair loop is risky: an AI can “fix” a failing test by matching the implementation. D1–D3 stayed defects only because we checked source/docs. AI also misread API names and exception types.")
para("**Ethics/reliability:** AI use is disclosed (Appendix C); every generated test was reviewed; no unreviewed output was submitted; no real PII was used. The main bias risk is over-trusting confident explanations and treating model coverage as completeness. Mitigation is procedural: mutation, independent oracles, human review and explicit xfails.")
para("**Next time:** same-commit AI-only rerun to isolate the group contribution; full 45–60-minute exploratory box; a real 20–50-user load test; earlier equivalent-mutant triage; exact-message and boundary assertions in the prompt from the start.")
para("**Conclusion:** the hybrid suite is measurably stronger than the AI-only baseline, with unit, integration and acceptance evidence and a CI gate that enforces what matters. The headline is 57.8% → 77.4% mutation, but the method matters more: generate fast, measure with mutation, design human tests against the gaps, keep evidence reproducible. AI is a useful first draft; it is not ground truth.")

page_break()


# ---------------------------------------------------------------------------
# Appendices
# ---------------------------------------------------------------------------

h1("Appendices")

h2("Appendix A — Requirements Traceability Matrix")
para("Sources: README, CHANGELOG, docstrings and reverse-engineered code. “Final verification” lists the main evidence.", size=9, italic=True)
caption("Table 11. Full requirements traceability matrix.")
table(
    ["ID", "Requirement", "Source", "AI baseline", "Final verification"],
    [
        ["R01", "Parse any valid TOML 1.1 document into a TOMLDocument with spec types", "README / CHANGELOG", "Covered", "Parser suite; P1; IT4"],
        ["R02", "`parse` then `dumps` on an unmodified document returns the identical string", "README", "Covered", "P2; IT4"],
        ["R03", "Editing changes only the edited value; comments/layout preserved", "README", "Partial", "K6, K10; BDD; IT2"],
        ["R04", "Malformed input raises a ParseError subclass with line/column", "Code", "Partial", "K1–K3; BDD"],
        ["R05", "`dumps` handles Mapping/Table/Container, `sort_keys`, TypeError otherwise", "Docstring / CHANGELOG", "Covered", "K9; IT5"],
        ["R06", "`load`/`dump` work with text and binary file-like objects", "Docstring", "Covered", "IT1"],
        ["R07", "TOMLFile read/write preserves LF, CRLF and mixed endings", "Code", "Covered", "K11; IT2; BDD"],
        ["R08", "`date`/`time`/`datetime` factories return the right type", "Docstring", "Fails (D1)", "C1; P5"],
        ["R09", "`item()` converts supported types, raises ConvertError otherwise, uses encoders", "Docstring", "Covered", "P1; project tests"],
        ["R10", "`string()` escapes and supports literal/multiline forms", "Docstring / spec", "Covered", "P3; C2"],
        ["R11", "Arithmetic on Integer/Float/Date items returns the same kind and keeps trivia", "Code", "Covered", "Project tests"],
        ["R12", "Array editing yields valid, reparseable output; slice assignment rejected", "Docstring / CHANGELOG", "Partial", "K6, K7; IT2"],
        ["R13", "Out-of-order and dotted-key tables can be read, edited and deleted", "README / CHANGELOG", "Partial", "K10; IT3"],
        ["R14", "Comments always produce valid TOML; line breaks split/rejected", "Docstring / CHANGELOG", "Fails (D6)", "C3; K8"],
        ["R15", "`key()` always serialises to a valid, reparseable key", "Docstring / code", "Fails (D5)", "**Open**; strict xfail"],
        ["R16", "Parsing time grows roughly linearly with document size", "CHANGELOG", "Untested", "**Open**; perf baseline only"],
    ],
    [1.0, 6.0, 3.2, 2.6, 3.2],
    size=8,
)
para("R15 and R16 are the two documented gaps: `key([])` is still unparseable, and no large-input scaling test exists. They are reported openly rather than counted as covered.", size=9, italic=True, space_before=3)


h2("Appendix B — Prompt Log, TDD and BDD Evidence")
para("Full prompt log: `tests_ai/PROMPT_LOG.md`. Tool: Claude claude-opus-5-5 via claude.ai, 18 October 2026, target `8c959b5`; the model saw module source and README only.", size=9, italic=True)
caption("Table 12. Prompt log summary.")
table(
    ["Prompt", "Scope"],
    [
        ["P0", "Role/ground rules: pytest only, public API, concrete assertions, parametrise"],
        ["P1", "Public API: parse/loads, dumps/dump/load, item factories, encoders"],
        ["P2", "Parser: keys, strings, numbers, dates, arrays, tables, malformed input"],
        ["P3", "Items: item(), String.from_raw, arithmetic, Array/Table/AoT, keys, comments"],
        ["P4", "Container/document: editing, comments/whitespace, dotted/out-of-order tables, errors"],
        ["P5", "Utilities/errors: parse_rfc3339, escape_string, Source navigation, exception messages"],
        ["P6", "File I/O: TOMLFile read/write, LF/CRLF/mixed endings"],
    ],
    [1.6, 14.4],
)
para("Run 1: 387 collected, 379 passed, 8 failed. Five AI assumptions repaired; three real defects kept as strict xfails (D1–D3). Run 2: 388 collected, 385 passed, 3 xfailed. TDD cycle details are in Table 8; raw outputs are in `week8/tdd_runs/` and `week11/tdd_runs/`. BDD scenarios are in `tests_bdd/features/` and automated by `test_edit_config.py` and `test_backlog.py`.", size=10, space_before=3)


h2("Appendix C — Declaration of AI Tool Use")
para("All AI use is disclosed below. All analysis, root-cause explanations and reflections are the group's own work. Every AI-generated test, finding and code change was reviewed and verified before submission.")
caption("Table 13. AI tools and activities.")
table(
    ["Tool", "Version / access", "Activities"],
    [
        ["Claude (Anthropic)", "claude-opus-5-5 via claude.ai, free tier", "Week 6 baseline suite; `container.py` review; exploratory charters/edge cases; report wording"],
    ],
    [4.2, 5.0, 6.8],
)
para("We confirm that AI output was treated as a draft, not ground truth; that failing tests were not silently changed to match implementation behaviour; and that all reported numbers come from scripts and raw outputs retained in the repository. No real personal data was used.", space_before=4)
para("Signed by all group members:", space_before=10)
table(
    ["Name", "Student ID", "Signature", "Date"],
    [
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "", ""],
    ],
    [5.2, 3.4, 4.6, 2.8],
)
para("Peer-contribution form: submitted individually and confidentially via the separate Blackboard link, as required by Section 9 of the brief.", size=9, italic=True, space_before=8)


OUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUT)
print(f"Wrote {OUT}")
