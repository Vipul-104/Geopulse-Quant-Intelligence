"""
GeoPulse – PDF Export v4 (white body, professional layout)
"""
from __future__ import annotations
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable, KeepTogether
)
from src.models import IntelligenceBriefing, RiskLevel, PriceDirection

# ── Palette (print-safe, white background) ────────────────────────────────────
BG      = colors.white
SURFACE = colors.HexColor("#F8F8F8")
BORDER  = colors.HexColor("#DDDDDD")
MUTED   = colors.HexColor("#555555")
NAVY    = colors.HexColor("#1A1A2E")
BLUE    = colors.HexColor("#0055AA")
GREEN   = colors.HexColor("#1A7A1A")
ORANGE  = colors.HexColor("#C85A00")
RED     = colors.HexColor("#C0003C")
WHITE   = colors.white
BLACK   = colors.HexColor("#111111")

RISK_COLORS = {
    RiskLevel.CRITICAL: colors.HexColor("#E24B4A"),
    RiskLevel.HIGH:     colors.HexColor("#C85A00"),
    RiskLevel.MODERATE: colors.HexColor("#1A7A1A"),
    RiskLevel.LOW:      colors.HexColor("#0055AA"),
    RiskLevel.MINIMAL:  colors.HexColor("#888780"),
}

RISK_BG = {
    RiskLevel.CRITICAL: colors.HexColor("#FFF0F0"),
    RiskLevel.HIGH:     colors.HexColor("#FFF5EE"),
    RiskLevel.MODERATE: colors.HexColor("#F2FFF2"),
    RiskLevel.LOW:      colors.HexColor("#F0F5FF"),
    RiskLevel.MINIMAL:  colors.HexColor("#F5F5F5"),
}

DIRECTION_LABEL = {
    PriceDirection.SHARP_RISE:    "++ SHARP RISE",
    PriceDirection.MODERATE_RISE: "+  MOD RISE",
    PriceDirection.STABLE:        "-> STABLE",
    PriceDirection.MODERATE_FALL: "-  MOD FALL",
    PriceDirection.SHARP_FALL:    "-- SHARP FALL",
}

def _vc(v: int):
    if v <= 33: return GREEN
    if v <= 66: return ORANGE
    return RED

def _vc_bg(v: int):
    if v <= 33: return colors.HexColor("#F2FFF2")
    if v <= 66: return colors.HexColor("#FFF8F2")
    return colors.HexColor("#FFF2F5")

# ── Styles ────────────────────────────────────────────────────────────────────
def S():
    return {
        "h2":    ParagraphStyle("h2",  fontSize=10, textColor=BLUE,   fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3),
        "h3":    ParagraphStyle("h3",  fontSize=7.5,textColor=MUTED,  fontName="Helvetica-Bold", spaceBefore=5, spaceAfter=2),
        "body":  ParagraphStyle("b",   fontSize=8,  textColor=BLACK,  fontName="Helvetica",      spaceAfter=2,  leading=11),
        "muted": ParagraphStyle("m",   fontSize=7,  textColor=MUTED,  fontName="Helvetica",      spaceAfter=1,  leading=10),
        "green": ParagraphStyle("g",   fontSize=7.5,textColor=GREEN,  fontName="Helvetica",      spaceAfter=1),
        "red":   ParagraphStyle("r",   fontSize=7.5,textColor=RED,    fontName="Helvetica",      spaceAfter=1),
        "blue":  ParagraphStyle("c",   fontSize=7.5,textColor=BLUE,   fontName="Helvetica",      spaceAfter=1),
        "orange":ParagraphStyle("y",   fontSize=8,  textColor=ORANGE, fontName="Helvetica-Bold", spaceAfter=1),
        "ital":  ParagraphStyle("i",   fontSize=7.5,textColor=MUTED,  fontName="Helvetica-Oblique", spaceAfter=2),
        "disc":  ParagraphStyle("d",   fontSize=6.5,textColor=MUTED,  fontName="Helvetica-Oblique"),
        "head":  ParagraphStyle("hd",  fontSize=9,  textColor=BLACK,  fontName="Helvetica-Bold", spaceAfter=4, leading=13),
        "exec":  ParagraphStyle("ex",  fontSize=8,  textColor=BLACK,  fontName="Helvetica",      spaceAfter=2, leading=12),
        "sub":   ParagraphStyle("sb",  fontSize=7,  textColor=MUTED,  fontName="Helvetica",      spaceAfter=4),
        "white": ParagraphStyle("w",   fontSize=8,  textColor=WHITE,  fontName="Helvetica",      spaceAfter=2, leading=11),
        "whiteb":ParagraphStyle("wb",  fontSize=9,  textColor=WHITE,  fontName="Helvetica-Bold", spaceAfter=2),
        "whitem":ParagraphStyle("wm",  fontSize=7,  textColor=colors.HexColor("#AAAAAA"), fontName="Helvetica", spaceAfter=1),
    }

