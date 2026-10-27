#!/usr/bin/env python3
"""Build one PDF evidence pack per week/folder.

Run from the repository root:
    python reports/build_week_pdfs.py

Outputs:
    reports/pdf/week6.pdf ... week12.pdf
    reports/pdf/COMP441_GroupA_Weekly_Evidence.pdf
    reports/pdf/README.md

The packs print the human-readable report and key summaries. Large raw
artefacts (full mutmut output, coverage JSON, HTML coverage, kill matrices)
are listed in each pack's inventory and stay in the repository as evidence;
they are not printed page-for-page.
"""

from __future__ import annotations

import csv
import json
import re
import textwrap
from datetime import date
from pathlib import Path

from markdown_it import MarkdownIt
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    LongTable,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    XPreformatted,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "pdf"

NAVY = colors.HexColor("#1F3864")
GREY = colors.HexColor("#595959")
LIGHT_GREY = colors.HexColor("#F2F2F2")
GRID = colors.HexColor("#BFBFBF")
GOLD = colors.HexColor("#C9A227")
CODE_BG = colors.HexColor("#F7F7F7")

PAGE_W, PAGE_H = A4
MARGIN = 1.8 * cm
CONTENT_W = PAGE_W - 2 * MARGIN


# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

def _register_fonts() -> tuple[str, str, str, str, str, str]:
    """Register Arial/Courier from Windows, fall back to Type 1 fonts."""
    font_dir = Path("C:/Windows/Fonts")
    candidates = {
        "Arial": font_dir / "arial.ttf",
        "Arial-Bold": font_dir / "arialbd.ttf",
        "Arial-Italic": font_dir / "ariali.ttf",
        "Arial-BoldItalic": font_dir / "arialbi.ttf",
        "Courier": font_dir / "cour.ttf",
        "Courier-Bold": font_dir / "courbd.ttf",
    }
    if all(p.exists() for p in candidates.values()):
        for name, path in candidates.items():
            pdfmetrics.registerFont(TTFont(name, str(path)))
        pdfmetrics.registerFontFamily(
            "Arial",
            normal="Arial",
            bold="Arial-Bold",
            italic="Arial-Italic",
            boldItalic="Arial-BoldItalic",
        )
        return "Arial", "Arial-Bold", "Arial-Italic", "Arial-BoldItalic", "Courier", "Courier-Bold"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique", "Courier", "Courier-Bold"


BODY, BOLD, ITALIC, BOLD_ITALIC, CODE, CODE_BOLD = _register_fonts()


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

STYLES = {
    "cover_kicker": ParagraphStyle(
        "CoverKicker", fontName=BOLD, fontSize=10.5, leading=14, textColor=colors.white
    ),
    "cover_title": ParagraphStyle(
        "CoverTitle", fontName=BOLD, fontSize=19, leading=23, textColor=colors.white
    ),
    "cover_sub": ParagraphStyle(
        "CoverSub", fontName=BODY, fontSize=10.5, leading=14, textColor=colors.HexColor("#D9E2F3")
    ),
    "toc_title": ParagraphStyle(
        "TOCTitle", fontName=BOLD, fontSize=18, leading=22, textColor=NAVY, spaceAfter=12
    ),
    "h1": ParagraphStyle(
        "H1", fontName=BOLD, fontSize=15, leading=19, textColor=NAVY, spaceBefore=10, spaceAfter=4,
        keepWithNext=True,
    ),
    "h2": ParagraphStyle(
        "H2", fontName=BOLD, fontSize=12, leading=15, textColor=NAVY, spaceBefore=8, spaceAfter=3,
        keepWithNext=True,
    ),
    "h3": ParagraphStyle(
        "H3", fontName=BOLD, fontSize=10.5, leading=13, textColor=colors.HexColor("#2F5597"),
        spaceBefore=6, spaceAfter=2, keepWithNext=True,
    ),
    "body": ParagraphStyle(
        "Body", fontName=BODY, fontSize=9.5, leading=13, textColor=colors.HexColor("#1A1A1A"),
        spaceAfter=5, splitLongWords=1,
    ),
    "body_tight": ParagraphStyle(
        "BodyTight", fontName=BODY, fontSize=9.5, leading=12.5, textColor=colors.HexColor("#1A1A1A"),
        spaceAfter=2, splitLongWords=1,
    ),
    "bullet": ParagraphStyle(
        "Bullet", fontName=BODY, fontSize=9.5, leading=12.5, textColor=colors.HexColor("#1A1A1A"),
        leftIndent=12, bulletIndent=0, spaceAfter=2, splitLongWords=1,
    ),
    "quote": ParagraphStyle(
        "Quote", fontName=ITALIC, fontSize=9.2, leading=12.5, textColor=colors.HexColor("#404040"),
        leftIndent=14, rightIndent=6, spaceAfter=4, borderPadding=3,
    ),
    "code": ParagraphStyle(
        "Code", fontName=CODE, fontSize=7.2, leading=9, textColor=colors.HexColor("#202020"),
        backColor=CODE_BG, borderColor=colors.HexColor("#DDDDDD"), borderWidth=0.4,
        borderPadding=4, spaceBefore=2, spaceAfter=6, splitLongWords=1,
    ),
    "source": ParagraphStyle(
        "Source", fontName=ITALIC, fontSize=7.8, leading=10, textColor=colors.HexColor("#777777"),
        spaceBefore=2, spaceAfter=3,
    ),
    "note": ParagraphStyle(
        "Note", fontName=BODY, fontSize=8.8, leading=12, textColor=colors.HexColor("#333333"),
        backColor=colors.HexColor("#FFF8E1"), borderColor=GOLD, borderWidth=0.6,
        borderPadding=5, spaceBefore=4, spaceAfter=7,
    ),
    "caption": ParagraphStyle(
        "Caption", fontName=ITALIC, fontSize=7.8, leading=10, textColor=GREY, spaceAfter=3
    ),
    "cell": ParagraphStyle(
        "Cell", fontName=BODY, fontSize=7.2, leading=8.8, textColor=colors.HexColor("#1A1A1A"),
        splitLongWords=1,
    ),
    "cell_header": ParagraphStyle(
        "CellHeader", fontName=BOLD, fontSize=7.2, leading=8.8, textColor=colors.white,
        splitLongWords=1,
    ),
}

