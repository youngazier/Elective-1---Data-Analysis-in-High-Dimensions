#!/usr/bin/env python3
"""Build a 16-slide editable 16:9 PowerPoint deck (.pptx) from the study assets.

All titles, Slide 1 cover layout, Slide 2 ToC + workflow, Slide 3 motivation & RQs,
Slide 16 closing slide, and custom diagrams are emitted as native OOXML shapes and
editable text boxes using the orange-white-blue VGU x FRA-UAS palette, while
empirical Matplotlib figures (fig01-fig07), conceptual illustrations (diag01-diag05),
and logos are embedded cleanly at exact aspect ratios.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape
import zipfile

from PIL import Image

BASE_DIR = Path("/mnt/hdd-1tb/CSE-VGU/2026-2027/Elective-1")
FIG_DIR = BASE_DIR / "output" / "figures"
LOGO_DIR = BASE_DIR / "report" / "logo"
OUT_PPTX = BASE_DIR / "output" / "When_AI_Disagrees_With_You.pptx"

# 1920 x 1080 logical canvas mapped cleanly onto 13.333" x 7.5" (12192000 x 6858000 EMU)
CANVAS_W = 1920
CANVAS_H = 1080
PX_TO_EMU = 6350
SLIDE_W_EMU = CANVAS_W * PX_TO_EMU
SLIDE_H_EMU = CANVAS_H * PX_TO_EMU

FONT_NAME = "Open Sans"

# VGU Orange, White, and Frankfurt UAS Blue Palette
ORANGE = "F58220"
ORANGE_DARK = "C2410C"
ORANGE_BG = "FFF7ED"
ORANGE_BORDER = "FDBA74"

BLUE = "005A9C"
BLUE_LIGHT = "E0F2FE"
BLUE_BG = "EFF6FF"
BLUE_BORDER = "93C5FD"

NAVY = "0F2C59"
SLATE = "475569"
LIGHT_BG = "F8FAFC"
SOFT_BG = "F1F5F9"
GRAY_BORDER = "CBD5E1"
WHITE = "FFFFFF"


def emu(px: float) -> int:
    return round(px * PX_TO_EMU)


@dataclass
class RunSpec:
    text: str
    pt: float = 11.0
    bold: bool = False
    color: str = NAVY


@dataclass
class ParagraphSpec:
    runs: list[RunSpec]
    align: str = "ctr"  # l, ctr, r
    space_after_pt: float = 2.0
    line_pct: int = 118000


def make_p(
    text: str,
    pt: float = 11.0,
    bold: bool = False,
    color: str = NAVY,
    align: str = "ctr",
    space_after_pt: float = 2.0,
    line_pct: int = 118000,
) -> ParagraphSpec:
    return ParagraphSpec(
        runs=[RunSpec(text=text, pt=pt, bold=bold, color=color)],
        align=align,
        space_after_pt=space_after_pt,
        line_pct=line_pct,
    )


def render_paragraphs(paragraphs: list[ParagraphSpec]) -> str:
    out: list[str] = []
    for p in paragraphs:
        ppr = (
            f'<a:pPr algn="{p.align}">'
            f'<a:lnSpc><a:spcPct val="{p.line_pct}"/></a:lnSpc>'
            f'<a:spcAft><a:spcPts val="{round(p.space_after_pt * 100)}"/></a:spcAft>'
            f"</a:pPr>"
        )
        runs_xml: list[str] = []
        for r in p.runs:
            b_attr = ' b="1"' if r.bold else ' b="0"'
            sz = round(r.pt * 100)
            runs_xml.append(
                f'<a:r><a:rPr lang="en-US" sz="{sz}"{b_attr} dirty="0">'
                f'<a:solidFill><a:srgbClr val="{r.color}"/></a:solidFill>'
                f'<a:latin typeface="{FONT_NAME}"/><a:ea typeface="{FONT_NAME}"/>'
                f'<a:cs typeface="{FONT_NAME}"/>'
                f"</a:rPr><a:t>{escape(r.text)}</a:t></a:r>"
            )
        out.append(f"<a:p>{ppr}{''.join(runs_xml)}</a:p>")
    return "".join(out)


@dataclass
class SlideBuilder:
    title: str
    _next_id: int = 2
    shapes: list[str] = field(default_factory=list)
    rels: list[tuple[str, Path]] = field(default_factory=list)

    def _alloc_id(self) -> int:
        sid = self._next_id
        self._next_id += 1
        return sid

    def add_shape(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        prst: str = "rect",
        fill: str | None = None,
        stroke: str | None = None,
        stroke_pt: float = 1.5,
        radius_px: float = 0.0,
        rot_deg: float = 0.0,
        paragraphs: list[ParagraphSpec] | None = None,
        anchor: str = "ctr",
        pad_px: tuple[float, float, float, float] = (0, 0, 0, 0),
        tx_box: bool = False,
    ) -> None:
        sid = self._alloc_id()
        rot_attr = f' rot="{round(rot_deg * 60000)}"' if rot_deg else ""
        av_lst = ""
        if prst == "roundRect" and w > 0 and h > 0:
            adj = min(50000, max(0, round(radius_px / min(w, h) * 100000)))
            av_lst = f'<a:avLst><a:gd name="adj" fmla="val {adj}"/></a:avLst>'

        fill_xml = (
            f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
            if fill is not None
            else "<a:noFill/>"
        )
        if stroke is not None and stroke_pt > 0:
            ln_w = round(stroke_pt * 12700)
            ln_xml = (
                f'<a:ln w="{ln_w}" cap="flat" cmpd="sng" algn="ctr">'
                f'<a:solidFill><a:srgbClr val="{stroke}"/></a:solidFill>'
                f"</a:ln>"
            )
        else:
            ln_xml = '<a:ln><a:noFill/></a:ln>'

        l_ins, t_ins, r_ins, b_ins = (emu(v) for v in pad_px)
        tx_xml = ""
        if paragraphs or tx_box:
            body = render_paragraphs(paragraphs or [make_p("")])
            tx_xml = (
                "<p:txBody>"
                f'<a:bodyPr wrap="square" rtlCol="0" anchor="{anchor}" '
                f'lIns="{l_ins}" tIns="{t_ins}" rIns="{r_ins}" bIns="{b_ins}"/>'
                "<a:lstStyle/>"
                f"{body}"
                "</p:txBody>"
            )

        tx_attr = ' txBox="1"' if tx_box else ""
        self.shapes.append(
            "<p:sp>"
            "<p:nvSpPr>"
            f'<p:cNvPr id="{sid}" name="Shape {sid}"/>'
            f"<p:cNvSpPr{tx_attr}/>"
            "<p:nvPr/>"
            "</p:nvSpPr>"
            "<p:spPr>"
            f'<a:xfrm{rot_attr}><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="{prst}">{av_lst}</a:prstGeom>'
            f"{fill_xml}{ln_xml}"
            "</p:spPr>"
            f"{tx_xml}"
            "</p:sp>"
        )

    def add_text(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        paragraphs: list[ParagraphSpec],
        anchor: str = "t",
        pad_px: tuple[float, float, float, float] = (0, 0, 0, 0),
    ) -> None:
        self.add_shape(
            x=x,
            y=y,
            w=w,
            h=h,
            prst="rect",
            fill=None,
            stroke=None,
            paragraphs=paragraphs,
            anchor=anchor,
            pad_px=pad_px,
            tx_box=True,
        )

    def add_card(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str,
        stroke: str | None = None,
        stroke_pt: float = 1.8,
        radius_px: float = 18.0,
        paragraphs: list[ParagraphSpec] | None = None,
        anchor: str = "ctr",
        pad_px: tuple[float, float, float, float] = (14, 10, 14, 10),
    ) -> None:
        self.add_shape(
            x=x,
            y=y,
            w=w,
            h=h,
            prst="roundRect",
            fill=fill,
            stroke=stroke,
            stroke_pt=stroke_pt,
            radius_px=radius_px,
            paragraphs=paragraphs,
            anchor=anchor,
            pad_px=pad_px,
        )

    def add_right_arrow(
        self, x1: float, y: float, x2: float, color: str = NAVY, head_w: float = 12, head_h: float = 14
    ) -> None:
        shaft_end = x2 - head_w + 2
        if shaft_end > x1:
            self.add_shape(x1, y - 2, shaft_end - x1, 4, prst="rect", fill=color)
        self.add_shape(
            x2 - head_w,
            y - head_h / 2,
            head_w,
            head_h,
            prst="triangle",
            fill=color,
            rot_deg=90.0,
        )

    def add_line_seg(self, x1: float, y1: float, x2: float, y2: float, thick: float = 4.0, color: str = NAVY) -> None:
        if abs(x2 - x1) >= abs(y2 - y1):
            lx = min(x1, x2)
            self.add_shape(lx, y1 - thick / 2, abs(x2 - x1), thick, prst="rect", fill=color)
        else:
            ty = min(y1, y2)
            self.add_shape(x1 - thick / 2, ty, thick, abs(y2 - y1), prst="rect", fill=color)

    def add_down_arrow(
        self, x: float, y1: float, y2: float, color: str = NAVY, head_w: float = 14, head_h: float = 12
    ) -> None:
        shaft_end = y2 - head_h + 2
        if shaft_end > y1:
            self.add_shape(x - 2, y1, 4, shaft_end - y1, prst="rect", fill=color)
        self.add_shape(
            x - head_w / 2,
            y2 - head_h,
            head_w,
            head_h,
            prst="triangle",
            fill=color,
            rot_deg=180.0,
        )

    def add_image(
        self, path: Path, x: float, y: float, max_w: float, max_h: float, center_in_box: bool = True
    ) -> tuple[float, float, float, float]:
        with Image.open(path) as im:
            iw, ih = im.size
        scale = min(max_w / iw, max_h / ih)
        w = iw * scale
        h = ih * scale
        px = x + (max_w - w) / 2 if center_in_box else x
        py = y + (max_h - h) / 2 if center_in_box else y

        sid = self._alloc_id()
        rid = f"rId{len(self.rels) + 1}"
        self.rels.append((rid, path))
        self.shapes.append(
            "<p:pic>"
            "<p:nvPicPr>"
            f'<p:cNvPr id="{sid}" name="{escape(path.name)}"/>'
            '<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>'
            "<p:nvPr/>"
            "</p:nvPicPr>"
            "<p:blipFill>"
            f'<a:blip r:embed="{rid}"/>'
            "<a:stretch><a:fillRect/></a:stretch>"
            "</p:blipFill>"
            "<p:spPr>"
            f'<a:xfrm><a:off x="{emu(px)}" y="{emu(py)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            "</p:spPr>"
            "</p:pic>"
        )
        return px, py, w, h

    def add_header(self, kicker: str, title: str, two_line: bool = False) -> float:
        self.add_text(
            110,
            54,
            1450,
            30,
            [make_p(kicker, pt=10.5, bold=True, color=BLUE, align="l", space_after_pt=0)],
        )
        title_h = 136 if two_line else 76
        self.add_text(
            110,
            92,
            1680,
            title_h,
            [make_p(title, pt=27.0, bold=True, color=NAVY, align="l", space_after_pt=0, line_pct=112000)],
        )
        bar_y = 92 + title_h + 12
        self.add_shape(110, bar_y, 96, 8, prst="rect", fill=ORANGE)
        return bar_y + 26

    def to_xml(self) -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            "<p:cSld>"
            "<p:spTree>"
            "<p:nvGrpSpPr><p:cNvPr id=\"1\" name=\"\"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>"
            "<p:grpSpPr><a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"0\" cy=\"0\"/>"
            "<a:chOff x=\"0\" y=\"0\"/><a:chExt cx=\"0\" cy=\"0\"/></a:xfrm></p:grpSpPr>"
            f"{''.join(self.shapes)}"
            "</p:spTree>"
            "</p:cSld>"
            "<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>"
            "</p:sld>"
        )


def build_slide_1() -> SlideBuilder:
    s = SlideBuilder("Title Slide")
    s.add_shape(0, 0, 650, 1080, prst="rect", fill=NAVY)
    s.add_shape(650, 0, 26, 1080, prst="rect", fill=ORANGE)

    s.add_text(
        90,
        150,
        480,
        90,
        [
            make_p("SUPERVISOR", pt=10.5, bold=True, color=ORANGE, align="l", space_after_pt=4),
            make_p("Prof. Dr. Eva Christina Andersson", pt=13.0, bold=False, color=WHITE, align="l"),
        ],
    )
    s.add_text(
        90,
        560,
        500,
        190,
        [
            make_p("PRESENTERS", pt=10.5, bold=True, color=ORANGE, align="l", space_after_pt=6),
            make_p("Tran Trong Nhan · 10423160", pt=13.5, bold=False, color=WHITE, align="l", space_after_pt=4),
            make_p("Nguyen Minh Nhat Huy · 10423045", pt=13.5, bold=False, color=WHITE, align="l", space_after_pt=4),
            make_p("Dao Hoang Minh Triet · 10423179", pt=13.5, bold=False, color=WHITE, align="l", space_after_pt=0),
        ],
    )

    s.add_text(
        760,
        105,
        1060,
        72,
        [
            make_p("VIETNAMESE–GERMAN UNIVERSITY", pt=11.5, bold=True, color=BLUE, align="l", space_after_pt=2),
            make_p("× FRANKFURT UNIVERSITY OF APPLIED SCIENCES", pt=11.5, bold=True, color=BLUE, align="l"),
        ],
    )
    s.add_text(
        760,
        235,
        1060,
        230,
        [
            make_p("When AI", pt=46.0, bold=True, color=NAVY, align="l", space_after_pt=2, line_pct=106000),
            make_p("Disagrees With You", pt=46.0, bold=True, color=NAVY, align="l", line_pct=106000),
        ],
    )
    s.add_text(
        765,
        475,
        960,
        60,
        [make_p("How university students respond to uncertain AI answers", pt=16.0, color=SLATE, align="l")],
    )

    s.add_image(LOGO_DIR / "vgu.png", 765, 785, 365, 125, center_in_box=True)
    s.add_image(LOGO_DIR / "fra-uas.png", 1215, 765, 385, 165, center_in_box=True)
    return s


def _draw_flow_node(
    s: SlideBuilder,
    x: float,
    y: float,
    w: float,
    h: float,
    cap: str,
    lines: list[tuple[str, bool, str, float]],
    col: str,
    cap_h: float = 42,
    cap_pt: float = 11.0,
) -> None:
    s.add_card(x, y, w, h, fill=WHITE, stroke=col, stroke_pt=2.0, radius_px=14)
    s.add_shape(x, y, w, cap_h, prst="roundRect", fill=col, radius_px=12)
    s.add_shape(x, y + cap_h - 14, w, 14, prst="rect", fill=col)
    s.add_text(x + 6, y + 4, w - 12, cap_h - 6, [make_p(cap, pt=cap_pt, bold=True, color=WHITE)], anchor="ctr")
    paras = [
        make_p(txt, pt=pt, bold=bold, color=c, space_after_pt=3.0, line_pct=112000)
        for txt, bold, c, pt in lines
    ]
    s.add_text(x + 10, y + cap_h + 6, w - 20, h - cap_h - 12, paras, anchor="ctr")


def build_slide_toc() -> SlideBuilder:
    s = SlideBuilder("Table of contents & study pipeline")
    s.add_header("TABLE OF CONTENTS · STUDY WORKFLOW", "Presentation Outline & Study Pipeline")

    # Top: Table of Contents aligned 1-to-1 with the 3 workflow columns below
    toc_cols = [
        (
            65,
            420,
            "SECTION 1 · SPEAKER 1 · SLIDES 3–5",
            "Motivation, Research Questions & Our Survey",
            "",
            [
                "• Slide 3: Motivation & RQ1–RQ3",
                "• Slide 4: Survey (Q1–Q5, n = 261)",
                "• Slide 5: Marginal Q1–Q5 choices",
            ],
            ORANGE,
            ORANGE_BG,
        ),
        (
            519,
            716,
            "SECTION 2 · SPEAKER 2 · SLIDES 6–10",
            "Methodology",
            "Nominal distance, linkage trees & optimal cut selection",
            [
                "• Slide 6: Normalized Hamming / Gower metric (nominal space)",
                "• Slides 7–8: Agglomerative trees & 4 linkage criteria",
                "• Slide 9: Dendrogram battle & cophenetic faithfulness (r_coph)",
                "• Slide 10: Choosing K = 6 via silhouette peak & anti-chaining",
            ],
            BLUE,
            BLUE_BG,
        ),
        (
            1279,
            576,
            "SECTION 3 · SPEAKER 3 · SLIDES 11–16",
            "Validation and Results",
            "Partition stability, external tests & 6 student archetypes",
            [
                "• Slide 11: Stability check via ARI (ties & 80% subsampling)",
                "• Slides 12–13: Six behavioral archetypes (C1–C6)",
                "• Slides 14–15: External validation on Q6 AI use & S4 year",
                "• Slide 16: Conclusions, limitations & Q&A",
            ],
            NAVY,
            SOFT_BG,
        ),
    ]

    for x, w, badge, title, subtitle, bullets, col, bg in toc_cols:
        y, h = 208, 258
        s.add_card(x, y, w, h, fill=bg, stroke=col, stroke_pt=2.0, radius_px=16)
        s.add_shape(x, y, w, 44, prst="roundRect", fill=col, radius_px=14)
        s.add_shape(x, y + 30, w, 14, prst="rect", fill=col)
        s.add_text(x + 12, y + 4, w - 24, 36, [make_p(badge, pt=10.5, bold=True, color=WHITE)], anchor="ctr")

        if subtitle:
            s.add_text(
                x + 18,
                y + 52,
                w - 36,
                64,
                [
                    make_p(title, pt=14.0, bold=True, color=NAVY, align="l", space_after_pt=2, line_pct=108000),
                    make_p(subtitle, pt=9.8, color=SLATE, align="l", space_after_pt=0, line_pct=108000),
                ],
                anchor="ctr",
            )
        else:
            s.add_text(
                x + 16,
                y + 52,
                w - 32,
                64,
                [make_p(title, pt=12.5, bold=True, color=NAVY, align="l", space_after_pt=0, line_pct=112000)],
                anchor="ctr",
            )

        s.add_line_seg(x + 16, y + 120, x + w - 16, y + 120, thick=1.5, color=col)
        bullet_ps = [
            make_p(b, pt=9.5, color=NAVY, align="l", space_after_pt=3.0, line_pct=112000) for b in bullets
        ]
        s.add_text(x + 16, y + 128, w - 32, h - 134, bullet_ps, anchor="t")
        s.add_down_arrow(x + w / 2, 470, 514, color=col, head_w=16, head_h=12)

    # Bottom: Section 0 Study Workflow Diagram divided into the same 3 matching zones
    zones = [
        (65, 420, "STAGE 1 · MOTIVATION & DATA", ORANGE, ORANGE_BG, ORANGE_DARK),
        (519, 716, "STAGE 2 · UNSUPERVISED METHODOLOGY", BLUE, BLUE_BG, BLUE),
        (1279, 576, "STAGE 3 · VALIDATION & RESULTS", NAVY, SOFT_BG, NAVY),
    ]
    for x, w, zlabel, col, bg, tcol in zones:
        s.add_card(x, 518, w, 496, fill=bg, stroke=col, stroke_pt=2.0, radius_px=18)
        s.add_text(x + 14, 524, w - 28, 30, [make_p(zlabel, pt=10.2, bold=True, color=tcol)], anchor="ctr")

    # Zone 1 internals: Motivation + RQ trigger -> A (Survey Q1-Q5)
    s.add_card(
        89,
        564,
        372,
        82,
        fill=WHITE,
        stroke=ORANGE,
        stroke_pt=1.8,
        radius_px=12,
        paragraphs=[
            make_p("Motivation & RQs (Slide 3)", pt=10.0, bold=True, color=ORANGE_DARK, space_after_pt=2),
            make_p("Uncertain AI · 3 Research Questions", pt=9.2, color=NAVY, space_after_pt=0),
        ],
        pad_px=(10, 6, 10, 6),
    )
    s.add_down_arrow(275, 648, 678, color=ORANGE_DARK, head_w=14, head_h=10)
    _draw_flow_node(
        s,
        89,
        680,
        372,
        192,
        "A · Survey Q1–Q5",
        [
            ("261 VGU students", True, NAVY, 11.5),
            ("5 coursework scenarios", False, SLATE, 10.0),
            ("Slides 4–5", True, ORANGE_DARK, 9.5),
        ],
        ORANGE,
    )
    s.add_card(
        89,
        898,
        372,
        84,
        fill=WHITE,
        stroke=ORANGE_BORDER,
        stroke_pt=1.5,
        radius_px=12,
        paragraphs=[
            make_p("Input matrix: 261 × 5 nominal", pt=9.8, bold=True, color=NAVY, space_after_pt=2),
            make_p("Unordered A–F · no preset grading", pt=9.0, color=SLATE, space_after_pt=0),
        ],
        pad_px=(10, 6, 10, 6),
    )

    # Zone 2 internals: B -> C -> D (Methodology)
    s.add_card(
        539,
        564,
        676,
        82,
        fill=WHITE,
        stroke=BLUE_BORDER,
        stroke_pt=1.5,
        radius_px=12,
        paragraphs=[
            make_p("Agglomerative Clustering Pipeline (Bottom-Up)", pt=10.5, bold=True, color=BLUE, space_after_pt=2),
            make_p("Preserve unordered choices → compare linkages → pick optimal cut K", pt=9.5, color=NAVY, space_after_pt=0),
        ],
        pad_px=(10, 6, 10, 6),
    )
    _draw_flow_node(
        s,
        539,
        680,
        204,
        192,
        "B · Distance",
        [
            ("Pairwise Metric", True, NAVY, 10.5),
            ("Hamming / Gower", False, SLATE, 9.5),
            ("Slide 6", True, BLUE, 9.5),
        ],
        BLUE,
    )
    _draw_flow_node(
        s,
        775,
        680,
        204,
        192,
        "C · Build Tree",
        [
            ("Average (UPGMA)", True, NAVY, 10.5),
            ("r_coph = 0.6221", False, SLATE, 9.5),
            ("Slides 7–9", True, BLUE, 9.5),
        ],
        BLUE,
    )
    _draw_flow_node(
        s,
        1011,
        680,
        204,
        192,
        "D · Cut at K = 6",
        [
            ("Silhouette Peak", True, NAVY, 10.5),
            ("Sil = +0.1952", False, SLATE, 9.5),
            ("Slide 10", True, BLUE, 9.5),
        ],
        BLUE,
    )
    s.add_card(
        539,
        898,
        676,
        84,
        fill=WHITE,
        stroke=BLUE_BORDER,
        stroke_pt=1.5,
        radius_px=12,
        paragraphs=[
            make_p("Why UPGMA at K = 6? Breaks Single chains (98%) & resists ties", pt=9.8, bold=True, color=NAVY, space_after_pt=2),
            make_p("Zero singletons; largest cluster drops from 88.9% (Complete) to 26.1%", pt=9.2, color=SLATE, space_after_pt=0),
        ],
        pad_px=(10, 6, 10, 6),
    )

    # Zone 3 internals: D forks to E (Stability) & F (External Validation) -> Results (6 Archetypes)
    _draw_flow_node(
        s,
        1301,
        582,
        264,
        178,
        "E · Check Stability",
        [
            ("Shuffle & 80% sample", True, NAVY, 10.2),
            ("ARI = 0.50–0.57", False, SLATE, 9.5),
            ("Slide 11", True, BLUE, 9.5),
        ],
        BLUE,
    )
    _draw_flow_node(
        s,
        1301,
        792,
        264,
        178,
        "F · External Checks",
        [
            ("Q6 AI use & S4 Year", True, NAVY, 10.2),
            ("p = 0.0147 · p = 0.0001", False, SLATE, 9.5),
            ("Slides 14–15", True, NAVY, 9.5),
        ],
        NAVY,
    )
    _draw_flow_node(
        s,
        1617,
        656,
        216,
        240,
        "Results · K = 6",
        [
            ("6 Behavioral", True, NAVY, 11.2),
            ("Archetypes", True, NAVY, 11.2),
            ("(C1–C6 groups)", False, ORANGE_DARK, 9.8),
            ("Slides 12–13, 16", True, ORANGE_DARK, 9.5),
        ],
        ORANGE,
    )

    # Flowchart edges drawn last so arrowheads sit cleanly across zone boundaries
    s.add_right_arrow(461, 776, 537, color=NAVY)
    s.add_right_arrow(743, 776, 773, color=BLUE)
    s.add_right_arrow(979, 776, 1009, color=BLUE)

    # Fork D -> E and D -> F across Zone 2 -> Zone 3 boundary
    s.add_line_seg(1215, 776, 1257, 776, thick=4.0, color=NAVY)
    s.add_line_seg(1257, 671, 1257, 881, thick=4.0, color=NAVY)
    s.add_right_arrow(1257, 671, 1299, color=NAVY)
    s.add_right_arrow(1257, 881, 1299, color=NAVY)

    # Merge E & F -> Results
    s.add_line_seg(1565, 671, 1589, 671, thick=4.0, color=NAVY)
    s.add_line_seg(1565, 881, 1589, 881, thick=4.0, color=NAVY)
    s.add_line_seg(1589, 671, 1589, 881, thick=4.0, color=NAVY)
    s.add_right_arrow(1589, 776, 1615, color=ORANGE_DARK)
    return s


def build_slide_motivation() -> SlideBuilder:
    s = SlideBuilder("Motivation & research questions")
    s.add_header("SECTION 1 · MOTIVATION, RQs & SURVEY · SPEAKER 1 (~3.5 MIN)", "Motivation & research questions")

    s.add_text(
        110,
        214,
        1700,
        36,
        [make_p("Motivation: Why Uncertain AI Answers Matter in Higher Education", pt=14.5, bold=True, color=NAVY)],
    )
    mots = [
        (
            "1. Widespread AI Use",
            "4.09 ± 2.13 days/wk",
            "Students use ChatGPT, Gemini & Claude routinely in coursework (n = 261, median = 4.0).",
            BLUE,
            BLUE_BG,
            BLUE,
        ),
        (
            "2. Four Failure Traps",
            "Fluent ≠ Reliable",
            "Wrong facts, fake citations, skipped math steps & answer flips on \"Are you sure?\".",
            ORANGE,
            ORANGE_BG,
            ORANGE_DARK,
        ),
        (
            "3. Unsupervised Goal",
            "No Preset Grading",
            "Rather than marking answers right or wrong, let natural reaction groups emerge from Q1–Q5.",
            NAVY,
            SOFT_BG,
            NAVY,
        ),
    ]
    for i, (cap, big, desc, col, bg, bcol) in enumerate(mots):
        x = 110 + i * 586
        y, w, h = 262, 528, 240
        s.add_card(x, y, w, h, fill=bg, stroke=col, stroke_pt=2.0, radius_px=16)
        s.add_shape(x, y, w, 48, prst="roundRect", fill=col, radius_px=14)
        s.add_shape(x, y + 32, w, 16, prst="rect", fill=col)
        s.add_text(x + 12, y + 6, w - 24, 38, [make_p(cap, pt=12.0, bold=True, color=WHITE)], anchor="ctr")
        s.add_text(
            x + 18,
            y + 62,
            w - 36,
            162,
            [
                make_p(big, pt=16.5, bold=True, color=bcol, space_after_pt=8),
                make_p(desc, pt=11.0, color=NAVY, line_pct=118000),
            ],
            anchor="ctr",
        )

    s.add_text(
        110,
        534,
        1700,
        36,
        [make_p("Three Core Research Questions (RQ1–RQ3)", pt=14.5, bold=True, color=NAVY)],
    )
    rqs = [
        (
            "RQ1 · Student Habits",
            "How do students react when AI seems wrong or unclear?",
            "Tests whether natural first-response strategies emerge across 5 conflict scenarios (Q1–Q5).",
            ORANGE,
            ORANGE_BG,
            ORANGE_BORDER,
            ORANGE_DARK,
        ),
        (
            "RQ2 · Grouping Method",
            "Does the choice of clustering rule change the results?",
            "Compares Single, Complete & Average (UPGMA) linkage on discrete Normalized Hamming distances.",
            BLUE,
            BLUE_BG,
            BLUE_BORDER,
            BLUE,
        ),
        (
            "RQ3 · Real-World Check",
            "Are these groups stable, and linked to AI use & study year?",
            "Checks ARI stability under shuffles & 80% subsampling, plus unseen Q6 usage & S4 year.",
            ORANGE,
            ORANGE_BG,
            ORANGE_BORDER,
            ORANGE_DARK,
        ),
    ]
    for i, (cap, question, scope, col, bg, div_col, tcol) in enumerate(rqs):
        x = 110 + i * 586
        y, w, h = 582, 528, 420
        s.add_card(x, y, w, h, fill=bg, stroke=col, stroke_pt=2.2, radius_px=18)
        s.add_shape(x, y, w, 54, prst="roundRect", fill=col, radius_px=16)
        s.add_shape(x, y + 36, w, 18, prst="rect", fill=col)
        s.add_text(x + 12, y + 8, w - 24, 40, [make_p(cap, pt=13.0, bold=True, color=WHITE)], anchor="ctr")
        s.add_text(
            x + 24,
            y + 74,
            w - 48,
            148,
            [make_p(question, pt=15.0, bold=True, color=tcol, line_pct=118000)],
            anchor="ctr",
        )
        s.add_line_seg(x + 42, y + 236, x + w - 42, y + 236, thick=1.8, color=div_col)
        s.add_text(
            x + 24,
            y + 252,
            w - 48,
            148,
            [make_p(scope, pt=11.5, color=NAVY, line_pct=120000)],
            anchor="ctr",
        )
    return s


def build_slide_3() -> SlideBuilder:
    s = SlideBuilder("Survey design: 5 scenarios & sample (n = 261)")
    s.add_header("SECTION 1 · MOTIVATION, RQs & SURVEY", "Survey design: 5 uncertainty scenarios & sample (n = 261)")

    s.add_text(
        110,
        228,
        1700,
        36,
        [make_p("Survey Architecture: 5 Scenarios (Q1–Q5) & Sample (n = 261)", pt=15.0, bold=True, color=NAVY)],
    )

    scenarios = [
        ("Q1 (6 opts)", "AI Disagrees", "With Your B", "A–F"),
        ("Q2 (6 opts)", "Two AIs", "Disagree (B vs D)", "A–F"),
        ("Q3 (5 opts)", "Cited Paper", "Not on Scholar", "A–E"),
        ("Q4 (5 opts)", "Unclear Step", "Step 3 → Step 4", "A–E"),
        ("Q5 (6 opts)", "AI Flips", "'Are you sure?'", "A–F"),
    ]
    for i, (qid, t1, t2, opts) in enumerate(scenarios):
        x = 120 + i * 342
        col = ORANGE if i % 2 == 0 else BLUE
        bg = ORANGE_BG if i % 2 == 0 else BLUE_BG
        s.add_card(x, 282, 312, 206, fill=bg, stroke=col, stroke_pt=2.0, radius_px=16)
        s.add_card(
            x + 24,
            298,
            264,
            40,
            fill=col,
            stroke=None,
            radius_px=8,
            paragraphs=[make_p(qid, pt=11.5, bold=True, color=WHITE)],
            pad_px=(4, 2, 4, 2),
        )
        s.add_text(
            x + 12,
            352,
            288,
            122,
            [
                make_p(t1, pt=12.5, bold=True, color=NAVY, space_after_pt=3),
                make_p(t2, pt=11.0, color=SLATE, space_after_pt=8),
                make_p(f"Nominal: {opts}", pt=10.5, bold=True, color=col),
            ],
        )

    # Action spectrum bar
    s.add_card(120, 516, 1680, 220, fill=WHITE, stroke=NAVY, stroke_pt=2.0, radius_px=16)
    s.add_text(
        120,
        532,
        1680,
        36,
        [make_p("Nominal Response Spectrum (What Students Do First)", pt=13.0, bold=True, color=NAVY)],
    )
    actions = [
        ("Opt A", "Course Material", "Notes / Scholar", BLUE),
        ("Opt B", "Self-Solve", "Derive / Re-solve", BLUE),
        ("Opt C", "Same AI", "Probe / Ask DOI", ORANGE),
        ("Opt D", "Diff AI / Peer", "2nd Opinion", ORANGE),
        ("Opt E / F", "Accept / Reject", "No Verification", NAVY),
    ]
    for i, (code, a1, a2, col) in enumerate(actions):
        ax = 148 + i * 328
        s.add_card(
            ax,
            582,
            306,
            132,
            fill=LIGHT_BG,
            stroke=col,
            stroke_pt=1.8,
            radius_px=12,
            paragraphs=[
                make_p(code, pt=11.5, bold=True, color=col, space_after_pt=3),
                make_p(a1, pt=11.5, bold=True, color=NAVY, space_after_pt=2),
                make_p(a2, pt=10.0, color=SLATE),
            ],
            pad_px=(8, 6, 8, 6),
        )

    # Bottom split: VGU Sample Profile vs Withheld External Validation
    s.add_card(
        120,
        764,
        822,
        246,
        fill=BLUE_BG,
        stroke=BLUE,
        stroke_pt=2.0,
        radius_px=16,
        paragraphs=[
            make_p("VGU Sample Profile (n = 261, 0 Missing)", pt=13.5, bold=True, color=BLUE, space_after_pt=8),
            make_p("215 unique 5-question profiles / 5,400 possible", pt=11.2, color=NAVY, space_after_pt=5),
            make_p("Years 1–4: ~24% each · Grad/Master: 4.6%", pt=11.2, color=NAVY, space_after_pt=5),
            make_p("Major: 52.1% CSE · Top repeat: B-B-A-B-B (n = 8)", pt=11.2, color=NAVY),
        ],
        pad_px=(18, 12, 18, 12),
    )
    s.add_card(
        978,
        764,
        822,
        246,
        fill=ORANGE_BG,
        stroke=ORANGE,
        stroke_pt=2.0,
        radius_px=16,
        paragraphs=[
            make_p(
                "Withheld From Clustering (External Validation)",
                pt=13.5,
                bold=True,
                color=ORANGE_DARK,
                space_after_pt=8,
            ),
            make_p("Q6: Weekly AI Usage (0–7 days)", pt=11.8, bold=True, color=NAVY, space_after_pt=2),
            make_p("Mean = 4.09 ± 2.13 days/wk · Median = 4.0", pt=10.8, color=SLATE, space_after_pt=8),
            make_p("S4: Year of Study (1st Yr – Grad, n = 255)", pt=11.8, bold=True, color=NAVY),
        ],
        pad_px=(18, 12, 18, 12),
    )
    return s


def build_slide_4() -> SlideBuilder:
    s = SlideBuilder("First look: student choices across Q1-Q5")
    s.add_header("SECTION 1 · MOTIVATION, RQs & SURVEY", "First look: student choices across Q1–Q5")
    s.add_image(FIG_DIR / "fig01_marginal_responses.png", 365, 220, 1190, 672)

    cards = [
        ("Q3 Missing-Paper Spike", "40.2% pick Opt A (Search source, n = 105)", ORANGE_DARK, ORANGE_BG, ORANGE),
        ("Expected Match Rate", "Q3 = 25.7% vs. 17.7%–20.7% in Q1/Q2/Q4/Q5", BLUE, BLUE_BG, BLUE),
        ("Balanced Mix Elsewhere", "Q1, Q2, Q4, Q5 spread 8%–25% across A–F", NAVY, SOFT_BG, NAVY),
    ]
    for i, (head, sub, hcol, bg, stroke) in enumerate(cards):
        x = 130 + i * 562
        s.add_card(
            x,
            906,
            536,
            132,
            fill=bg,
            stroke=stroke,
            stroke_pt=2.0,
            radius_px=16,
            paragraphs=[
                make_p(head, pt=13.0, bold=True, color=hcol, space_after_pt=5),
                make_p(sub, pt=10.5, color=NAVY),
            ],
            pad_px=(14, 10, 14, 10),
        )
    return s


def build_slide_5() -> SlideBuilder:
    s = SlideBuilder("Nominal metric: Normalized Hamming / Gower distance")
    s.add_header("SECTION 2 · METHODOLOGY · SPEAKER 2 (~4.5 MIN)", "Nominal metric: Normalized Hamming / Gower distance")

    # Left column cards (x=90..830, w=740)
    s.add_card(
        90,
        245,
        740,
        130,
        fill=BLUE_BG,
        stroke=BLUE,
        stroke_pt=2.0,
        radius_px=16,
        paragraphs=[
            make_p("d(i, j) = mismatches(Q1..Q5) ÷ 5", pt=14.5, bold=True, color=BLUE, space_after_pt=4),
            make_p("0.0 = identical strategy · 1.0 = zero matching options (range 0–1)", pt=10.5, color=NAVY),
        ],
    )

    # Worked Example Box
    s.add_card(90, 398, 740, 365, fill=WHITE, stroke=NAVY, stroke_pt=2.0, radius_px=16)
    s.add_text(
        106,
        412,
        708,
        38,
        [make_p("Worked Example (Real VGU Student Pair)", pt=12.5, bold=True, color=NAVY)],
    )
    cols_x = [305, 405, 505, 605, 705]
    for idx, qname in enumerate(["Q1", "Q2", "Q3", "Q4", "Q5"]):
        s.add_text(cols_x[idx] - 32, 456, 64, 30, [make_p(qname, pt=11.0, bold=True, color=SLATE)])

    s.add_text(114, 498, 145, 36, [make_p("R018 (C3)", pt=11.0, bold=True, color=BLUE, align="l")])
    for idx, ch in enumerate(["B", "B", "A", "B", "B"]):
        s.add_card(
            cols_x[idx] - 30,
            495,
            60,
            46,
            fill=BLUE_BG,
            stroke=BLUE_BORDER,
            stroke_pt=1.5,
            radius_px=8,
            paragraphs=[make_p(ch, pt=12.0, bold=True, color=NAVY)],
            pad_px=(2, 2, 2, 2),
        )

    s.add_text(114, 560, 145, 36, [make_p("R008 (C4)", pt=11.0, bold=True, color=ORANGE_DARK, align="l")])
    for idx, ch in enumerate(["A", "D", "A", "D", "F"]):
        s.add_card(
            cols_x[idx] - 30,
            557,
            60,
            46,
            fill=ORANGE_BG,
            stroke=ORANGE_BORDER,
            stroke_pt=1.5,
            radius_px=8,
            paragraphs=[make_p(ch, pt=12.0, bold=True, color=NAVY)],
            pad_px=(2, 2, 2, 2),
        )

    s.add_text(114, 622, 150, 34, [make_p("Mismatch?", pt=10.5, bold=True, color=SLATE, align="l")])
    for idx, sc in enumerate([1, 1, 0, 1, 1]):
        bg = ORANGE if sc == 1 else BLUE
        s.add_card(
            cols_x[idx] - 28,
            620,
            56,
            40,
            fill=bg,
            stroke=None,
            radius_px=16,
            paragraphs=[make_p(str(sc), pt=11.0, bold=True, color=WHITE)],
            pad_px=(2, 2, 2, 2),
        )

    s.add_card(
        114,
        686,
        692,
        54,
        fill=LIGHT_BG,
        stroke=None,
        radius_px=8,
        paragraphs=[
            ParagraphSpec(
                runs=[
                    RunSpec("d(R018, R008) = (1 + 1 + 0 + 1 + 1) ÷ 5 = 4/5 = ", pt=11.5, bold=True, color=NAVY),
                    RunSpec("0.80", pt=11.5, bold=True, color=ORANGE_DARK),
                ],
                align="ctr",
                space_after_pt=0,
            )
        ],
        pad_px=(4, 2, 4, 2),
    )

    # Bottom two summary cards
    s.add_card(
        90,
        786,
        356,
        180,
        fill=ORANGE_BG,
        stroke=ORANGE,
        stroke_pt=2.0,
        radius_px=16,
        paragraphs=[
            make_p("33,930 Pairs", pt=18.5, bold=True, color=ORANGE_DARK, space_after_pt=4),
            make_p("Mean d = 0.8021", pt=11.0, bold=True, color=NAVY, space_after_pt=3),
            make_p("73.8% pairs differ in ≥ 4 items", pt=10.0, color=SLATE),
        ],
    )
    s.add_card(
        474,
        786,
        356,
        180,
        fill=LIGHT_BG,
        stroke=NAVY,
        stroke_pt=2.0,
        radius_px=16,
        paragraphs=[
            make_p("Why Nominal Metric?", pt=12.5, bold=True, color=NAVY, space_after_pt=5),
            make_p("Unordered A–F labels have", pt=10.5, color=SLATE, space_after_pt=2),
            make_p("no Euclidean mean (no Ward)", pt=10.5, bold=True, color=BLUE),
        ],
    )

    s.add_image(FIG_DIR / "fig02_hamming_distribution.png", 860, 315, 970, 582)
    return s


def build_slide_6() -> SlideBuilder:
    s = SlideBuilder("How agglomerative trees & cutting work")
    s.add_header("SECTION 2 · METHODOLOGY", "How agglomerative trees & cutting work")
    s.add_image(FIG_DIR / "diag01_dendrogram_cutting.png", 140, 225, 1610, 840)
    return s


def build_slide_7() -> SlideBuilder:
    s = SlideBuilder("Comparing 4 linkage rules on nominal data")
    s.add_header("SECTION 2 · METHODOLOGY", "Comparing 4 linkage rules on nominal data")
    s.add_image(FIG_DIR / "diag02_linkage_methods.png", 376, 235, 1167, 790)
    return s


def build_slide_8() -> SlideBuilder:
    s = SlideBuilder("Dendrogram battle & cophenetic faithfulness")
    s.add_header("SECTION 2 · METHODOLOGY", "Dendrogram battle & cophenetic faithfulness (r_coph)")
    s.add_image(FIG_DIR / "fig03_dendrograms_comparison.png", 380, 212, 1160, 444)
    s.add_image(FIG_DIR / "diag04_cophenetic_calculation.png", 565, 665, 790, 395)
    return s


def build_slide_9() -> SlideBuilder:
    s = SlideBuilder("Choosing K = 6: silhouette peak & anti-chaining")
    s.add_header("SECTION 2 · METHODOLOGY", "Choosing K = 6: silhouette peak & anti-chaining")
    s.add_image(FIG_DIR / "diag03_silhouette_explained.png", 55, 250, 900, 431)
    s.add_image(FIG_DIR / "fig04_silhouette_comparison.png", 955, 250, 900, 430)

    cards = [
        ("1. Silhouette Peak at K = 6", "+0.1952 peak (only 16.5% < 0)", BLUE, BLUE_BG),
        ("2. Breaks Dominant Mega-Blob", "Max = 26.1% vs. Complete 88.9%", ORANGE_DARK, ORANGE_BG),
        ("3. Clean Interpretability", "Zero singletons; separates C4 & C3", NAVY, SOFT_BG),
    ]
    for i, (head, sub, col, bg) in enumerate(cards):
        x = 120 + i * 566
        s.add_card(
            x,
            760,
            548,
            170,
            fill=bg,
            stroke=col,
            stroke_pt=2.0,
            radius_px=16,
            paragraphs=[
                make_p(head, pt=13.5, bold=True, color=col, space_after_pt=6),
                make_p(sub, pt=11.0, color=NAVY),
            ],
        )
    return s


def build_slide_10() -> SlideBuilder:
    s = SlideBuilder("Stability check: ties & 80% subsampling (ARI)")
    s.add_header("SECTION 3 · VALIDATION & RESULTS · SPEAKER 3 (~5 MIN)", "Stability check: ties & 80% subsampling (ARI)")
    s.add_image(FIG_DIR / "fig05_stability_ari.png", 360, 222, 1200, 607)

    s.add_card(
        120,
        845,
        820,
        195,
        fill=BLUE_BG,
        stroke=BLUE,
        stroke_pt=2.0,
        radius_px=16,
        paragraphs=[
            make_p("100× 80% Subsampling (n = 209) → Drop-Row Test", pt=13.5, bold=True, color=BLUE, space_after_pt=5),
            make_p("Average (K=6): Mean ARI = 0.523 · Median = 0.533", pt=12.0, bold=True, color=NAVY, space_after_pt=4),
            make_p("Complete drops to 0.301 · Single’s 0.820 is just 98%-chain stability", pt=10.5, color=SLATE),
        ],
    )
    s.add_card(
        980,
        845,
        820,
        195,
        fill=ORANGE_BG,
        stroke=ORANGE,
        stroke_pt=2.0,
        radius_px=16,
        paragraphs=[
            make_p("100× Row-Order Shuffles → Tie-Breaking Test", pt=13.5, bold=True, color=ORANGE_DARK, space_after_pt=5),
            make_p("Average (K=6): ARI = 0.498 vs. Complete Collapse = 0.135", pt=12.0, bold=True, color=NAVY, space_after_pt=4),
            make_p("Discrete distances (0, 0.2..1) cause ties; UPGMA resists row order", pt=10.5, color=SLATE),
        ],
    )
    return s


def build_slide_11() -> SlideBuilder:
    s = SlideBuilder("Six behavioral archetypes emerge (K = 6)")
    s.add_header("SECTION 3 · VALIDATION & RESULTS", "Six behavioral archetypes emerge (K = 6)")
    s.add_image(FIG_DIR / "fig06_cluster_profiles.png", 355, 220, 1210, 634)

    # Native K = 5 -> K = 6 Split Tree
    s.add_card(
        160,
        890,
        490,
        135,
        fill=NAVY,
        stroke=None,
        radius_px=16,
        paragraphs=[
            make_p("K = 5 Super-Cluster", pt=13.5, bold=True, color=WHITE, space_after_pt=4),
            make_p("n = 128 (49.0% Active Verifiers)", pt=11.5, color=BLUE_LIGHT),
        ],
    )
    s.add_text(668, 860, 128, 30, [make_p("K = 5 → 6", pt=10.5, bold=True, color=SLATE)])
    s.add_line_seg(656, 957, 725, 957, thick=4, color=NAVY)
    s.add_line_seg(725, 912, 725, 1002, thick=4, color=NAVY)
    s.add_right_arrow(725, 912, 795, color=BLUE, head_w=12, head_h=14)
    s.add_right_arrow(725, 1002, 795, color=ORANGE, head_w=12, head_h=14)

    s.add_card(800, 874, 960, 76, fill=BLUE_BG, stroke=BLUE, stroke_pt=2.0, radius_px=14)
    s.add_text(
        822,
        894,
        660,
        38,
        [make_p("C4 · Course-Material Verifiers (n = 68 · 26.1%)", pt=12.5, bold=True, color=BLUE, align="l")],
        anchor="ctr",
    )
    s.add_text(
        1490,
        894,
        245,
        38,
        [make_p("Opt A: 44%–68%", pt=11.5, color=NAVY, align="r")],
        anchor="ctr",
    )

    s.add_card(800, 964, 960, 76, fill=ORANGE_BG, stroke=ORANGE, stroke_pt=2.0, radius_px=14)
    s.add_text(
        822,
        984,
        660,
        38,
        [make_p("C3 · Independent Problem-Solvers (n = 60 · 23.0%)", pt=12.5, bold=True, color=ORANGE_DARK, align="l")],
        anchor="ctr",
    )
    s.add_text(
        1490,
        984,
        245,
        38,
        [make_p("Opt B: 52%–70%", pt=11.5, color=NAVY, align="r")],
        anchor="ctr",
    )
    return s


def build_slide_12() -> SlideBuilder:
    s = SlideBuilder("Behavioral archetype map: 6 student strategies")
    s.add_header("SECTION 3 · VALIDATION & RESULTS", "Behavioral archetype map: 6 student strategies")

    s.add_text(
        110,
        228,
        1700,
        68,
        [
            make_p("Six Behavioral Archetypes (UPGMA, K = 6, n = 261)", pt=15.0, bold=True, color=NAVY, space_after_pt=3),
            make_p(
                "At K = 5 → 6, the 128-student Self-Verifier super-cluster splits into Course-Material (C4) & Independent Solvers (C3)",
                pt=10.8,
                color=SLATE,
            ),
        ],
    )

    cards = [
        ("C4 · Course-Material Verifiers", "n = 68 (26.1%)", "Checks lecture notes & Scholar", "Q1–Q5 Opt A (44%–68%) · Q6: 4.41 d/wk", BLUE, BLUE_BG),
        ("C3 · Independent Solvers", "n = 60 (23.0%)", "Re-solves & derives from scratch", "Q1–Q5 Opt B (52%–70%) · Q6: 3.90 d/wk", BLUE, BLUE_BG),
        ("C2 · Same-AI Conversationalists", "n = 49 (18.8%)", "Probes same AI for DOIs & steps", "Q1–Q5 Opt C (47%–78%) · Q6: 4.63 d/wk (Max)", ORANGE, ORANGE_BG),
        ("C1 · Cross-AI & Peer Triangulators", "n = 46 (17.6%)", "Asks 2nd/3rd AI or classmate", "Q1–Q5 Opt D (48%–65%) · Q6: 3.67 d/wk", ORANGE, ORANGE_BG),
        ("C5 · Uncritical AI Conformers", "n = 20 (7.7%)", "Accepts AI & drops citations unverified", "Q1-E (85%), Q3-D (60%) · Q6: 2.85 d/wk (Min)", NAVY, SOFT_BG),
        ("C6 · AI-Skeptical Anchors", "n = 18 (6.9%)", "Keeps own answer or drops task", "Q1-F (78%), Q5-F (67%) · Q6: 4.44 d/wk", NAVY, SOFT_BG),
    ]
    for idx, (title, size, desc, stats, col, bg) in enumerate(cards):
        row = idx // 2
        col_idx = idx % 2
        x = 135 + col_idx * 845
        y = 318 + row * 212
        w, h = 805, 190
        s.add_card(x, y, w, h, fill=bg, stroke=col, stroke_pt=2.0, radius_px=16)
        s.add_shape(x, y, w, 54, prst="roundRect", fill=col, radius_px=14)
        s.add_shape(x, y + 36, w, 18, prst="rect", fill=col)
        s.add_text(x + 20, y + 10, 560, 34, [make_p(title, pt=12.5, bold=True, color=WHITE, align="l")], anchor="ctr")
        s.add_text(x + 565, y + 10, 220, 34, [make_p(size, pt=12.0, bold=True, color=WHITE, align="r")], anchor="ctr")
        s.add_text(
            x + 20,
            y + 70,
            w - 40,
            106,
            [
                make_p(desc, pt=12.5, bold=True, color=NAVY, align="l", space_after_pt=5),
                make_p(stats, pt=11.0, color=SLATE, align="l"),
            ],
            anchor="ctr",
        )

    s.add_card(135, 964, 1650, 56, fill=LIGHT_BG, stroke=GRAY_BORDER, stroke_pt=1.0, radius_px=10)
    s.add_text(155, 976, 540, 32, [make_p("■ 49.1% Active Verification (C4 + C3)", pt=11.0, bold=True, color=BLUE)], anchor="ctr")
    s.add_text(705, 976, 540, 32, [make_p("■ 36.4% AI / Peer Dialogue (C2 + C1)", pt=11.0, bold=True, color=ORANGE_DARK)], anchor="ctr")
    s.add_text(1255, 976, 510, 32, [make_p("■ 14.6% Extreme Poles (C5 + C6)", pt=11.0, bold=True, color=NAVY)], anchor="ctr")
    return s


def build_slide_13() -> SlideBuilder:
    s = SlideBuilder("External validation setup: testing Q6 & S4")
    s.add_header("SECTION 3 · VALIDATION & RESULTS", "External validation setup: testing Q6 & S4")
    s.add_image(FIG_DIR / "diag05_external_validation_methods.png", 205, 240, 1509, 770)
    return s


def build_slide_14() -> SlideBuilder:
    s = SlideBuilder("External validation results: AI usage & study year")
    s.add_header("SECTION 3 · VALIDATION & RESULTS", "External validation results: AI usage & study year")
    s.add_image(FIG_DIR / "fig07_external_validation.png", 55, 280, 1275, 574)

    # Top right card: Q6
    s.add_card(1355, 265, 500, 315, fill=ORANGE_BG, stroke=ORANGE, stroke_pt=2.2, radius_px=18)
    s.add_shape(1355, 265, 500, 54, prst="roundRect", fill=ORANGE, radius_px=16)
    s.add_shape(1355, 300, 500, 19, prst="rect", fill=ORANGE)
    s.add_text(
        1365,
        272,
        480,
        40,
        [make_p("Q6 · Weekly AI Usage (0–7 Days)", pt=12.5, bold=True, color=WHITE)],
        anchor="ctr",
    )
    s.add_text(
        1373,
        336,
        464,
        122,
        [
            make_p("p = 0.0147", pt=26.0, bold=True, color=ORANGE_DARK, space_after_pt=4),
            make_p("Kruskal–Wallis H = 14.14 (ANOVA p = 0.0130)", pt=10.5, bold=True, color=NAVY),
        ],
    )
    s.add_line_seg(1391, 466, 1819, 466, thick=1.5, color=ORANGE_BORDER)
    s.add_text(
        1373,
        482,
        464,
        82,
        [
            ParagraphSpec(
                runs=[
                    RunSpec("Highest: ", pt=11.0, color=NAVY),
                    RunSpec("C2 Same-AI = 4.63 d/wk", pt=11.0, bold=True, color=ORANGE_DARK),
                ],
                space_after_pt=4,
            ),
            ParagraphSpec(
                runs=[
                    RunSpec("Lowest: ", pt=11.0, color=NAVY),
                    RunSpec("C5 Conformers = 2.85 d/wk", pt=11.0, bold=True, color=NAVY),
                ],
            ),
        ],
    )

    # Bottom right card: S4
    s.add_card(1355, 608, 500, 315, fill=BLUE_BG, stroke=BLUE, stroke_pt=2.2, radius_px=18)
    s.add_shape(1355, 608, 500, 54, prst="roundRect", fill=BLUE, radius_px=16)
    s.add_shape(1355, 643, 500, 19, prst="rect", fill=BLUE)
    s.add_text(
        1365,
        615,
        480,
        40,
        [make_p("S4 · Year of Study (n = 255)", pt=12.5, bold=True, color=WHITE)],
        anchor="ctr",
    )
    s.add_text(
        1373,
        679,
        464,
        122,
        [
            make_p("p = 0.0001", pt=26.0, bold=True, color=BLUE, space_after_pt=4),
            make_p("χ² = 76.66 · 10,000 Monte Carlo Replicates", pt=10.5, bold=True, color=NAVY),
        ],
    )
    s.add_line_seg(1391, 809, 1819, 809, thick=1.5, color=BLUE_BORDER)
    s.add_text(
        1373,
        825,
        464,
        82,
        [
            make_p("10 of 12 Grad/Master sit in C5 (6) & C6 (4)", pt=11.0, color=NAVY, space_after_pt=4),
            make_p("42.1% of C5 Conformers are 1st-year", pt=11.0, color=NAVY),
        ],
    )
    return s


def build_slide_15() -> SlideBuilder:
    s = SlideBuilder("Conclusions, limitations & Q&A")
    s.add_header("SECTION 3 · VALIDATION & RESULTS · FINAL SLIDE", "Conclusions, limitations & Q&A")

    rqs = [
        ("RQ1 · Student Habits", "6 Distinct Archetypes", "• 49.1% actively verify", "• 36.4% probe AI / peers", "• 14.6% uncritical / skeptical", BLUE, BLUE_BG),
        ("RQ2 · Grouping Method", "UPGMA Wins Clearly", "• r_coph = 0.6221 (best)", "• 67 heights break ties", "• Single chains (98%), Complete ties", ORANGE, ORANGE_BG),
        ("RQ3 · Real-World Check", "Robust & Meaningful", "• ARI = 0.50–0.57 stable", "• Q6 AI use: p = 0.0147", "• S4 Study year: p = 0.0001", BLUE, BLUE_BG),
    ]
    for i, (head, big, b1, b2, b3, col, bg) in enumerate(rqs):
        x = 140 + i * 562
        y, w, h = 240, 516, 360
        s.add_card(x, y, w, h, fill=bg, stroke=col, stroke_pt=2.2, radius_px=18)
        s.add_shape(x, y, w, 58, prst="roundRect", fill=col, radius_px=16)
        s.add_shape(x, y + 40, w, 18, prst="rect", fill=col)
        s.add_text(x + 12, y + 10, w - 24, 38, [make_p(head, pt=13.5, bold=True, color=WHITE)], anchor="ctr")
        s.add_text(x + 16, y + 74, w - 32, 48, [make_p(big, pt=16.5, bold=True, color=NAVY)], anchor="ctr")
        s.add_line_seg(x + 48, y + 132, x + w - 48, y + 132, thick=1.5, color=col)
        s.add_text(
            x + 22,
            y + 150,
            w - 44,
            190,
            [
                make_p(b1, pt=12.5, color=NAVY, space_after_pt=10),
                make_p(b2, pt=12.5, color=NAVY, space_after_pt=10),
                make_p(b3, pt=12.5, color=NAVY),
            ],
            anchor="ctr",
        )

    s.add_card(
        140,
        625,
        1640,
        245,
        fill=ORANGE_BG,
        stroke=ORANGE,
        stroke_pt=2.0,
        radius_px=18,
        paragraphs=[
            make_p("Methodological Limitations & Future Work", pt=14.0, bold=True, color=ORANGE_DARK, space_after_pt=8),
            make_p(
                "1. Self-reported first intentions (n = 261 at VGU) rather than observed behavior logs or grades",
                pt=12.0,
                color=NAVY,
                space_after_pt=6,
            ),
            make_p(
                "2. Unweighted Hamming treats all option mismatches equally; 5-option Q3/Q4 have higher random match (20.0% vs 16.7%)",
                pt=11.5,
                color=NAVY,
                space_after_pt=8,
            ),
            make_p(
                "Future: Weighted semantic dissimilarities & longitudinal classroom tracking",
                pt=12.0,
                bold=True,
                color=BLUE,
            ),
        ],
    )

    s.add_image(LOGO_DIR / "vgu.png", 140, 915, 228, 78)
    s.add_text(
        460,
        890,
        1000,
        130,
        [make_p("Questions?", pt=46.0, bold=True, color=ORANGE)],
        anchor="ctr",
    )
    s.add_image(LOGO_DIR / "fra-uas.png", 1565, 905, 215, 92)
    return s


CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>
  <Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>
  <Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>
{slide_overrides}
</Types>"""

