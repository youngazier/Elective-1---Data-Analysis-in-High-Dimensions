#!/usr/bin/env python3
"""Generate clean educational SVG + PNG diagrams for STATS_EXPLAINED.md."""

import argparse
from pathlib import Path
import subprocess
from xml.sax.saxutils import escape

OUT_DIR = Path(__file__).resolve().parent.parent / "output" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT = "Noto Sans, DejaVu Sans, Arial, sans-serif"


def svg_header(w: int, h: int, bg: str = "#FFFFFF") -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'  <rect width="{w}" height="{h}" fill="{bg}"/>',
        f'  <style>text {{ font-family: {FONT}; }}</style>',
    ]


def write_and_render(name: str, lines: list[str], scale: float = 2.0) -> None:
    lines.append("</svg>")
    svg_path = OUT_DIR / f"{name}.svg"
    png_path = OUT_DIR / f"{name}.png"
    svg_path.write_text("\n".join(lines), encoding="utf-8")
    subprocess.run(
        ["rsvg-convert", "-z", str(scale), "-o", str(png_path), str(svg_path)],
        check=True,
    )
    print(f"Generated {svg_path.name} and {png_path.name}")


def build_dendrogram_diagram() -> None:
    w, h = 920, 480
    s = svg_header(w, h, "#FFFFFF")

    # Title & subtitle
    s.append(
        f'<text x="460" y="38" text-anchor="middle" font-size="20" font-weight="700" fill="#1E293B">'
        f'How a Dendrogram Works &amp; What "Cutting at K" Means</text>'
    )
    s.append(
        f'<text x="460" y="62" text-anchor="middle" font-size="13.5" fill="#475569">'
        f'Toy example with 7 students: start at the bottom (individual students) and merge closest groups upward</text>'
    )

    # Coordinate helpers: y=390 is height 0.0, y=110 is height 1.0
    def y_of(height: float) -> float:
        return 390 - height * 280

    # Grid lines and y-axis
    for val in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        yy = y_of(val)
        s.append(
            f'<line x1="115" y1="{yy:.1f}" x2="730" y2="{yy:.1f}" '
            f'stroke="#E2E8F0" stroke-width="1" stroke-dasharray="4,4"/>'
        )
        s.append(
            f'<text x="103" y="{yy + 4:.1f}" text-anchor="end" font-size="12" fill="#64748B">{val:.1f}</text>'
        )

    s.append('<line x1="115" y1="105" x2="115" y2="395" stroke="#475569" stroke-width="1.8"/>')
    s.append(
        '<text x="48" y="250" text-anchor="middle" font-size="13" font-weight="600" fill="#334155" '
        'transform="rotate(-90 48 250)">Merge Height (Distance)</text>'
    )

    # Student positions (x)
    xs = [170, 250, 340, 420, 515, 595, 685]
    labels = ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]
    colors = ["#2563EB", "#2563EB", "#0D9488", "#0D9488", "#D97706", "#D97706", "#DC2626"]
    cluster_names = ["Cluster 1", "Cluster 2", "Cluster 3", "Cluster 4"]

    # Cluster background pills at bottom (cut at 0.65)
    pills = [
        (140, 280, "#DBEAFE", "#2563EB", cluster_names[0]),
        (310, 450, "#CCFBF1", "#0D9488", cluster_names[1]),
        (485, 625, "#FEF3C7", "#D97706", cluster_names[2]),
        (652, 718, "#FEE2E2", "#DC2626", cluster_names[3]),
    ]
    for x0, x1, fill, stroke, cname in pills:
        s.append(
            f'<rect x="{x0}" y="396" width="{x1 - x0}" height="52" rx="10" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        )
        s.append(
            f'<text x="{(x0 + x1) / 2:.1f}" y="440" text-anchor="middle" font-size="11.5" '
            f'font-weight="700" fill="{stroke}">{cname}</text>'
        )

    # Tree branches
    # Merge 1: S1 & S2 at h=0.20 -> x=210
    # Merge 2: S3 & S4 at h=0.30 -> x=380
    # Merge 3: S5 & S6 at h=0.40 -> x=555
    # Merge 4: (S1,S2) & (S3,S4) at h=0.78 -> x=295
    # Merge 5: (S5,S6) & S7 at h=0.84 -> x=620
    # Merge 6: Root at h=0.96 -> x=457.5
    def draw_merge(x_left: float, h_left: float, x_right: float, h_right: float, h_top: float, col: str) -> None:
        yl, yr, yt = y_of(h_left), y_of(h_right), y_of(h_top)
        s.append(
            f'<path d="M {x_left:.1f} {yl:.1f} V {yt:.1f} H {x_right:.1f} V {yr:.1f}" '
            f'fill="none" stroke="{col}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>'
        )

    draw_merge(xs[0], 0.0, xs[1], 0.0, 0.20, "#2563EB")
    draw_merge(xs[2], 0.0, xs[3], 0.0, 0.30, "#0D9488")
    draw_merge(xs[4], 0.0, xs[5], 0.0, 0.40, "#D97706")

    # Vertical stems up to cut & above cut
    y_cut = y_of(0.62)
    # Branch from (S5,S6) and S7
    draw_merge(210, 0.20, 380, 0.30, 0.76, "#475569")
    draw_merge(555, 0.40, xs[6], 0.0, 0.84, "#475569")
    draw_merge(295, 0.76, 620, 0.84, 0.96, "#334155")

    # Re-draw lower colored portions cleanly up to cut line so color coding is super clear
    for bx, h0, col in [(210, 0.20, "#2563EB"), (380, 0.30, "#0D9488"), (555, 0.40, "#D97706"), (xs[6], 0.0, "#DC2626")]:
        s.append(
            f'<line x1="{bx:.1f}" y1="{y_of(h0):.1f}" x2="{bx:.1f}" y2="{y_cut:.1f}" '
            f'stroke="{col}" stroke-width="3.0"/>'
        )

    # Student dots & labels
    for x, lbl, col in zip(xs, labels, colors):
        s.append(f'<circle cx="{x}" cy="{y_of(0.0):.1f}" r="5.5" fill="{col}" stroke="#FFFFFF" stroke-width="1.5"/>')
        s.append(
            f'<text x="{x}" y="418" text-anchor="middle" font-size="13" font-weight="700" fill="#1E293B">{lbl}</text>'
        )

    # Cut line
    s.append(
        f'<line x1="115" y1="{y_cut:.1f}" x2="740" y2="{y_cut:.1f}" '
        f'stroke="#E11D48" stroke-width="2.4" stroke-dasharray="8,5"/>'
    )
    # 4 intersection markers
    for bx, col in [(210, "#2563EB"), (380, "#0D9488"), (555, "#D97706"), (xs[6], "#DC2626")]:
        s.append(f'<circle cx="{bx}" cy="{y_cut:.1f}" r="5" fill="#FFFFFF" stroke="#E11D48" stroke-width="2.4"/>')

    # Right-side explanation cards
    # Card 1: Cut line callout
    s.append('<rect x="748" y="178" width="155" height="78" rx="8" fill="#FFF1F2" stroke="#FDA4AF" stroke-width="1.4"/>')
    s.append('<text x="760" y="200" font-size="12.5" font-weight="700" fill="#BE123C">Horizontal Cut</text>')
    s.append('<text x="760" y="218" font-size="11.5" fill="#475569">Crosses 4 branches</text>')
    s.append('<text x="760" y="235" font-size="12" font-weight="700" fill="#1E293B">→ K = 4 clusters</text>')
    s.append(f'<line x1="740" y1="{y_cut:.1f}" x2="748" y2="{y_cut:.1f}" stroke="#E11D48" stroke-width="2"/>')

    # Card 2: High vs low join
    s.append('<rect x="748" y="95" width="155" height="64" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.2"/>')
    s.append('<text x="760" y="116" font-size="12" font-weight="700" fill="#1E293B">High Merge (0.96)</text>')
    s.append('<text x="760" y="133" font-size="11" fill="#475569">Very different groups</text>')
    s.append('<text x="760" y="148" font-size="11" fill="#475569">join last at the top.</text>')

    s.append('<rect x="748" y="315" width="155" height="64" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.2"/>')
    s.append('<text x="760" y="336" font-size="12" font-weight="700" fill="#1E293B">Low Merge (0.20)</text>')
    s.append('<text x="760" y="353" font-size="11" fill="#475569">Very similar students</text>')
    s.append('<text x="760" y="368" font-size="11" fill="#475569">(S1 &amp; S2) join first.</text>')

    # Small label on merge height 0.20
    s.append(
        f'<text x="210" y="{y_of(0.20) - 8:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="#2563EB">h = 0.20</text>'
    )
    s.append(
        f'<text x="380" y="{y_of(0.30) - 8:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="#0D9488">h = 0.30</text>'
    )
    s.append(
        f'<text x="555" y="{y_of(0.40) - 8:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="#D97706">h = 0.40</text>'
    )

    write_and_render("diag01_dendrogram_cutting", s)


def build_linkage_diagram() -> None:
    w, h = 960, 650
    s = svg_header(w, h, "#FFFFFF")

    s.append(
        '<text x="480" y="36" text-anchor="middle" font-size="20" font-weight="700" fill="#1E293B">'
        'The 4 Linkage Rules: How Do We Measure Distance Between Two Groups?</text>'
    )
    s.append(
        '<text x="480" y="60" text-anchor="middle" font-size="13.5" fill="#475569">'
        'Cluster 1 (blue, k = 3 students) vs. Cluster 2 (orange, l = 3 students) — each rule picks which connections count</text>'
    )

    panels = [
        (30, 82, "1. Single (Nearest Neighbour)", "BASELINE", "#64748B", "#F1F5F9", "single"),
        (495, 82, "2. Complete (Furthest Neighbour)", "BASELINE", "#64748B", "#F1F5F9", "complete"),
        (30, 366, "3. Average Linkage (UPGMA)", "USED HERE", "#047857", "#D1FAE5", "average"),
        (495, 366, "4. Centroid & Ward Methods", "CANNOT USE", "#B91C1C", "#FEE2E2", "centroid"),
    ]

    # Relative point coordinates inside a 435x260 panel
    c1_pts = [(75, 108), (118, 134), (80, 166)]
    c2_pts = [(338, 104), (308, 140), (355, 168)]
    # Closest pair: c1_pts[1] (118,134) <-> c2_pts[1] (308,140)
    # Farthest pair: c1_pts[0] (75,108) <-> c2_pts[2] (355,168)

    for px, py, title, badge, badge_fg, badge_bg, kind in panels:
        card_border = "#10B981" if kind == "average" else ("#FCA5A5" if kind == "centroid" else "#CBD5E1")
        card_bw = "2.2" if kind == "average" else "1.4"
        s.append(
            f'<rect x="{px}" y="{py}" width="435" height="262" rx="12" '
            f'fill="#F8FAFC" stroke="{card_border}" stroke-width="{card_bw}"/>'
        )
        # Header bar
        s.append(
            f'<text x="{px + 18}" y="{py + 30}" font-size="15" font-weight="700" fill="#1E293B">{escape(title)}</text>'
        )
        # Badge
        bw = len(badge) * 6.8 + 16
        s.append(
            f'<rect x="{px + 419 - bw:.1f}" y="{py + 13}" width="{bw:.1f}" height="22" rx="11" fill="{badge_bg}"/>'
        )
        s.append(
            f'<text x="{px + 419 - bw / 2:.1f}" y="{py + 28}" text-anchor="middle" '
            f'font-size="10" font-weight="700" fill="{badge_fg}">{escape(badge)}</text>'
        )

        # Cluster blobs
        s.append(
            f'<ellipse cx="{px + 94}" cy="{py + 136}" rx="54" ry="52" '
            f'fill="#DBEAFE" fill-opacity="0.7" stroke="#3B82F6" stroke-width="1.6"/>'
        )
        s.append(
            f'<ellipse cx="{px + 336}" cy="{py + 136}" rx="54" ry="52" '
            f'fill="#FFEDD5" fill-opacity="0.75" stroke="#F97316" stroke-width="1.6"/>'
        )
        s.append(f'<text x="{px + 94}" y="{py + 76}" text-anchor="middle" font-size="12" font-weight="700" fill="#1D4ED8">Cluster 1</text>')
        s.append(f'<text x="{px + 336}" y="{py + 76}" text-anchor="middle" font-size="12" font-weight="700" fill="#C2410C">Cluster 2</text>')

        if kind in ("single", "complete", "average"):
            for i, (x1, y1) in enumerate(c1_pts):
                for j, (x2, y2) in enumerate(c2_pts):
                    is_min = i == 1 and j == 1
                    is_max = i == 0 and j == 2
                    if kind == "average":
                        s.append(
                            f'<line x1="{px + x1}" y1="{py + y1}" x2="{px + x2}" y2="{py + y2}" '
                            f'stroke="#0D9488" stroke-width="2.0" stroke-opacity="0.72"/>'
                        )
                    elif kind == "single":
                        if is_min:
                            continue
                        s.append(
                            f'<line x1="{px + x1}" y1="{py + y1}" x2="{px + x2}" y2="{py + y2}" '
                            f'stroke="#CBD5E1" stroke-width="1.1" stroke-dasharray="3,3"/>'
                        )
                    elif kind == "complete":
                        if is_max:
                            continue
                        s.append(
                            f'<line x1="{px + x1}" y1="{py + y1}" x2="{px + x2}" y2="{py + y2}" '
                            f'stroke="#CBD5E1" stroke-width="1.1" stroke-dasharray="3,3"/>'
                        )

            if kind == "single":
                x1, y1 = c1_pts[1]
                x2, y2 = c2_pts[1]
                s.append(
                    f'<line x1="{px + x1}" y1="{py + y1}" x2="{px + x2}" y2="{py + y2}" '
                    f'stroke="#E11D48" stroke-width="3.4"/>'
                )
                s.append(
                    f'<rect x="{px + 168}" y="{py + 123}" width="92" height="22" rx="6" fill="#FFF1F2" stroke="#FDA4AF"/>'
                )
                s.append(
                    f'<text x="{px + 214}" y="{py + 138}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#BE123C">min distance</text>'
                )
            elif kind == "complete":
                x1, y1 = c1_pts[0]
                x2, y2 = c2_pts[2]
                s.append(
                    f'<line x1="{px + x1}" y1="{py + y1}" x2="{px + x2}" y2="{py + y2}" '
                    f'stroke="#EA580C" stroke-width="3.4"/>'
                )
                s.append(
                    f'<rect x="{px + 168}" y="{py + 125}" width="96" height="22" rx="6" fill="#FFF7ED" stroke="#FDBA74"/>'
                )
                s.append(
                    f'<text x="{px + 216}" y="{py + 140}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#C2410C">max distance</text>'
                )
            elif kind == "average":
                s.append(
                    f'<rect x="{px + 149}" y="{py + 122}" width="136" height="24" rx="6" fill="#ECFDF5" stroke="#6EE7B7" stroke-width="1.3"/>'
                )
                s.append(
                    f'<text x="{px + 217}" y="{py + 138}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#047857">mean of all 9 pairs</text>'
                )

        else:
            # Centroid / Ward panel
            cx1, cy1 = px + 91, py + 136
            cx2, cy2 = px + 334, py + 137
            s.append(
                f'<line x1="{cx1}" y1="{cy1}" x2="{cx2}" y2="{cy2}" '
                f'stroke="#94A3B8" stroke-width="2.6" stroke-dasharray="6,4"/>'
            )
            # Crosshair markers for centroids
            for cx, cy in [(cx1, cy1), (cx2, cy2)]:
                s.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="#FFFFFF" stroke="#DC2626" stroke-width="2"/>')
                s.append(f'<path d="M {cx-4} {cy-4} L {cx+4} {cy+4} M {cx-4} {cy+4} L {cx+4} {cy-4}" stroke="#DC2626" stroke-width="2"/>')
            s.append(
                f'<rect x="{px + 148}" y="{py + 112}" width="140" height="44" rx="7" fill="#FEF2F2" stroke="#FCA5A5" stroke-width="1.3"/>'
            )
            s.append(
                f'<text x="{px + 218}" y="{py + 131}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#B91C1C">mean(A, B, D) = ???</text>'
            )
            s.append(
                f'<text x="{px + 218}" y="{py + 147}" text-anchor="middle" font-size="10.5" fill="#7F1D1D">no average for labels</text>'
            )

        # Draw student dots on top of lines
        for idx, (x1, y1) in enumerate(c1_pts):
            s.append(f'<circle cx="{px + x1}" cy="{py + y1}" r="6" fill="#2563EB" stroke="#FFFFFF" stroke-width="1.6"/>')
            if kind == "centroid":
                lbl = ["A", "B", "D"][idx]
                dx, dy = [(-15, 4), (9, -8), (-15, 4)][idx]
                s.append(f'<text x="{px + x1 + dx}" y="{py + y1 + dy}" font-size="11" font-weight="700" fill="#1E3A8A">{lbl}</text>')
        for idx, (x2, y2) in enumerate(c2_pts):
            s.append(f'<circle cx="{px + x2}" cy="{py + y2}" r="6" fill="#EA580C" stroke="#FFFFFF" stroke-width="1.6"/>')
            if kind == "centroid":
                lbl = ["C", "E", "F"][idx]
                dx, dy = [(10, 4), (-14, -9), (10, 4)][idx]
                s.append(f'<text x="{px + x2 + dx}" y="{py + y2 + dy}" font-size="11" font-weight="700" fill="#9A3412">{lbl}</text>')

        # Footer explanation box inside panel
        if kind == "single":
            line1 = "Rule: closest single pair between the two groups."
            line2 = "Problem: chaining — chains 98% of students into 1 mega-blob."
        elif kind == "complete":
            line1 = "Rule: farthest single pair between the two groups."
            line2 = "Problem: final 15 merges tie at 1.0 → depends on row order."
        elif kind == "average":
            line1 = "Rule: arithmetic average of all k × l cross-group pairs."
            line2 = "Why it wins: breaks ties into 67 rational heights (r_coph = 0.62)."
        else:
            line1 = "Rule: distance between group means (or SSE variance for Ward)."
            line2 = "Why skipped: survey choices A–F are categories, not numbers."

        s.append(f'<text x="{px + 18}" y="{py + 220}" font-size="12" font-weight="600" fill="#334155">{escape(line1)}</text>')
        s.append(f'<text x="{px + 18}" y="{py + 240}" font-size="11.5" fill="#475569">{escape(line2)}</text>')

    write_and_render("diag02_linkage_methods", s)


def build_silhouette_diagram() -> None:
    w, h = 920, 440
    s = svg_header(w, h, "#FFFFFF")

    s.append(
        '<text x="460" y="36" text-anchor="middle" font-size="20" font-weight="700" fill="#1E293B">'
        'How Silhouette Width s(i) Measures Cluster Fit for Student i</text>'
    )
    s.append(
        '<text x="460" y="60" text-anchor="middle" font-size="13.5" fill="#475569">'
        'Compares how close student i is to their own cluster a(i) versus the nearest neighbouring cluster b(i)</text>'
    )

    # Own cluster (left)
    s.append('<ellipse cx="215" cy="195" rx="135" ry="95" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2"/>')
    s.append('<text x="215" y="90" text-anchor="middle" font-size="14" font-weight="700" fill="#1D4ED8">Own Cluster</text>')

    # Nearest neighbour cluster (middle-right)
    s.append('<ellipse cx="565" cy="195" rx="125" ry="90" fill="#FFF7ED" stroke="#F97316" stroke-width="2"/>')
    s.append('<text x="565" y="90" text-anchor="middle" font-size="14" font-weight="700" fill="#C2410C">Nearest Neighbour Cluster</text>')

    # Farther cluster (far right, faded)
    s.append('<ellipse cx="815" cy="195" rx="75" ry="70" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5" stroke-dasharray="4,4"/>')
    s.append('<text x="815" y="96" text-anchor="middle" font-size="12" font-weight="600" fill="#94A3B8">Far Cluster</text>')
    s.append('<text x="815" y="112" text-anchor="middle" font-size="11" fill="#94A3B8">(ignored by b)</text>')
    for fx, fy in [(790, 175), (835, 185), (812, 225)]:
        s.append(f'<circle cx="{fx}" cy="{fy}" r="5.5" fill="#CBD5E1"/>')

    # Student i and own-cluster peers
    si = (255, 198)
    own_peers = [(145, 160), (195, 145), (145, 225), (210, 250)]
    nbr_peers = [(505, 155), (585, 145), (520, 238), (620, 215)]

    # Draw a(i) lines
    for px, py in own_peers:
        s.append(f'<line x1="{si[0]}" y1="{si[1]}" x2="{px}" y2="{py}" stroke="#2563EB" stroke-width="2.2"/>')
    # Draw b(i) lines
    for px, py in nbr_peers:
        s.append(f'<line x1="{si[0]}" y1="{si[1]}" x2="{px}" y2="{py}" stroke="#EA580C" stroke-width="2.0" stroke-dasharray="6,4"/>')

    # Draw peer dots
    for px, py in own_peers:
        s.append(f'<circle cx="{px}" cy="{py}" r="6.5" fill="#3B82F6" stroke="#FFFFFF" stroke-width="1.5"/>')
    for px, py in nbr_peers:
        s.append(f'<circle cx="{px}" cy="{py}" r="6.5" fill="#F97316" stroke="#FFFFFF" stroke-width="1.5"/>')

    # Student i node (highlighted)
    s.append(f'<circle cx="{si[0]}" cy="{si[1]}" r="13" fill="#1E293B" stroke="#FFFFFF" stroke-width="2.5"/>')
    s.append(f'<text x="{si[0]}" y="{si[1] + 4}" text-anchor="middle" font-size="13" font-weight="700" fill="#FFFFFF">i</text>')

    # Callout badges for a(i) and b(i)
    s.append('<rect x="115" y="185" width="92" height="24" rx="6" fill="#DBEAFE" stroke="#60A5FA"/>')
    s.append('<text x="161" y="201" text-anchor="middle" font-size="12" font-weight="700" fill="#1E40AF">a(i) = mean</text>')

    s.append('<rect x="368" y="176" width="96" height="24" rx="6" fill="#FFEDD5" stroke="#FB923C"/>')
    s.append('<text x="416" y="192" text-anchor="middle" font-size="12" font-weight="700" fill="#9A3412">b(i) = mean</text>')

    # Bottom interpretation scale
    s.append('<rect x="40" y="318" width="840" height="96" rx="10" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.3"/>')
    s.append(
        '<text x="460" y="344" text-anchor="middle" font-size="13.5" font-weight="700" fill="#1E293B">'
        'Formula:   s(i) = [ b(i) − a(i) ] / max{ a(i), b(i) }     (always between −1 and +1)</text>'
    )

    cards = [
        (60, "#FEF2F2", "#FCA5A5", "#B91C1C", "s(i) < 0  (Bad fit)", "a(i) > b(i): closer to neighbours"),
        (330, "#FEFCE8", "#FDE047", "#A16207", "s(i) ≈ 0  (On border)", "a(i) ≈ b(i): sits between 2 clusters"),
        (600, "#ECFDF5", "#6EE7B7", "#047857", "s(i) → +1  (Great fit)", "a(i) ≪ b(i): tight inside own group"),
    ]
    for cx, bg, bd, fg, head, sub in cards:
        s.append(f'<rect x="{cx}" y="356" width="256" height="46" rx="7" fill="{bg}" stroke="{bd}" stroke-width="1.3"/>')
        s.append(f'<text x="{cx + 128}" y="375" text-anchor="middle" font-size="12.5" font-weight="700" fill="{fg}">{escape(head)}</text>')
        s.append(f'<text x="{cx + 128}" y="393" text-anchor="middle" font-size="11.5" fill="#475569">{escape(sub)}</text>')

    write_and_render("diag03_silhouette_explained", s)


def build_cophenetic_diagram() -> None:
    w, h = 980, 490
    s = svg_header(w, h, "#FFFFFF")

    s.append(
        '<text x="490" y="36" text-anchor="middle" font-size="20" font-weight="700" fill="#1E293B">'
        'How Cophenetic Correlation (r_coph) Is Calculated Step by Step</text>'
    )
    s.append(
        '<text x="490" y="60" text-anchor="middle" font-size="13.5" fill="#475569">'
        'Compare all M = n(n − 1)/2 = 33,930 student pairs before and after building the dendrogram (shown with 4 students)</text>'
    )

    # 3 step cards
    cards = [
        (24, 82, 300, 382, "#EFF6FF", "#93C5FD", "Step 1: Original Distances (d)", "#1D4ED8"),
        (340, 82, 300, 382, "#F0FDFA", "#5EEAD4", "Step 2: Tree Merge Heights (c)", "#0F766E"),
        (656, 82, 300, 382, "#F8FAFC", "#CBD5E1", "Step 3: Correlate d and c", "#1E293B"),
    ]
    for cx, cy, cw, ch, bg, bd, title, fg in cards:
        s.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="12" fill="{bg}" stroke="{bd}" stroke-width="1.6"/>')
        s.append(f'<text x="{cx + cw / 2:.1f}" y="{cy + 28}" text-anchor="middle" font-size="14.5" font-weight="700" fill="{fg}">{escape(title)}</text>')

    # Arrows between cards
    for ax in (326, 642):
        s.append(f'<polygon points="{ax},256 {ax+12},264 {ax},272" fill="#475569"/>')

    # --- STEP 1: 4x4 Lower-Triangle Distance Matrix ---
    gx, gy = 78, 146
    cell = 50
    students = ["S1", "S2", "S3", "S4"]
    mat = [
        ["0", "—", "—", "—"],
        ["0.2", "0", "—", "—"],
        ["0.8", "0.8", "0", "—"],
        ["0.8", "0.6", "0.4", "0"],
    ]
    for idx, st in enumerate(students):
        # Column headers
        s.append(f'<text x="{gx + idx * cell + cell / 2:.1f}" y="{gy - 10}" text-anchor="middle" font-size="12" font-weight="700" fill="#334155">{st}</text>')
        # Row headers
        s.append(f'<text x="{gx - 12}" y="{gy + idx * cell + cell / 2 + 4:.1f}" text-anchor="end" font-size="12" font-weight="700" fill="#334155">{st}</text>')

    for r in range(4):
        for c in range(4):
            rx, ry = gx + c * cell, gy + r * cell
            if r == c:
                fill, stroke, tcol = "#E2E8F0", "#CBD5E1", "#64748B"
            elif r > c:
                fill, stroke, tcol = "#DBEAFE", "#2563EB", "#1E40AF"
            else:
                fill, stroke, tcol = "#F8FAFC", "#E2E8F0", "#94A3B8"
            s.append(f'<rect x="{rx}" y="{ry}" width="{cell - 3}" height="{cell - 3}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
            fw = "700" if r > c else "500"
            s.append(f'<text x="{rx + (cell - 3) / 2:.1f}" y="{ry + (cell - 3) / 2 + 4:.1f}" text-anchor="middle" font-size="12" font-weight="{fw}" fill="{tcol}">{mat[r][c]}</text>')

    s.append('<text x="174" y="366" text-anchor="middle" font-size="11.5" font-weight="700" fill="#1D4ED8">Lower triangle = unique pairs</text>')
    s.append('<rect x="44" y="380" width="260" height="44" rx="7" fill="#FFFFFF" stroke="#93C5FD"/>')
    s.append('<text x="174" y="399" text-anchor="middle" font-size="11.5" font-weight="700" fill="#1E293B">d = [0.2, 0.8, 0.8, 0.8, 0.6, 0.4]</text>')
    s.append('<text x="174" y="416" text-anchor="middle" font-size="10.5" fill="#475569">In our dataset: 33,930 values (mean = 0.8021)</text>')
    s.append('<text x="174" y="446" text-anchor="middle" font-size="10.5" fill="#64748B">Upper triangle is identical, so we skip it</text>')

    # --- STEP 2: 4-student Dendrogram -> c ---
    # Tree area inside card 2: x from 375 to 605, y from 140 to 320
    tx = [395, 455, 525, 585]
    # y=315 is h=0.0, y=155 is h=0.8 (200px per 1.0)
    def ty(hv: float) -> float:
        return 315 - hv * 200

    for hv in [0.0, 0.2, 0.4, 0.6, 0.8]:
        yy = ty(hv)
        s.append(f'<line x1="378" y1="{yy:.1f}" x2="606" y2="{yy:.1f}" stroke="#CCFBF1" stroke-width="1"/>')
        s.append(f'<text x="373" y="{yy + 4:.1f}" text-anchor="end" font-size="10.5" fill="#0F766E">{hv:.1f}</text>')

    # S1 & S2 merge at 0.20 -> x=425
    s.append(f'<path d="M {tx[0]} {ty(0):.1f} V {ty(0.2):.1f} H {tx[1]} V {ty(0):.1f}" fill="none" stroke="#0D9488" stroke-width="2.6"/>')
    # S3 & S4 merge at 0.40 -> x=555
    s.append(f'<path d="M {tx[2]} {ty(0):.1f} V {ty(0.4):.1f} H {tx[3]} V {ty(0):.1f}" fill="none" stroke="#0D9488" stroke-width="2.6"/>')
    # (S1,S2) & (S3,S4) merge at 0.75 -> x=490
    s.append(f'<path d="M 425 {ty(0.2):.1f} V {ty(0.75):.1f} H 555 V {ty(0.4):.1f}" fill="none" stroke="#0F766E" stroke-width="2.6"/>')

    s.append(f'<text x="408" y="{ty(0.2) - 6:.1f}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#0F766E">0.20</text>')
    s.append(f'<text x="572" y="{ty(0.4) - 6:.1f}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#0F766E">0.40</text>')
    s.append(f'<text x="490" y="{ty(0.75) - 6:.1f}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#0F766E">0.75</text>')

    for x, st in zip(tx, students):
        s.append(f'<circle cx="{x}" cy="{ty(0):.1f}" r="4.5" fill="#0D9488" stroke="#FFFFFF" stroke-width="1.2"/>')
        s.append(f'<text x="{x}" y="335" text-anchor="middle" font-size="12" font-weight="700" fill="#1E293B">{st}</text>')

    s.append('<text x="490" y="366" text-anchor="middle" font-size="11.5" font-weight="700" fill="#0F766E">Height where each pair first meets</text>')
    s.append('<rect x="360" y="380" width="260" height="44" rx="7" fill="#FFFFFF" stroke="#5EEAD4"/>')
    s.append('<text x="490" y="399" text-anchor="middle" font-size="11.5" font-weight="700" fill="#1E293B">c = [0.2, 0.75, 0.75, 0.75, 0.75, 0.4]</text>')
    s.append('<text x="490" y="416" text-anchor="middle" font-size="10.5" fill="#475569">Same 33,930 pairs, in exact same order</text>')
    s.append('<text x="490" y="446" text-anchor="middle" font-size="10.5" fill="#64748B">In R: cophenetic(hc_average)</text>')

    # --- STEP 3: Scatter + Pearson Correlation ---
    px0, py0, pw, ph = 708, 145, 212, 165
    s.append(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>')
    # Axes inside scatter
    s.append(f'<line x1="{px0 + 28}" y1="{py0 + 18}" x2="{px0 + 28}" y2="{py0 + ph - 24}" stroke="#475569" stroke-width="1.4"/>')
    s.append(f'<line x1="{px0 + 28}" y1="{py0 + ph - 24}" x2="{px0 + pw - 14}" y2="{py0 + ph - 24}" stroke="#475569" stroke-width="1.4"/>')
    s.append(f'<text x="{px0 + pw / 2 + 6:.1f}" y="{py0 + ph - 7}" text-anchor="middle" font-size="10.5" font-weight="600" fill="#475569">Original d</text>')
    s.append(
        f'<text x="{px0 + 13}" y="{py0 + ph / 2:.1f}" text-anchor="middle" font-size="10.5" font-weight="600" fill="#475569" '
        f'transform="rotate(-90 {px0 + 13} {py0 + ph / 2:.1f})">Tree c</text>'
    )
    # Trend line
    s.append(f'<line x1="{px0 + 38}" y1="{py0 + ph - 32}" x2="{px0 + pw - 22}" y2="{py0 + 28}" stroke="#E11D48" stroke-width="2" stroke-dasharray="5,4"/>')
    # Plot the 6 points (d, c)
    pts_dc = [(0.2, 0.2), (0.4, 0.4), (0.6, 0.75), (0.8, 0.75)]
    for dv, cv in pts_dc:
        sx = px0 + 34 + dv * 150
        sy = py0 + ph - 28 - cv * 125
        s.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="5" fill="#2563EB" stroke="#FFFFFF" stroke-width="1.4"/>')

    s.append('<text x="806" y="340" text-anchor="middle" font-size="12" font-weight="700" fill="#1E293B">Pearson Correlation: cor(d, c)</text>')
    s.append('<rect x="676" y="354" width="260" height="58" rx="8" fill="#ECFDF5" stroke="#6EE7B7" stroke-width="1.4"/>')
    s.append('<text x="806" y="376" text-anchor="middle" font-size="13" font-weight="700" fill="#047857">Average (UPGMA): r_coph = 0.6221</text>')
    s.append('<text x="806" y="396" text-anchor="middle" font-size="11" fill="#334155">Complete: 0.5290   |   Single: 0.1409</text>')
    s.append('<text x="806" y="434" text-anchor="middle" font-size="11" font-weight="600" fill="#334155">R: cor(dist_hamming, cophenetic(hc))</text>')

    write_and_render("diag04_cophenetic_calculation", s)


def build_external_val_diagram() -> None:
    w, h = 980, 500
    s = svg_header(w, h, "#FFFFFF")

    s.append(
        '<text x="490" y="36" text-anchor="middle" font-size="20" font-weight="700" fill="#1E293B">'
        'How the 3 External Validation Tests Work (Q6 &amp; S4)</text>'
    )
    s.append(
        '<text x="490" y="60" text-anchor="middle" font-size="13.5" fill="#475569">'
        'Testing whether the 6 clusters differ on variables withheld from clustering: AI Usage (Q6) and Year of Study (S4)</text>'
    )

    cards = [
        (24, 82, 300, 392, "#EFF6FF", "#93C5FD", "1. One-Way ANOVA (Q6)", "#1D4ED8"),
        (340, 82, 300, 392, "#F0FDFA", "#5EEAD4", "2. Kruskal–Wallis H (Q6)", "#0F766E"),
        (656, 82, 300, 392, "#FFF7ED", "#FDBA74", "3. Chi-Square + Monte Carlo (S4)", "#C2410C"),
    ]
    for cx, cy, cw, ch, bg, bd, title, fg in cards:
        s.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="12" fill="{bg}" stroke="{bd}" stroke-width="1.6"/>')
        s.append(f'<text x="{cx + cw / 2:.1f}" y="{cy + 28}" text-anchor="middle" font-size="14" font-weight="700" fill="{fg}">{escape(title)}</text>')

    # --- PANEL 1: ANOVA (Signal vs Noise) ---
    # Plot box
    s.append('<rect x="44" y="128" width="260" height="218" rx="8" fill="#FFFFFF" stroke="#BFDBFE"/>')
    # Overall mean dashed line
    s.append('<line x1="56" y1="226" x2="292" y2="226" stroke="#64748B" stroke-width="1.5" stroke-dasharray="5,4"/>')
    s.append('<text x="290" y="219" text-anchor="end" font-size="10" font-weight="700" fill="#475569">Overall mean = 4.09</text>')

    # 3 sample cluster columns: C5 (low, y=268), C3 (mid, y=232), C2 (high, y=190)
    anova_cols = [
        (96, 268, "C5", "2.85", "#16A34A", [244, 260, 272, 286, 296]),
        (174, 232, "C3", "3.90", "#EA580C", [198, 220, 234, 248, 268]),
        (252, 190, "C2", "4.63", "#7C3AED", [162, 178, 192, 204, 220]),
    ]
    for x, my, lbl, mval, col, pts_y in anova_cols:
        # Spread whisker (within-group noise)
        s.append(f'<line x1="{x}" y1="{min(pts_y)}" x2="{x}" y2="{max(pts_y)}" stroke="{col}" stroke-width="2" stroke-opacity="0.4"/>')
        for py in pts_y:
            s.append(f'<circle cx="{x}" cy="{py}" r="4.5" fill="{col}" fill-opacity="0.75"/>')
        # Mean bar
        s.append(f'<line x1="{x - 16}" y1="{my}" x2="{x + 16}" y2="{my}" stroke="#1E293B" stroke-width="3"/>')
        s.append(f'<text x="{x}" y="328" text-anchor="middle" font-size="11.5" font-weight="700" fill="#1E293B">{lbl} ({mval})</text>')

    # Signal arrow between C5 mean and overall mean
    s.append('<line x1="74" y1="226" x2="74" y2="268" stroke="#DC2626" stroke-width="2"/>')
    s.append('<text x="70" y="250" text-anchor="end" font-size="9.5" font-weight="700" fill="#DC2626">Signal</text>')
    # Noise bracket on C2
    s.append('<text x="272" y="188" font-size="9.5" font-weight="700" fill="#6D28D9">Noise</text>')

    s.append('<text x="174" y="370" text-anchor="middle" font-size="12" font-weight="700" fill="#1E293B">F = Between-group / Within-group</text>')
    s.append('<text x="174" y="390" text-anchor="middle" font-size="11.5" fill="#475569">Compares cluster means (assumes bell curve)</text>')
    s.append('<rect x="44" y="406" width="260" height="48" rx="7" fill="#FFFFFF" stroke="#93C5FD"/>')
    s.append('<text x="174" y="427" text-anchor="middle" font-size="12" font-weight="700" fill="#1D4ED8">F(5, 255) = 2.957,  p = 0.0130</text>')
    s.append('<text x="174" y="445" text-anchor="middle" font-size="10.5" fill="#475569">p &lt; 0.05 → AI usage means differ</text>')

    # --- PANEL 2: Kruskal-Wallis (Ranks) ---
    s.append('<rect x="360" y="128" width="260" height="218" rx="8" fill="#FFFFFF" stroke="#99F6E4"/>')
    s.append('<text x="490" y="152" text-anchor="middle" font-size="11.5" font-weight="700" fill="#0F766E">Step A: Sort &amp; replace days with Ranks</text>')

    # Mapping boxes: Raw days -> Ranks
    raw_items = [("0 d", "Rank ~10"), ("3 d", "Rank ~90"), ("5 d", "Rank ~175"), ("7 d", "Rank ~245")]
    for idx, (raw, rnk) in enumerate(raw_items):
        bx = 372 + idx * 60
        s.append(f'<rect x="{bx}" y="165" width="54" height="26" rx="5" fill="#F1F5F9" stroke="#CBD5E1"/>')
        s.append(f'<text x="{bx + 27}" y="182" text-anchor="middle" font-size="10.5" font-weight="700" fill="#334155">{raw}</text>')
        s.append(f'<line x1="{bx + 27}" y1="193" x2="{bx + 27}" y2="207" stroke="#0D9488" stroke-width="1.6"/>')
        s.append(f'<rect x="{bx}" y="209" width="54" height="26" rx="5" fill="#CCFBF1" stroke="#2DD4BF"/>')
        s.append(f'<text x="{bx + 27}" y="226" text-anchor="middle" font-size="10" font-weight="700" fill="#0F766E">{rnk}</text>')

    s.append('<text x="490" y="260" text-anchor="middle" font-size="11.5" font-weight="700" fill="#0F766E">Step B: Compare average cluster ranks</text>')
    # Rank number line (1 to 263)
    s.append('<line x1="382" y1="300" x2="598" y2="300" stroke="#475569" stroke-width="2"/>')
    s.append('<line x1="490" y1="274" x2="490" y2="324" stroke="#94A3B8" stroke-width="1.3" stroke-dasharray="4,3"/>')
    s.append('<text x="490" y="271" text-anchor="middle" font-size="9.5" fill="#64748B">Mid (~131)</text>')
    s.append('<text x="382" y="335" text-anchor="middle" font-size="10" fill="#64748B">Rank 1</text>')
    s.append('<text x="598" y="335" text-anchor="middle" font-size="10" fill="#64748B">Rank 263</text>')

    for rx, rlbl, rcol in [(415, "C5", "#16A34A"), (482, "C3", "#EA580C"), (555, "C2", "#7C3AED")]:
        s.append(f'<circle cx="{rx}" cy="300" r="7" fill="{rcol}" stroke="#FFFFFF" stroke-width="1.5"/>')
        s.append(f'<text x="{rx}" y="287" text-anchor="middle" font-size="10.5" font-weight="700" fill="{rcol}">{rlbl}</text>')

    s.append('<text x="490" y="370" text-anchor="middle" font-size="12" font-weight="700" fill="#1E293B">Non-parametric (no bell curve needed)</text>')
    s.append('<text x="490" y="390" text-anchor="middle" font-size="11.5" fill="#475569">Uses ranks instead of raw values (robust)</text>')
    s.append('<rect x="360" y="406" width="260" height="48" rx="7" fill="#FFFFFF" stroke="#5EEAD4"/>')
    s.append('<text x="490" y="427" text-anchor="middle" font-size="12" font-weight="700" fill="#0F766E">H = 14.144,  df = 5,  p = 0.0147</text>')
    s.append('<text x="490" y="445" text-anchor="middle" font-size="10.5" fill="#475569">p &lt; 0.05 → confirms ANOVA result</text>')

    # --- PANEL 3: Chi-Square + Monte Carlo ---
    s.append('<rect x="676" y="128" width="260" height="218" rx="8" fill="#FFFFFF" stroke="#FED7AA"/>')
    s.append('<text x="806" y="150" text-anchor="middle" font-size="11" font-weight="700" fill="#C2410C">6 × 5 Table: Observed vs. Expected</text>')

    # Highlight example cell (C5 x Grad/Master)
    s.append('<rect x="692" y="160" width="228" height="44" rx="6" fill="#FFF7ED" stroke="#FB923C"/>')
    s.append('<text x="806" y="178" text-anchor="middle" font-size="10.5" font-weight="700" fill="#9A3412">Example cell (C5 × Grad/Master):</text>')
    s.append('<text x="806" y="195" text-anchor="middle" font-size="10.5" fill="#334155">Observed = 6 (31.6%)  vs.  Expected ≈ 0.9</text>')

    s.append('<text x="806" y="224" text-anchor="middle" font-size="11" font-weight="700" fill="#C2410C">Monte Carlo: 10,000 random shuffles</text>')
    # Mini histogram of random chi-square values (left-skewed around df=20)
    s.append('<line x1="692" y1="312" x2="922" y2="312" stroke="#475569" stroke-width="1.5"/>')
    bars = [12, 34, 52, 58, 48, 32, 18, 9, 4, 2]
    for bi, bh in enumerate(bars):
        bx = 696 + bi * 14
        s.append(f'<rect x="{bx}" y="{312 - bh}" width="11" height="{bh}" rx="2" fill="#FDBA74" stroke="#EA580C" stroke-width="0.8"/>')
    s.append('<text x="765" y="328" text-anchor="middle" font-size="9.5" fill="#64748B">10,000 random χ²</text>')

    # Real chi-square spike far to the right
    s.append('<line x1="898" y1="242" x2="898" y2="312" stroke="#DC2626" stroke-width="2.6"/>')
    s.append('<circle cx="898" cy="242" r="4.5" fill="#DC2626"/>')
    s.append('<text x="894" y="236" text-anchor="end" font-size="10" font-weight="700" fill="#DC2626">Our χ² = 76.66</text>')
    s.append('<text x="898" y="328" text-anchor="middle" font-size="9.5" font-weight="700" fill="#DC2626">0 / 10,000 ≥ this</text>')

    s.append('<text x="806" y="370" text-anchor="middle" font-size="12" font-weight="700" fill="#1E293B">χ² = Σ (Observed − Expected)² / Expected</text>')
    s.append('<text x="806" y="390" text-anchor="middle" font-size="11.5" fill="#475569">Shuffles fix small-cell bias (12 Grad students)</text>')
    s.append('<rect x="676" y="406" width="260" height="48" rx="7" fill="#FFFFFF" stroke="#FDBA74"/>')
    s.append('<text x="806" y="427" text-anchor="middle" font-size="12" font-weight="700" fill="#C2410C">χ² = 76.659,  p = 0.0001</text>')
    s.append('<text x="806" y="445" text-anchor="middle" font-size="10.5" fill="#475569">p &lt; 0.05 → study year strongly linked</text>')

    write_and_render("diag05_external_validation_methods", s)


GENERATORS = {
    "dendrogram": build_dendrogram_diagram,
    "linkage": build_linkage_diagram,
    "silhouette": build_silhouette_diagram,
    "cophenetic": build_cophenetic_diagram,
    "external_val": build_external_val_diagram,
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate educational diagrams for STATS_EXPLAINED.md.")
    parser.add_argument(
        "diagrams",
        nargs="*",
        choices=[*GENERATORS.keys(), "all"],
        default=["all"],
        help="Specific diagram(s) to generate, or 'all' (default).",
    )
    args = parser.parse_args()
    targets = list(GENERATORS.keys()) if "all" in args.diagrams else args.diagrams
    for name in targets:
        GENERATORS[name]()