TOC_H1 = ParagraphStyle(
    "TOCH1", fontName=BOLD, fontSize=9.5, leading=13, textColor=NAVY, spaceBefore=3
)
TOC_H2 = ParagraphStyle(
    "TOCH2", fontName=BODY, fontSize=8.5, leading=11, textColor=colors.HexColor("#333333"),
    leftIndent=12,
)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def clean_text(value: str) -> str:
    """Repair common mojibake and remove control characters."""
    text = str(value)
    replacements = {
        "\ufffd+'": "→",
        "\ufffd": "",
        "â€“": "–",
        "â€”": "—",
        "â€™": "'",
        "â€œ": '"',
        "â€\x9d": '"',
        "â€": '"',
        "Â": "",
        "\x00": "",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


def read_text(path: Path) -> str:
    return clean_text(path.read_text(encoding="utf-8", errors="replace"))


def escape_xml(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def inline_html(children) -> str:
    """Convert markdown-it inline children to ReportLab mini-HTML."""
    out: list[str] = []
    for child in children or []:
        kind = child.type
        if kind == "text":
            out.append(escape_xml(clean_text(child.content)))
        elif kind == "softbreak":
            out.append(" ")
        elif kind == "hardbreak":
            out.append("<br/>")
        elif kind == "strong_open":
            out.append("<b>")
        elif kind == "strong_close":
            out.append("</b>")
        elif kind == "em_open":
            out.append("<i>")
        elif kind == "em_close":
            out.append("</i>")
        elif kind == "s_open":
            out.append("<strike>")
        elif kind == "s_close":
            out.append("</strike>")
        elif kind == "code_inline":
            out.append(
                f'<font face="{CODE}" size="8" color="#8B1A1A">'
                f"{escape_xml(clean_text(child.content))}</font>"
            )
        elif kind == "link_open":
            href = escape_xml(child.attrGet("href") or "")
            out.append(f'<link href="{href}" color="#1F3864">')
        elif kind == "link_close":
            out.append("</link>")
        elif kind == "image":
            alt = escape_xml(clean_text(child.content or "image"))
            out.append(f"[image: {alt}]")
        elif kind == "html_inline":
            raw = (child.content or "").strip().lower()
            if raw in {"<br>", "<br/>", "<br />"}:
                out.append("<br/>")
            else:
                out.append(escape_xml(clean_text(child.content or "")))
        else:
            if child.content:
                out.append(escape_xml(clean_text(child.content)))
    return "".join(out)


def cell_html(value: str) -> str:
    text = escape_xml(clean_text(value))
    text = re.sub(r"`([^`]+)`", rf'<font face="{CODE}" size="7">\1</font>', text)
    return text.replace("\n", "<br/>")


def wrap_code(text: str, width: int = 120) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        if len(line) <= width:
            lines.append(line)
            continue
        indent = len(line) - len(line.lstrip(" "))
        for start in range(0, len(line), width):
            chunk = line[start : start + width]
            if start:
                chunk = " " * min(indent, 10) + chunk
            lines.append(chunk)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# PDF document
# ---------------------------------------------------------------------------

class WeekDoc(BaseDocTemplate):
    def __init__(self, filename: str, week_label: str, **kwargs):
        super().__init__(filename, **kwargs)
        self.week_label = week_label
        self._heading_seq = 0
        self._last_outline_level = -1
        frame = Frame(MARGIN, MARGIN, CONTENT_W, PAGE_H - 2 * MARGIN, id="body")
        self.addPageTemplates(
            [
                PageTemplate(id="cover", frames=[frame], onPage=self._on_cover),
                PageTemplate(id="later", frames=[frame], onPage=self._on_later),
            ]
        )

    def _on_cover(self, canv: canvas.Canvas, doc) -> None:
        canv.saveState()
        canv.setFillColor(NAVY)
        canv.rect(0, PAGE_H - 6.4 * cm, PAGE_W, 6.4 * cm, fill=1, stroke=0)
        canv.setFillColor(GOLD)
        canv.rect(0, PAGE_H - 6.52 * cm, PAGE_W, 0.12 * cm, fill=1, stroke=0)
        canv.restoreState()

    def _on_later(self, canv: canvas.Canvas, doc) -> None:
        canv.saveState()
        canv.setFont(BODY, 8)
        canv.setFillColor(GREY)
        canv.drawString(MARGIN, PAGE_H - 1.15 * cm, f"COMP 441 Group A  ·  {self.week_label}")
        canv.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.15 * cm, "Weekly evidence pack")
        canv.setStrokeColor(colors.HexColor("#D0D0D0"))
        canv.setLineWidth(0.4)
        canv.line(MARGIN, PAGE_H - 1.35 * cm, PAGE_W - MARGIN, PAGE_H - 1.35 * cm)
        canv.drawString(MARGIN, 1.05 * cm, "github.com/the-dezeray/tomlkit")
        canv.restoreState()

    def afterFlowable(self, flowable) -> None:
        if not isinstance(flowable, Paragraph):
            return
        style = flowable.style.name
        if style not in {"H1", "H2"}:
            return
        text = flowable.getPlainText()
        level = 0 if style == "H1" else 1
        self.notify("TOCEntry", (level, text, self.page))
        key = f"h{self._heading_seq}"
        self._heading_seq += 1
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=0, closed=False)


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict] = []

    def showPage(self):  # noqa: N802
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if self._pageNumber > 1:
                self.setFont(BODY, 8)
                self.setFillColor(GREY)
                self.drawRightString(PAGE_W - MARGIN, 1.05 * cm, f"Page {self._pageNumber} of {total}")
            super().showPage()
        super().save()