ROOT_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""

THEME_XML = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="VGU_FRAUAS_Theme">
  <a:themeElements>
    <a:clrScheme name="VGU_FRAUAS">
      <a:dk1><a:srgbClr val="{NAVY}"/></a:dk1>
      <a:lt1><a:srgbClr val="{WHITE}"/></a:lt1>
      <a:dk2><a:srgbClr val="{SLATE}"/></a:dk2>
      <a:lt2><a:srgbClr val="{LIGHT_BG}"/></a:lt2>
      <a:accent1><a:srgbClr val="{ORANGE}"/></a:accent1>
      <a:accent2><a:srgbClr val="{BLUE}"/></a:accent2>
      <a:accent3><a:srgbClr val="{ORANGE_DARK}"/></a:accent3>
      <a:accent4><a:srgbClr val="{BLUE_LIGHT}"/></a:accent4>
      <a:accent5><a:srgbClr val="{NAVY}"/></a:accent5>
      <a:accent6><a:srgbClr val="{GRAY_BORDER}"/></a:accent6>
      <a:hlink><a:srgbClr val="{BLUE}"/></a:hlink>
      <a:folHlink><a:srgbClr val="{ORANGE_DARK}"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="OpenSansScheme">
      <a:majorFont><a:latin typeface="{FONT_NAME}"/><a:ea typeface="{FONT_NAME}"/><a:cs typeface="{FONT_NAME}"/></a:majorFont>
      <a:minorFont><a:latin typeface="{FONT_NAME}"/><a:ea typeface="{FONT_NAME}"/><a:cs typeface="{FONT_NAME}"/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Clean">
      <a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
      <a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
      <a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
      <a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