# ── Page callback ─────────────────────────────────────────────────────────────
def _page(canvas, doc):
    canvas.saveState()
    # White page
    canvas.setFillColor(WHITE)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    # Dark navy header bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1]-22*mm, A4[0], 22*mm, fill=1, stroke=0)
    # Header text
    canvas.setFillColor(BLUE)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(15*mm, A4[1]-10*mm, "GEOPULSE QUANT INTELLIGENCE")
    canvas.setFillColor(colors.HexColor("#AAAAAA"))
    canvas.setFont("Helvetica", 7)
    canvas.drawString(15*mm, A4[1]-17*mm, "INTERNAL USE ONLY  |  CLASSIFIED RISK ARCHIVE")
    canvas.drawRightString(A4[0]-15*mm, A4[1]-17*mm, doc.briefing_ts)
    # Footer
    canvas.setFillColor(colors.HexColor("#888888"))
    canvas.setFont("Helvetica", 6)
    canvas.drawCentredString(A4[0]/2, 8*mm, f"Page {doc.page}  |  AI-generated — verify before acting")
    canvas.restoreStore()

def _page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(WHITE)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1]-22*mm, A4[0], 22*mm, fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(15*mm, A4[1]-10*mm, "GEOPULSE QUANT INTELLIGENCE")
    canvas.setFillColor(colors.HexColor("#AAAAAA"))
    canvas.setFont("Helvetica", 7)
    canvas.drawString(15*mm, A4[1]-17*mm, "INTERNAL USE ONLY  |  CLASSIFIED RISK ARCHIVE")
    canvas.drawRightString(A4[0]-15*mm, A4[1]-17*mm, doc.briefing_ts)
    canvas.setFillColor(colors.HexColor("#888888"))
    canvas.setFont("Helvetica", 6)
    canvas.drawCentredString(A4[0]/2, 8*mm, f"Page {doc.page}  |  AI-generated — verify before acting")
    canvas.restoreState()

# ── Helper boxes ──────────────────────────────────────────────────────────────
def _surface_box(content_rows, col_w, stroke_col=None, fill_col=None):
    t = Table(content_rows, colWidths=[col_w])
    style = [
        ("BACKGROUND",    (0,0),(-1,-1), fill_col or SURFACE),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
    ]
    if stroke_col:
        style += [
            ("BOX",        (0,0),(-1,-1), 0.5, stroke_col),
            ("LINEBEFORE", (0,0),(0,-1),  3,   stroke_col),
        ]
    t.setStyle(TableStyle(style))
    return t