# ---------------------------------------------------------------------------
# Markdown renderer
# ---------------------------------------------------------------------------

class MarkdownRenderer:
    def __init__(self, story: list, width: float):
        self.story = story
        self.width = width
        self.md = MarkdownIt("commonmark", {"html": False}).enable("table").enable("strikethrough")
        self.list_stack: list[dict] = []
        self.in_item = False
        self.item_parts: list[str] = []
        self.quote_depth = 0
        self.table_header: list[str] = []
        self.table_rows: list[list[str]] = []
        self.table_row: list[str] = []
        self.table_cell: list[str] = []
        self.in_table = False
        self.in_thead = False
        self.in_cell = False
        self._heading_level: int | None = None
        self._heading_parts: list[str] = []
        self._paragraph_parts: list[str] = []

    def render(self, text: str, source: str) -> None:
        self.story.append(Paragraph(f"Source: {escape_xml(source)}", STYLES["source"]))
        tokens = self.md.parse(text)
        has_heading = any(t.type == "heading_open" for t in tokens)
        if not has_heading:
            self.story.append(Paragraph(escape_xml(source), STYLES["h2"]))
        for token in tokens:
            self._handle(token)

    # -- token handling -----------------------------------------------------

    def _handle(self, token) -> None:
        kind = token.type
        if kind == "heading_open":
            self._heading_level = int(token.tag[1])
            self._heading_parts = []
        elif kind == "heading_close":
            level = self._heading_level or 2
            style = {1: "h1", 2: "h2"}.get(level, "h3")
            heading_html = "".join(self._heading_parts).strip()
            if heading_html:
                self.story.append(Paragraph(heading_html, STYLES[style]))
            self._heading_level = None
            self._heading_parts = []
        elif kind == "inline":
            html = inline_html(token.children)
            if self._heading_level is not None:
                self._heading_parts.append(html)
            elif self.in_cell:
                self.table_cell.append(html)
            elif self.in_item:
                self.item_parts.append(html)
            elif self.in_table:
                self.table_cell.append(html)
            else:
                self._paragraph_parts.append(html)
        elif kind == "paragraph_open":
            self._paragraph_parts: list[str] = []
        elif kind == "paragraph_close":
            html = "".join(self._paragraph_parts).strip()
            if html:
                if self.in_item:
                    self.item_parts.append(html)
                elif self.quote_depth:
                    self.story.append(Paragraph(html, STYLES["quote"]))
                else:
                    self.story.append(Paragraph(html, STYLES["body"]))
        elif kind in {"bullet_list_open", "ordered_list_open"}:
            ordered = kind == "ordered_list_open"
            start = 1
            if ordered:
                raw = token.attrGet("start")
                start = int(raw) if raw and str(raw).isdigit() else 1
            self.list_stack.append({"ordered": ordered, "counter": start - 1, "depth": len(self.list_stack)})
        elif kind in {"bullet_list_close", "ordered_list_close"}:
            if self.list_stack:
                self.list_stack.pop()
        elif kind == "list_item_open":
            self.in_item = True
            self.item_parts = []
        elif kind == "list_item_close":
            html = " ".join(p for p in self.item_parts if p).strip()
            if html:
                if self.list_stack:
                    item = self.list_stack[-1]
                    depth = item["depth"]
                    if item["ordered"]:
                        item["counter"] += 1
                        bullet = f"{item['counter']}."
                    else:
                        bullet = "•"
                    style = ParagraphStyle(
                        f"List{depth}",
                        parent=STYLES["bullet"],
                        leftIndent=12 + depth * 14,
                        bulletIndent=depth * 14,
                    )
                    self.story.append(Paragraph(html, style, bulletText=bullet))
            self.in_item = False
            self.item_parts = []
        elif kind == "blockquote_open":
            self.quote_depth += 1
        elif kind == "blockquote_close":
            self.quote_depth = max(0, self.quote_depth - 1)
        elif kind in {"fence", "code_block"}:
            code = clean_text(token.content).rstrip("\n")
            if code:
                self.story.append(XPreformatted(escape_xml(wrap_code(code)), STYLES["code"]))
        elif kind == "hr":
            self.story.append(HRFlowable(width="100%", thickness=0.5, color=GRID, spaceBefore=5, spaceAfter=5))
        elif kind == "table_open":
            self.in_table = True
            self.table_header = []
            self.table_rows = []
        elif kind == "thead_open":
            self.in_thead = True
        elif kind == "thead_close":
            self.in_thead = False
        elif kind == "tbody_open":
            self.in_thead = False
        elif kind == "tr_open":
            self.table_row = []
        elif kind == "tr_close":
            if self.in_thead:
                self.table_header = self.table_row
            else:
                self.table_rows.append(self.table_row)
            self.table_row = []
        elif kind in {"th_open", "td_open"}:
            self.in_cell = True
            self.table_cell = []
        elif kind in {"th_close", "td_close"}:
            self.table_row.append("".join(self.table_cell).strip())
            self.in_cell = False
            self.table_cell = []
        elif kind == "table_close":
            self.in_table = False
            self._emit_table()
        elif kind == "html_block":
            pass
        elif kind == "footnote_block_open":
            pass

    def _emit_table(self) -> None:
        header = self.table_header or []
        rows = self.table_rows or []
        ncols = max([len(header)] + [len(r) for r in rows] + [0])
        if ncols == 0:
            return
        header = header + [""] * (ncols - len(header))
        rows = [r + [""] * (ncols - len(r)) for r in rows]
        if not header:
            header = [""] * ncols
        self.story.append(make_table(header, rows, self.width))