</a:theme>"""

SLIDE_MASTER_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
</p:sldMaster>"""

SLIDE_MASTER_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""

SLIDE_LAYOUT_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank">
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""

SLIDE_LAYOUT_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""

PRES_PROPS_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:presProps xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'
VIEW_PROPS_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:viewProps xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:normalViewPr><p:restoredLeft sz="15620"/><p:restoredTop sz="94660"/></p:normalViewPr></p:viewProps>'
TABLE_STYLES_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>'


def write_pptx(slides: list[SlideBuilder], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    media_map: dict[Path, str] = {}

    def register_media(p: Path) -> str:
        if p not in media_map:
            media_map[p] = f"image{len(media_map) + 1}{p.suffix.lower()}"
        return media_map[p]

    slide_overrides = "\n".join(
        f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, len(slides) + 1)
    )
    sld_ids = "".join(
        f'<p:sldId id="{255 + i}" r:id="rId{i + 1}"/>'
        for i in range(1, len(slides) + 1)
    )
    pres_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" saveSubsetFonts="1">'
        '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
        f"<p:sldIdLst>{sld_ids}</p:sldIdLst>"
        f'<p:sldSz cx="{SLIDE_W_EMU}" cy="{SLIDE_H_EMU}" type="screen16x9"/>'
        '<p:notesSz cx="6858000" cy="9144000"/>'
        "</p:presentation>"
    )

    n = len(slides)
    pres_rels_items = [
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    ] + [
        f'<Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, n + 1)
    ] + [
        f'<Relationship Id="rId{n + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>',
        f'<Relationship Id="rId{n + 3}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/>',
        f'<Relationship Id="rId{n + 4}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>',
        f'<Relationship Id="rId{n + 5}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles" Target="tableStyles.xml"/>',
    ]
    pres_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{''.join(pres_rels_items)}"
        "</Relationships>"
    )

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES_XML.format(slide_overrides=slide_overrides))
        zf.writestr("_rels/.rels", ROOT_RELS_XML)
        zf.writestr("ppt/presentation.xml", pres_xml)
        zf.writestr("ppt/_rels/presentation.xml.rels", pres_rels_xml)
        zf.writestr("ppt/theme/theme1.xml", THEME_XML)
        zf.writestr("ppt/slideMasters/slideMaster1.xml", SLIDE_MASTER_XML)
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", SLIDE_MASTER_RELS_XML)
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", SLIDE_LAYOUT_XML)
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", SLIDE_LAYOUT_RELS_XML)
        zf.writestr("ppt/presProps.xml", PRES_PROPS_XML)
        zf.writestr("ppt/viewProps.xml", VIEW_PROPS_XML)
        zf.writestr("ppt/tableStyles.xml", TABLE_STYLES_XML)

        for idx, slide in enumerate(slides, start=1):
            zf.writestr(f"ppt/slides/slide{idx}.xml", slide.to_xml())
            s_rels = [
                f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{register_media(path)}"/>'
                for rid, path in slide.rels
            ]
            # Use unique rId for layout (after image rIds)
            layout_rid = f"rId{len(slide.rels) + 1}"
            s_rels.append(
                f'<Relationship Id="{layout_rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
            )
            zf.writestr(
                f"ppt/slides/_rels/slide{idx}.xml.rels",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f"{''.join(s_rels)}</Relationships>",
            )

        for src_path, media_name in media_map.items():
            zf.write(src_path, f"ppt/media/{media_name}")


def main() -> None:
    slides = [
        build_slide_1(),
        build_slide_toc(),
        build_slide_motivation(),
        build_slide_3(),
        build_slide_4(),
        build_slide_5(),
        build_slide_6(),
        build_slide_7(),
        build_slide_8(),
        build_slide_9(),
        build_slide_10(),
        build_slide_11(),
        build_slide_12(),
        build_slide_13(),
        build_slide_14(),
        build_slide_15(),
    ]
    write_pptx(slides, OUT_PPTX)
    print(f"Wrote {len(slides)} slides to {OUT_PPTX}")


if __name__ == "__main__":
    main()