# ── Main ──────────────────────────────────────────────────────────────────────
def generate_briefing_pdf(briefing: IntelligenceBriefing) -> bytes:
    buf  = io.BytesIO()
    W, H = A4
    M    = 15*mm
    BW   = W - 2*M
    s    = S()

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=M, rightMargin=M,
        topMargin=28*mm, bottomMargin=18*mm,
    )
    doc.briefing_ts = briefing.timestamp[:19].replace("T", "  ")

    geo  = briefing.geopolitical_analysis
    comm = briefing.commodity_analysis
    rc   = RISK_COLORS.get(geo.overall_risk_level, MUTED)
    rb   = RISK_BG.get(geo.overall_risk_level, SURFACE)

    story = []

    # Timestamp + headline
    story.append(Paragraph(doc.briefing_ts, s["sub"]))
    story.append(Paragraph(f"<b>INCOMING HEADLINE</b>", s["h3"]))
    story.append(Paragraph(briefing.headline, s["head"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=5))

    # Executive summary
    story.append(KeepTogether([
        _surface_box([
            [Paragraph(
                f'<font color="{rc.hexval()}"><b>EXECUTIVE SUMMARY  |  '
                f'RISK: {geo.overall_risk_level.value}  |  '
                f'SCORE: {geo.risk_score}/100</b></font>', s["body"])],
            [Paragraph(briefing.executive_summary, s["exec"])],
        ], BW, stroke_col=rc, fill_col=rb),
        Spacer(1, 8),
    ]))

    # KPI row
    kpis = [
        ("RISK SCORE",     f"{geo.risk_score}/100",                    rc),
        ("ESCALATION",     f"{geo.escalation_probability_pct}%",       ORANGE),
        ("SUPPLY DISRUPT", comm.supply_disruption_severity.value,       RISK_COLORS.get(comm.supply_disruption_severity, MUTED)),
        ("DISRUPT DAYS",   f"{comm.estimated_disruption_duration_days}d", BLUE),
    ]
    kw = BW / 4 - 1.5*mm
    kpi_t = Table(
        [[Paragraph(
            f'<font color="#555555"><b>{lb}</b></font><br/>'
            f'<font color="{col.hexval()}" size="14"><b>{val}</b></font>',
            s["body"])
          for lb, val, col in kpis]],
        colWidths=[kw]*4,
    )
    kpi_t.setStyle(TableStyle(
        [("BACKGROUND", (0,0),(-1,-1), WHITE)] +
        [("BOX", (i,0),(i,0), 1.5, kpis[i][2]) for i in range(4)] +
        [
            ("TOPPADDING",    (0,0),(-1,-1), 8),
            ("BOTTOMPADDING", (0,0),(-1,-1), 8),
            ("LEFTPADDING",   (0,0),(-1,-1), 8),
            ("RIGHTPADDING",  (0,0),(-1,-1), 8),
            ("INNERGRID",     (0,0),(-1,-1), 0, colors.transparent),
        ]
    ))
    story.append(kpi_t)
    story.append(Spacer(1, 10))

    # GEO SECTION
    story.append(Paragraph("GEOPOLITICAL RISK MATRIX", s["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BLUE, spaceAfter=4))
    story.append(Paragraph(
        f'Precedent: <font color="{ORANGE.hexval()}"><b>'
        f'{geo.historical_precedent_event} ({geo.historical_precedent_year or ""})'
        f'</b></font>  &nbsp;&nbsp; '
        f'Escalation: <font color="{ORANGE.hexval()}"><b>{geo.escalation_probability_pct}%</b></font>',
        s["body"]))

    story.append(Paragraph("KEY PARALLELS", s["h3"]))
    for p in geo.key_parallels:
        story.append(Paragraph(f"+ {p}", s["green"]))

    story.append(Paragraph("STRUCTURAL DIFFERENCES", s["h3"]))
    for d in geo.structural_differences:
        story.append(Paragraph(f"- {d}", s["red"]))

    story.append(Paragraph("ACTORS", s["h3"]))
    story.append(Paragraph("  |  ".join(geo.geopolitical_actors), s["blue"]))

    story.append(Paragraph("CHOKE POINTS", s["h3"]))
    story.append(Paragraph("  |  ".join(geo.choke_points_at_risk), s["red"]))

    story.append(Spacer(1, 4))
    story.append(_surface_box([[Paragraph(geo.analyst_note, s["ital"])]], BW, stroke_col=BORDER))
    story.append(Spacer(1, 10))

    # COMMODITY TABLE
    story.append(Paragraph("COMMODITY IMPACT TABLE", s["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=ORANGE, spaceAfter=4))

    for ci in comm.commodity_impacts:
        vc   = _vc(ci.volatility_index)
        vcb  = _vc_bg(ci.volatility_index)
        vhx  = vc.hexval()
        arr  = DIRECTION_LABEL.get(ci.price_direction, "->")
        cw1, cw2 = BW * 0.6, BW * 0.4

        card = Table([
            [Paragraph(f'<font color="{vhx}"><b>{ci.name}</b></font>', s["body"]),
             Paragraph(f'<font color="#888888">{ci.ticker_hint}  |  Conf: {ci.confidence.value}</font>', s["muted"])],
            [Paragraph(
                f'<font color="#555">{arr}</font>  '
                f'<font color="{vhx}"><b>{ci.expected_move_pct_min:+.1f}% '
                f'to {ci.expected_move_pct_max:+.1f}%</b></font>  '
                f'<font color="#888">(mid {ci.expected_move_pct_mid:+.1f}%)</font>',
                s["body"]), ""],
            [Paragraph(
                f'<font color="#555">Vol: <b>{ci.volatility_index}/100</b>  '
                f'Hist avg: <b>{ci.historical_avg_move_pct:+.1f}%</b>  '
                f'Elasticity: <b>{ci.supply_elasticity_score}/100</b></font>',
                s["muted"]), ""],
            [Paragraph(ci.supply_chain_impact, s["muted"]), ""],
        ], colWidths=[cw1, cw2])

        card.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), vcb),
            ("BOX",           (0,0),(-1,-1), 0.5, vc),
            ("LINEBEFORE",    (0,0),(0,-1),  3,   vc),
            ("SPAN",          (0,1),(1,1)),
            ("SPAN",          (0,2),(1,2)),
            ("SPAN",          (0,3),(1,3)),
            ("TOPPADDING",    (0,0),(-1,-1), 4),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
            ("LEFTPADDING",   (0,0),(-1,-1), 6),
            ("RIGHTPADDING",  (0,0),(-1,-1), 6),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
            ("ALIGN",         (1,0),(1,0),   "RIGHT"),
        ]))
        story.append(KeepTogether([card, Spacer(1, 5)]))

    # TAIL RISK
    story.append(Spacer(1, 4))
    story.append(KeepTogether([
        _surface_box([[Paragraph(
            f'<font color="{RED.hexval()}"><b>TAIL RISK:</b></font>  '
            f'<font color="#111">{comm.tail_risk_scenario}</font>',
            s["body"]
        )]], BW, stroke_col=RED, fill_col=colors.HexColor("#FFF0F3")),
        Spacer(1, 6),
    ]))

    # TRADING CONSIDERATIONS
    story.append(Paragraph("TRADING CONSIDERATIONS", s["h3"]))
    for tc in comm.trading_considerations:
        story.append(Paragraph(f"• {tc}", s["muted"]))

    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Paragraph(briefing.confidence_disclaimer, s["disc"]))

    doc.build(story, onFirstPage=_page, onLaterPages=_page)
    buf.seek(0)
    return buf.read()