# ---------------------------------------------------------------------------
# Table helpers
# ---------------------------------------------------------------------------

def make_table(
    header: list[str],
    rows: list[list[str]],
    width: float,
    font_size: float = 7.2,
    raw_html: bool = True,
    max_rows: int | None = None,
) -> LongTable:
    total_rows = len(rows)
    if max_rows is not None and total_rows > max_rows:
        rows = rows[:max_rows]
    ncols = max(1, len(header))
    data: list[list] = []
    head_style = ParagraphStyle(
        "HeaderCell", parent=STYLES["cell_header"], fontSize=font_size, leading=font_size + 1.6
    )
    body_style = ParagraphStyle(
        "BodyCell", parent=STYLES["cell"], fontSize=font_size, leading=font_size + 1.6
    )
    data.append([Paragraph(cell if raw_html else cell_html(cell), head_style) for cell in header])
    for row in rows:
        data.append(
            [Paragraph(cell if raw_html else cell_html(cell), body_style) for cell in row]
        )

    # Content-weighted column widths with a guaranteed minimum so headers do
    # not collapse into one-character columns on wide tables.
    weights: list[float] = []
    for i in range(ncols):
        lengths = [len(strip_tags(header[i]))]
        lengths += [len(strip_tags(r[i])) for r in rows[:40]]
        weights.append(max(1.0, min(float(max(lengths)), 60.0)))
    min_w = min(1.2 * cm, width / max(ncols, 1) * 0.55)
    available = max(width - ncols * min_w, 0.1 * cm)
    total = sum(weights) or 1.0
    widths = [min_w + available * w / total for w in weights]

    table = LongTable(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.35, GRID),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FB")]),
            ]
        )
    )
    if max_rows is not None and total_rows > max_rows:
        # The caller adds the truncation note; keep the table itself clean.
        pass
    return table


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def add_heading(story: list, text: str, style: str = "h2") -> None:
    story.append(Paragraph(escape_xml(text), STYLES[style]))


def add_text_section(story: list, path: Path, title: str, max_lines: int | None = None) -> None:
    add_heading(story, title)
    story.append(Paragraph(f"Source: {escape_xml(str(path.relative_to(ROOT)))}", STYLES["source"]))
    text = read_text(path)
    lines = text.splitlines()
    truncated = False
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        truncated = True
    body = "\n".join(lines).rstrip()
    if body:
        story.append(XPreformatted(escape_xml(wrap_code(body)), STYLES["code"]))
    if truncated:
        story.append(
            Paragraph(
                f"Showing the first {max_lines} of {len(text.splitlines())} lines. "
                f"Full file: <font face='{CODE}'>{escape_xml(str(path.relative_to(ROOT)))}</font>.",
                STYLES["caption"],
            )
        )


def add_code_section(story: list, path: Path, title: str, max_lines: int | None = None) -> None:
    add_text_section(story, path, title, max_lines=max_lines)


def add_csv_section(
    story: list,
    path: Path,
    title: str,
    max_rows: int | None = None,
    font_size: float = 7.2,
) -> None:
    add_heading(story, title)
    story.append(Paragraph(f"Source: {escape_xml(str(path.relative_to(ROOT)))}", STYLES["source"]))
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        story.append(Paragraph("(empty file)", STYLES["caption"]))
        return
    header, body = rows[0], rows[1:]
    total = len(body)
    shown = body[:max_rows] if max_rows else body
    story.append(make_table(header, shown, CONTENT_W, font_size=font_size, raw_html=False))
    if max_rows and total > max_rows:
        story.append(
            Paragraph(
                f"Showing the first {max_rows} of {total} rows. Full file: "
                f"<font face='{CODE}'>{escape_xml(str(path.relative_to(ROOT)))}</font>.",
                STYLES["caption"],
            )
        )


def add_csv_summary(story: list, path: Path, title: str, column: str) -> None:
    add_heading(story, title)
    story.append(Paragraph(f"Source: {escape_xml(str(path.relative_to(ROOT)))}", STYLES["source"]))
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        rows = list(csv.DictReader(handle))
    counts: dict[str, int] = {}
    for row in rows:
        key = clean_text(row.get(column, "") or "(blank)")
        counts[key] = counts.get(key, 0) + 1
    total = len(rows)
    data = [["Value", "Count", "Share"]]
    for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        data.append([key, str(count), f"{100 * count / total:.1f}%"])
    data.append(["**Total**", f"**{total}**", "**100.0%**"])
    story.append(make_table(data[0], data[1:], CONTENT_W, font_size=8.0, raw_html=False))
    story.append(Paragraph(f"{total} rows summarised by `{column}`.", STYLES["caption"]))


def add_coverage_summary(story: list, path: Path, title: str) -> None:
    add_heading(story, title)
    story.append(Paragraph(f"Source: {escape_xml(str(path.relative_to(ROOT)))}", STYLES["source"]))
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    totals = data.get("totals", {})
    rows = [
        ["Metric", "Value"],
        ["Statements", f"{totals.get('covered_lines', 0):,} / {totals.get('num_statements', 0):,}"],
        ["Statement coverage", f"{totals.get('percent_statements_covered', 0):.2f}%"],
        ["Branches", f"{totals.get('covered_branches', 0):,} / {totals.get('num_branches', 0):,}"],
        ["Branch coverage", f"{totals.get('percent_branches_covered', 0):.2f}%"],
        ["Combined coverage", f"{totals.get('percent_covered', 0):.2f}%"],
        ["Excluded lines", f"{totals.get('excluded_lines', 0):,}"],
    ]
    story.append(make_table(rows[0], rows[1:], CONTENT_W, font_size=8.5, raw_html=False))


def add_mutation_summary(story: list, path: Path, title: str) -> None:
    add_heading(story, title)
    story.append(Paragraph(f"Source: {escape_xml(str(path.relative_to(ROOT)))}", STYLES["source"]))
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    rows: list[list[str]] = []
    for module, stats in data.items():
        rows.append(
            [
                module,
                f"{stats.get('total', 0):,}",
                f"{stats.get('killed', 0):,}",
                f"{stats.get('timeout', 0):,}",
                f"{stats.get('survived', 0):,}",
                f"{stats.get('no_tests', 0):,}",
                f"{stats.get('score', 0):.1f}%",
                f"{stats.get('covered_score', 0):.1f}%",
            ]
        )
    header = ["Module", "Total", "Killed", "Timeout", "Survived", "No tests", "Score", "Covered"]
    story.append(make_table(header, rows, CONTENT_W, font_size=7.6, raw_html=False))


def add_json_table(story: list, path: Path, title: str) -> None:
    add_heading(story, title)
    story.append(Paragraph(f"Source: {escape_xml(str(path.relative_to(ROOT)))}", STYLES["source"]))
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    if isinstance(data, dict):
        rows = [[clean_text(str(k)), clean_text(str(v))] for k, v in data.items()]
        story.append(make_table(["Key", "Value"], rows, CONTENT_W, font_size=8.0, raw_html=False))
    else:
        story.append(XPreformatted(escape_xml(wrap_code(json.dumps(data, indent=2))), STYLES["code"]))


def add_json_code(story: list, path: Path, title: str, max_lines: int = 80) -> None:
    add_heading(story, title)
    story.append(Paragraph(f"Source: {escape_xml(str(path.relative_to(ROOT)))}", STYLES["source"]))
    text = json.dumps(json.loads(path.read_text(encoding="utf-8", errors="replace")), indent=2)
    lines = text.splitlines()
    truncated = len(lines) > max_lines
    if truncated:
        lines = lines[:max_lines]
    story.append(XPreformatted(escape_xml(wrap_code("\n".join(lines))), STYLES["code"]))
    if truncated:
        story.append(
            Paragraph(
                f"Showing the first {max_lines} lines of the JSON file. Full file: "
                f"<font face='{CODE}'>{escape_xml(str(path.relative_to(ROOT)))}</font>.",
                STYLES["caption"],
            )
        )


def add_image(story: list, path: Path, title: str) -> None:
    from PIL import Image as PILImage

    with PILImage.open(path) as img:
        px_w, px_h = img.size
    max_w = CONTENT_W
    max_h = 18 * cm
    ratio = min(max_w / px_w, max_h / px_h)
    parts = [
        Paragraph(escape_xml(title), STYLES["h2"]),
        Paragraph(f"Source: {escape_xml(str(path.relative_to(ROOT)))}", STYLES["source"]),
        Image(str(path), width=px_w * ratio, height=px_h * ratio),
        Paragraph(path.name, STYLES["caption"]),
    ]
    story.append(KeepTogether(parts))


def add_note(story: list, text: str) -> None:
    story.append(Paragraph(text, STYLES["note"]))


def add_source_inventory(story: list, folder: Path) -> None:
    add_heading(story, "Raw evidence inventory", "h2")
    story.append(
        Paragraph(
            "The pack prints the readable report and key summaries. Large raw artefacts are "
            "kept in the repository and listed here so a marker can verify them without paging "
            "through thousands of lines. Items tagged <b>[AI-only]</b> are deliberately not "
            "printed: they are the AI baseline's raw output, not the final hybrid result.",
            STYLES["body"],
        )
    )
    rows: list[list[str]] = []
    if folder.exists():
        for path in sorted(folder.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT)
            if any(part in {"__pycache__", ".pytest_cache", "htmlcov_ai"} for part in path.parts):
                continue
            size = path.stat().st_size
            human = f"{size / 1024:.0f} KB" if size >= 1024 else f"{size} B"
            tag = ""
            name = path.name.lower()
            if "cov_ai" in name or "tests_ai" in str(rel).lower() or "htmlcov_ai" in str(rel).lower():
                tag = "[AI-only]"
            elif "v1" in name or "mutmut_results_v1" in name:
                tag = "[v1 baseline]"
            rows.append([str(rel), human, tag])
    if rows:
        story.append(make_table(["File", "Size", "Tag"], rows, CONTENT_W, font_size=6.8, raw_html=False))
    else:
        story.append(Paragraph("(No files found.)", STYLES["caption"]))


# ---------------------------------------------------------------------------
# Week definitions
# ---------------------------------------------------------------------------

WEEKS: list[dict] = [
    {
        "key": "week6",
        "label": "Week 6",
        "title": "AI Baseline, Coverage and Static Analysis",
        "folder": "week6",
        "commit": "8c959b5",
        "sections": [
            ("md", "week6/README.md", None),
            ("csv", "week6/rtm/rtm_week6.csv", "Requirements traceability matrix (R01–R16)", None, 6.2),
            ("text", "week6/radon_cc.txt", "Radon cyclomatic complexity (rank C and above)", 200),
            ("text", "week6/radon_mi.txt", "Radon maintainability index", 100),
            ("text", "week6/pylint.txt", "Pylint output", 100),
            ("text", "week6/symbolic/crosshair_output.txt", "CrossHair symbolic-execution counterexample", 40),
            ("code", "week6/symbolic/ch_date.py", "CrossHair contract"),
            ("summary_csv", "week6/assertion_audit.csv", "Assertion audit summary", "verdict"),
            ("coverage", "week6/cov_ai.json", "AI-only coverage summary"),
            ("coverage", "week6/cov_existing.json", "Maintainers' existing coverage summary"),
            ("text", "week6/rtm/ai_test_ids.txt", "AI test IDs used by the RTM", 25),
            ("note", None, "The AI-only HTML coverage report is in <font face='Courier'>week6/htmlcov_ai/</font>; the raw JSON is <font face='Courier'>week6/cov_ai.json</font>. These are evidence, not printed page-for-page."),
        ],
    },
    {
        "key": "week7",
        "label": "Week 7",
        "title": "Mutation Testing v1 and Risk-Based Prioritisation",
        "folder": "week7",
        "commit": "8c959b5",
        "sections": [
            ("md", "week7/README.md", None),
            ("mutation", "week7/mutation_v1_summary.json", "Mutation v1 summary by module"),
            ("csv", "week7/detection_curve.csv", "Detection curve (risk-based order)", None, 7.6),
            ("json_table", "week7/prioritisation_eval.json", "Prioritisation evaluation (APFD)"),
            ("csv", "week7/priority_order.csv", "Risk-based test order (first 20 tests)", 20, 6.8),
            ("summary_csv", "week7/survivor_categories_v1.csv", "Survivor categories", "category"),
            ("text", "week7/collection_order.txt", "Pytest collection order (first 20 tests)", 20),
            ("text", "week7/durations_ai.txt", "AI test durations (first 20 lines)", 20),
            ("note", None, "The full 5,389-line mutmut output is <font face='Courier'>week7/mutmut_results_v1.txt</font>; the 300-mutant kill matrix is <font face='Courier'>week7/kill_matrix.json</font>. The original Week 7 PDF report is <font face='Courier'>week7/mutation-testing-report-v1.pdf</font>; it is kept as a raw artifact and is not appended here because it duplicates this README and uses legacy font encoding."),
        ],
    },
    {
        "key": "week8",
        "label": "Week 8",
        "title": "TDD Cycles and BDD Acceptance Scenarios",
        "folder": "week8",
        "commit": "a4f54db / a38a3d8 / c829a38",
        "sections": [
            ("md", "week8/TDD_LOG.md", None),
            ("text", "week8/tdd_runs/c1_red.txt", "C1 red — date() accepts datetime strings", 80),
            ("text", "week8/tdd_runs/c1_green.txt", "C1 green", 20),
            ("text", "week8/tdd_runs/c1_refactor.txt", "C1 refactor", 20),
            ("text", "week8/tdd_runs/c2_red.txt", "C2 red — bare CR in multiline strings", 80),
            ("text", "week8/tdd_runs/c2_green.txt", "C2 green", 20),
            ("text", "week8/tdd_runs/c2_refactor.txt", "C2 refactor", 20),
            ("text", "week8/tdd_runs/c3_red.txt", "C3 red — comment() with a bare CR", 80),
            ("text", "week8/tdd_runs/c3_green.txt", "C3 green", 20),
            ("text", "week8/tdd_runs/c3_refactor.txt", "C3 refactor", 20),
            ("code", "tests_bdd/features/edit_config.feature", "BDD feature — edit config and preserve layout"),
            ("code", "tests_bdd/features/backlog.feature", "BDD feature — backlog scenarios"),
            ("note", None, "The BDD step implementations are <font face='Courier'>tests_bdd/test_edit_config.py</font> and <font face='Courier'>tests_bdd/test_backlog.py</font>. The full red/green/refactor logs are in <font face='Courier'>week8/tdd_runs/</font>."),
        ],
    },
    {
        "key": "week9",
        "label": "Week 9",
        "title": "Performance, Usability and Exploratory Testing",
        "folder": "docs/week9",
        "commit": "see source report",
        "sections": [
            ("md", "docs/week9/performance_usability_report.md", None),
            ("md", "docs/week9/exploratory_session_report.md", None),
            ("text", "docs/week9/performance_environment.txt", "Performance environment", 40),
            ("text", "docs/week9/performance_results.txt", "Performance results", 80),
            ("text", "docs/week9/usability_error_check.txt", "Usability check — error diagnosis", 60),
            ("text", "docs/week9/usability_insert_check.txt", "Usability check — insertion at index 0", 60),
            ("text", "docs/week9/usability_modification_check.txt", "Usability check — modification", 60),
            ("text", "docs/week9/usability_help_check.txt", "Usability check — help/documentation", 60),
            ("text", "docs/week9/usability_api_misuse_check.txt", "Usability check — API misuse", 60),
            ("code", "docs/week9/performance_check.py", "Performance harness"),
        ],
    },
    {
        "key": "week10",
        "label": "Week 10",
        "title": "Metrics, Defect Density and RTM Completeness",
        "folder": "reports/week10",
        "commit": "6b8884f",
        "sections": [
            ("md", "reports/week10/metrics_log.md", None),
            ("note", None, "<b>Snapshot notice:</b> Week 10 is an intermediate measurement. The final, authoritative numbers are in the final report §7 and <font face='Courier'>week11/mutation_v2/</font>. Where Week 10 differs (for example coverage 89.4/84.2 and v1 mutation 62.0% with timeouts excluded), the difference is scope or formula, not a correction."),
            ("csv", "reports/week10/dashboard.csv", "Week 10 dashboard", None, 7.2),
            ("coverage", "reports/week10/coverage.json", "Week 10 coverage summary (tests/ only)"),
            ("csv", "reports/defects.csv", "Consolidated defect log (final)", None, 6.8),
        ],
    },
    {
        "key": "week11",
        "label": "Week 11",
        "title": "Mutation v2, TDD and Property-Based Testing",
        "folder": "week11",
        "commit": "6b8884f",
        "sections": [
            ("md", "week11/README.md", None),
            ("md", "week11/TDD_LOG.md", None),
            ("md", "week11/mutation_v2/mutation_v2_report.md", None),
            ("mutation", "week11/mutation_v2/mutation_v2_summary.json", "Mutation v2 summary by module"),
            ("csv", "week11/mutation_v2/v1_vs_v2.csv", "Mutation v1 vs v2 by module", None, 7.6),
            ("image", "week11/mutation_v2/v1_vs_v2.png", "Mutation v1 vs v2 chart"),
            ("md", "week11/mutation_v2/survivor_rootcause_v2.md", None),
            ("md", "week11/property/PROPERTY_CHECKPOINT.md", None),
            ("text", "week11/full_suite.txt", "Final suite result", 80),
            ("text", "week11/property/pytest_property.txt", "Property-test result", 80),
            ("text", "week11/mutation_v2/selected_diffs.txt", "Selected survivor diffs", 120),
            ("md", "week11/mutation_v2/README.md", None),
            ("text", "week11/tdd_runs/c1_red.txt", "TDD C1 red", 80),
            ("text", "week11/tdd_runs/c1_green.txt", "TDD C1 green", 20),
            ("text", "week11/tdd_runs/c1_refactor.txt", "TDD C1 refactor", 20),
            ("text", "week11/tdd_runs/c2_red.txt", "TDD C2 red", 80),
            ("text", "week11/tdd_runs/c2_green.txt", "TDD C2 green", 20),
            ("text", "week11/tdd_runs/c2_refactor.txt", "TDD C2 refactor", 20),
            ("text", "week11/tdd_runs/c3_red.txt", "TDD C3 red", 80),
            ("text", "week11/tdd_runs/c3_green.txt", "TDD C3 green", 20),
            ("text", "week11/tdd_runs/c3_refactor.txt", "TDD C3 refactor", 20),
            ("note", None, "The full 5,389-line v2 mutmut output is <font face='Courier'>week11/mutation_v2/mutmut_results_v2.txt</font>; survivor lists are <font face='Courier'>survivors_v2.txt</font> and <font face='Courier'>survivors_v1_v2.csv</font>. The chart workbook is <font face='Courier'>week11/Week11_TrackD_Findings.xlsx</font>."),
        ],
    },
    {
        "key": "week12",
        "label": "Week 12",
        "title": "CI/CD Pipeline, Quality Gates and Final Evidence",
        "folder": "reports/week12",
        "commit": "30ad2f0 / 524355a",
        "sections": [
            ("md", "reports/week12/ci-evidence.md", None),
            ("md", "docs/ci-cd.md", None),
            ("md", "docs/ci-cd-demo.md", None),
            ("code", ".github/workflows/ci.yml", "CI workflow definition", 160),
            ("csv", "reports/defects.csv", "Consolidated defect log (final)", None, 6.8),
            ("note", None, "The green run is GitHub Actions run <font face='Courier'>40412867639</font>. Download artefacts with <font face='Courier'>gh run download 40412867639 -n dashboard</font>, replacing <font face='Courier'>dashboard</font> with the artifact name. The workflow file is printed above; the full file is <font face='Courier'>.github/workflows/ci.yml</font>."),
        ],
    },
]


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_week(week: dict) -> Path:
    label = week["label"]
    title = week["title"]
    folder = ROOT / week["folder"]
    out_path = OUT_DIR / f"{week['key']}.pdf"

    doc = WeekDoc(
        str(out_path),
        label,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title=f"COMP 441 Group A — {label}: {title}",
        author="COMP 441 Group A",
        subject="AI-Augmented Test Suite — weekly evidence pack",
    )

    story: list = []
    # Cover
    story.append(Spacer(1, 0.95 * cm))
    story.append(Paragraph("COMP 441 — Software Analysis and Testing", STYLES["cover_kicker"]))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(f"{label} — {escape_xml(title)}", STYLES["cover_title"]))
    story.append(Spacer(1, 0.18 * cm))
    story.append(Paragraph("Group A  ·  Track D  ·  TOML Kit", STYLES["cover_sub"]))
    story.append(Spacer(1, 2.55 * cm))

    meta_rows = [
        ["Period", label],
        ["Evidence folder", week["folder"]],
        ["Repository", "github.com/the-dezeray/tomlkit"],
        ["Commit(s)", week["commit"]],
        ["Generated", date.today().isoformat()],
        ["Contents", f"{len(week['sections'])} sections"],
    ]
    meta = Table(
        [[Paragraph(f"<b>{escape_xml(a)}</b>", STYLES["body"]), Paragraph(escape_xml(b), STYLES["body"])] for a, b in meta_rows],
        colWidths=[3.6 * cm, CONTENT_W - 3.6 * cm],
        hAlign="LEFT",
    )
    meta.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#E0E0E0")),
            ]
        )
    )
    story.append(meta)
    story.append(Spacer(1, 0.6 * cm))
    story.append(
        Paragraph(
            "This pack collects the week's human-readable report and key evidence. "
            "Raw AI-only logs are listed in the inventory and intentionally not printed.",
            STYLES["body_tight"],
        )
    )
    story.append(NextPageTemplate("later"))
    story.append(PageBreak())

    # TOC
    story.append(Paragraph("Contents", STYLES["toc_title"]))
    toc = TableOfContents()
    toc.levelStyles = [TOC_H1, TOC_H2]
    toc.dotsMinLevel = 0
    story.append(toc)
    story.append(PageBreak())

    renderer = MarkdownRenderer(story, CONTENT_W)
    for section in week["sections"]:
        kind = section[0]
        path = ROOT / section[1] if section[1] else None
        title_text = section[2] if len(section) > 2 else None
        if kind == "md":
            if path and path.exists():
                renderer.render(read_text(path), str(path.relative_to(ROOT)))
                story.append(Spacer(1, 0.15 * cm))
            else:
                add_note(story, f"Missing file: <font face='Courier'>{escape_xml(section[1])}</font>")
        elif kind == "text":
            max_lines = section[3] if len(section) > 3 else None
            if path and path.exists():
                add_text_section(story, path, title_text or path.name, max_lines)
            else:
                add_note(story, f"Missing file: <font face='Courier'>{escape_xml(section[1])}</font>")
        elif kind == "code":
            max_lines = section[3] if len(section) > 3 else None
            if path and path.exists():
                add_code_section(story, path, title_text or path.name, max_lines)
            else:
                add_note(story, f"Missing file: <font face='Courier'>{escape_xml(section[1])}</font>")
        elif kind == "csv":
            max_rows = section[3] if len(section) > 3 else None
            font_size = section[4] if len(section) > 4 else 7.2
            if path and path.exists():
                add_csv_section(story, path, title_text or path.name, max_rows, font_size)
            else:
                add_note(story, f"Missing file: <font face='Courier'>{escape_xml(section[1])}</font>")
        elif kind == "summary_csv":
            column = section[3]
            if path and path.exists():
                add_csv_summary(story, path, title_text or path.name, column)
            else:
                add_note(story, f"Missing file: <font face='Courier'>{escape_xml(section[1])}</font>")
        elif kind == "coverage":
            if path and path.exists():
                add_coverage_summary(story, path, title_text or path.name)
            else:
                add_note(story, f"Missing file: <font face='Courier'>{escape_xml(section[1])}</font>")
        elif kind == "mutation":
            if path and path.exists():
                add_mutation_summary(story, path, title_text or path.name)
            else:
                add_note(story, f"Missing file: <font face='Courier'>{escape_xml(section[1])}</font>")
        elif kind == "json_table":
            if path and path.exists():
                add_json_table(story, path, title_text or path.name)
            else:
                add_note(story, f"Missing file: <font face='Courier'>{escape_xml(section[1])}</font>")
        elif kind == "image":
            if path and path.exists():
                add_image(story, path, title_text or path.name)
            else:
                add_note(story, f"Missing file: <font face='Courier'>{escape_xml(section[1])}</font>")
        elif kind == "note":
            add_note(story, title_text or "")

    add_source_inventory(story, folder)

    if week.get("append_pdf"):
        add_heading(story, f"Appendix — original {label} report", "h1")
        add_note(
            story,
            "The following pages are the original Week 7 PDF report, included for completeness. "
            "They keep their original pagination; this pack's page numbering stops before the appendix.",
        )
        story.append(PageBreak())

    doc.multiBuild(story, canvasmaker=NumberedCanvas)

    # Append an existing PDF (e.g. the original Week 7 report) after the pack.
    append_pdf = week.get("append_pdf")
    if append_pdf:
        extra = ROOT / append_pdf
        if extra.exists():
            base_reader = PdfReader(str(out_path))
            extra_reader = PdfReader(str(extra))
            writer = PdfWriter()
            for page in base_reader.pages:
                writer.add_page(page)
            start = len(writer.pages)
            for page in extra_reader.pages:
                writer.add_page(page)
            writer.add_outline_item(f"Appendix — original {label} report", start)
            with out_path.open("wb") as handle:
                writer.write(handle)

    return out_path


def build_combined(paths: list[Path]) -> Path:
    combined = OUT_DIR / "COMP441_GroupA_Weekly_Evidence.pdf"
    writer = PdfWriter()
    for week, path in zip(WEEKS, paths):
        reader = PdfReader(str(path))
        start = len(writer.pages)
        for page in reader.pages:
            writer.add_page(page)
        writer.add_outline_item(f"{week['label']} — {week['title']}", start)
    with combined.open("wb") as handle:
        writer.write(handle)
    return combined


def write_index(paths: list[Path]) -> Path:
    index = OUT_DIR / "README.md"
    lines = [
        "# Weekly evidence PDFs",
        "",
        "One PDF per week/folder, plus a combined pack for the marker.",
        "",
        "| PDF | Week | Contents | Source folder |",
        "|---|---|---|---|",
    ]
    for week, path in zip(WEEKS, paths):
        contents = ", ".join(
            s[2] or Path(s[1]).name for s in week["sections"] if len(s) > 1 and s[1]
        )
        lines.append(
            f"| [`{path.name}`]({path.name}) | {week['label']} | {week['title']} | `{week['folder']}` |"
        )
    lines.append(
        "| [`COMP441_GroupA_Weekly_Evidence.pdf`](COMP441_GroupA_Weekly_Evidence.pdf) "
        "| All | Combined pack with bookmarks for every week | all folders |"
    )
    lines += [
        "",
        "## What is printed",
        "",
        "Each pack prints the week's README/report, key summary tables, small raw outputs, and an inventory of the folder.",
        "Large raw artefacts (full mutmut output, coverage JSON, HTML coverage, kill matrices) are listed in the inventory",
        "and remain in the repository as evidence; they are not printed page-for-page.",
        "",
        "Items tagged `[AI-only]` or `[v1 baseline]` are deliberately excluded from the printed pages. They are the AI",
        "baseline's raw output, not the final hybrid result. They are still in the repository because the brief requires",
        "the AI-only baseline and v1 mutation evidence.",
        "",
        "See [`AI_ONLY_EXCLUDED.md`](AI_ONLY_EXCLUDED.md) for the full list and the reason each item is kept.",
        "",
        "## Rebuild",
        "",
        "```bash",
        "python reports/build_week_pdfs.py",
        "```",
    ]
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return index


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for week in WEEKS:
        path = build_week(week)
        paths.append(path)
        print(f"Wrote {path.relative_to(ROOT)}")
    combined = build_combined(paths)
    print(f"Wrote {combined.relative_to(ROOT)}")
    index = write_index(paths)
    print(f"Wrote {index.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
