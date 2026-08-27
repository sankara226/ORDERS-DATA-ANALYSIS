"""Generate the polished PDF business case-study at docs/project_resume.pdf.

Run standalone after src/main.py has produced outputs/dashboard.png and
outputs/figures/*.png, since this script embeds those images directly.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
DASHBOARD_PATH = PROJECT_ROOT / "outputs" / "dashboard.png"
OUTPUT_PATH = PROJECT_ROOT / "docs" / "project_resume.pdf"

INK = colors.HexColor("#1F2937")
MUTED = colors.HexColor("#6B7280")
ACCENT = colors.HexColor("#2E5EAA")
RULE = colors.HexColor("#D1D5DB")

PAGE_SIZE = A4
MARGIN = 2.4 * cm

REPORT_TITLE = "Orders Analysis: A Descriptive Case Study"
REPORT_DATE = "August 2026"
REPORT_SOURCE = "github.com/sankara226/ORDERS-DATA-ANALYSIS"


def _build_styles() -> dict:
    base = getSampleStyleSheet()
    styles = {
        "CoverTitle": ParagraphStyle(
            "CoverTitle", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=28, leading=34, textColor=INK, spaceAfter=12,
        ),
        "CoverPitch": ParagraphStyle(
            "CoverPitch", parent=base["Normal"], fontName="Helvetica",
            fontSize=14, leading=20, textColor=MUTED, spaceAfter=6,
        ),
        "CoverMeta": ParagraphStyle(
            "CoverMeta", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=15, textColor=MUTED,
        ),
        "H1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=17, leading=21, textColor=INK, spaceBefore=18, spaceAfter=10,
        ),
        "H2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=12.5, leading=16, textColor=ACCENT, spaceBefore=12, spaceAfter=6,
        ),
        "Body": ParagraphStyle(
            "Body", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.3, leading=15.5, textColor=INK, spaceAfter=9,
            alignment=4,  # justified
        ),
        "Caption": ParagraphStyle(
            "Caption", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=9, leading=12, textColor=MUTED, spaceAfter=14, alignment=1,
        ),
    }
    return styles


def _header_footer(canvas, doc) -> None:
    canvas.saveState()
    width, height = PAGE_SIZE

    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.6)

    if doc.page > 1:
        canvas.line(MARGIN, height - 1.4 * cm, width - MARGIN, height - 1.4 * cm)
        canvas.setFont("Helvetica", 8.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN, height - 1.2 * cm, "Orders Analysis — Project Case Study")
        canvas.drawRightString(width - MARGIN, height - 1.2 * cm, REPORT_SOURCE)

    canvas.line(MARGIN, 1.5 * cm, width - MARGIN, 1.5 * cm)
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, 1.1 * cm, REPORT_DATE)
    canvas.drawRightString(width - MARGIN, 1.1 * cm, f"Page {doc.page}")

    canvas.restoreState()


def _fitted_image(path: Path, max_width: float, max_height: float) -> Image:
    img = Image(str(path))
    ratio = min(max_width / img.imageWidth, max_height / img.imageHeight)
    img.drawWidth = img.imageWidth * ratio
    img.drawHeight = img.imageHeight * ratio
    return img


def build_pdf() -> None:
    styles = _build_styles()
    content_width = PAGE_SIZE[0] - 2 * MARGIN

    doc = BaseDocTemplate(
        str(OUTPUT_PATH),
        pagesize=PAGE_SIZE,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title=REPORT_TITLE,
    )
    frame = Frame(MARGIN, MARGIN, content_width, PAGE_SIZE[1] - 2 * MARGIN, id="main")
    doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=_header_footer)])

    story = []

    # --- Cover -----------------------------------------------------------
    story.append(Spacer(1, 5 * cm))
    story.append(Paragraph(REPORT_TITLE, styles["CoverTitle"]))
    story.append(Paragraph(
        "How a 368-row French retail export, full of inconsistent spellings and "
        "broken values, became a clean, chart-backed read on where order value "
        "actually comes from.",
        styles["CoverPitch"],
    ))
    story.append(Spacer(1, 2.5 * cm))
    story.append(Paragraph(f"Date: {REPORT_DATE}", styles["CoverMeta"]))
    story.append(Paragraph(f"Source: {REPORT_SOURCE}", styles["CoverMeta"]))
    story.append(Paragraph("Type: Descriptive analytics / data visualization case study", styles["CoverMeta"]))
    story.append(PageBreak())

    # --- Executive summary -------------------------------------------------
    story.append(Paragraph("Executive Summary", styles["H1"]))
    story.append(Paragraph(
        "This project takes a messy, real-world-style orders dataset — 368 rows spanning "
        "six product categories and seven French regions over thirteen months — and turns "
        "it into a trustworthy picture of where order value comes from. After cleaning, "
        "351 orders remained, worth €153,169 in total. The headline finding is that price, "
        "not order quantity, is the dominant driver of order value, and that this holds "
        "fairly evenly across a product mix where no single category dominates. The dataset "
        "also carries real data-quality scars worth knowing about before anyone acts on it: "
        "roughly 3.7% of orders sit outside a normal price range, and a genuine calculation "
        "bug in the original cleaning logic was found and corrected during this project, "
        "changing the category revenue totals by a meaningful margin. What follows explains "
        "how the data was cleaned, what it shows, and what a reasonable next step looks like.",
        styles["Body"],
    ))

    # --- Business context ---------------------------------------------------
    story.append(Paragraph("Business Context", styles["H1"]))
    story.append(Paragraph(
        "Picture a retail operations team that has just been handed a year's worth of order "
        "exports from a system that was clearly never designed with analysis in mind: region "
        "and category names typed by hand in at least three different conventions, prices "
        "recorded with stray minus signs and comma decimals, and a meaningful share of rows "
        "missing values entirely. Before anyone can answer a basic question — which category "
        "sells best, which region prices highest, whether order value is trending up or down "
        "— someone has to make the data trustworthy enough to answer those questions at all. "
        "That is the problem this project addresses: not building a predictive model, but "
        "establishing a clean, defensible baseline that a category manager or regional lead "
        "could actually use to make a call.",
        styles["Body"],
    ))

    # --- Methodology ---------------------------------------------------------
    story.append(Paragraph("Methodology", styles["H1"]))
    story.append(Paragraph(
        "The work followed four stages: cleaning, transformation, descriptive analysis, and "
        "visualization. Cleaning started with a full data-quality profile — missing-value "
        "rates ran as high as 27% in the raw order-amount column and 13% in order status — "
        "followed by removing 17 exact duplicate rows. Categorical fields (product, category, "
        "region, status) were normalized by stripping whitespace and accents and collapsing "
        "known abbreviations, since the same category could appear as \"Électronique\", "
        "\"electro\", or \"ÉLECTRONIQUE\" depending on who entered it. Prices and quantities "
        "were parsed out of inconsistent string formats (comma decimals, currency symbols, "
        "stray minus signs) into proper numeric types, and order value was recomputed from "
        "price times quantity rather than trusted from the dirty source column, which turned "
        "out to matter: the original fill-in logic filled order value independently of price "
        "and quantity, which silently broke that relationship for about 15% of rows once "
        "missing values were imputed. That bug was caught and fixed during this project, "
        "and it changes the category totals reported here versus a naive first pass. Once the "
        "data was consistent, descriptive analysis covered category and regional aggregation, "
        "IQR-based outlier detection on price, and a full correlation pass across the numeric "
        "fields, all of which fed directly into the five charts that follow.",
        styles["Body"],
    ))
    story.append(PageBreak())

    # --- Key findings ---------------------------------------------------------
    story.append(Paragraph("Key Findings", styles["H1"]))

    story.append(Paragraph("1. Category performance is broad-based, not top-heavy", styles["H2"]))
    story.append(_fitted_image(FIGURES_DIR / "02_comparison_by_categorie.png", content_width, 8.5 * cm))
    story.append(Paragraph("Total order value by category, sorted descending.", styles["Caption"]))
    story.append(Paragraph(
        "Toys lead at €33,293 in total order value, but the gap to the lowest category, "
        "clothing at €16,556, is real without being dramatic — every category in between "
        "sits within a fairly narrow band. There is no single category carrying the business; "
        "a strategy built around \"protect the top performer\" would be missing five other "
        "categories doing comparable work.",
        styles["Body"],
    ))

    story.append(Paragraph("2. Most orders are modest, with a long tail of large ones", styles["H2"]))
    story.append(_fitted_image(FIGURES_DIR / "01_distribution_montant_commande.png", content_width, 8.5 * cm))
    story.append(Paragraph("Distribution of order value across all cleaned orders.", styles["Caption"]))
    story.append(Paragraph(
        "The distribution is right-skewed, with a skew coefficient of 1.95. Most orders fall "
        "between €100 and €500, but a meaningful tail stretches out toward €2,300. Reporting "
        "a single average order value would flatter the typical customer's spend; the median "
        "(€354) is a far more honest read on what most orders actually look like.",
        styles["Body"],
    ))
    story.append(PageBreak())

    story.append(Paragraph("3. Regional pricing is not uniform", styles["H2"]))
    story.append(_fitted_image(FIGURES_DIR / "03_dispersion_by_region.png", content_width, 8.5 * cm))
    story.append(Paragraph("Unit price dispersion by region; red points mark IQR outliers.", styles["Caption"]))
    story.append(Paragraph(
        "Average unit price ranges from €106.60 in Bretagne down to €77.43 in "
        "Hauts-de-France — a spread of roughly 27%. Thirteen orders, 3.7% of the cleaned "
        "dataset, fall outside the normal IQR range on price, and they are not evenly spread: "
        "Nouvelle-Aquitaine and Île-de-France carry more than their share. That clustering is "
        "worth a manual look before anyone treats regional averages as directly comparable.",
        styles["Body"],
    ))

    story.append(Paragraph("4. Price, not quantity, drives order value", styles["H2"]))
    story.append(_fitted_image(FIGURES_DIR / "04_correlation_heatmap.png", content_width, 8.5 * cm))
    story.append(Paragraph("Correlation matrix across numeric order fields.", styles["Caption"]))
    story.append(Paragraph(
        "Unit price correlates with order value at r = 0.81, while quantity ordered "
        "correlates at a considerably weaker r = 0.52. In practical terms, orders get bigger "
        "mostly because items cost more, not because customers buy more of them in one go. "
        "Any lever aimed at growing order value should start with pricing and product mix "
        "before it starts with basket size.",
        styles["Body"],
    ))
    story.append(PageBreak())

    story.append(Paragraph("5. Revenue has two clear spikes against an otherwise steady baseline", styles["H2"]))
    story.append(_fitted_image(FIGURES_DIR / "05_trend_monthly_revenue.png", content_width, 8.5 * cm))
    story.append(Paragraph("Total order value by month (final month is partial).", styles["Caption"]))
    story.append(Paragraph(
        "Most months sit in a €9,000–€12,600 band, but May 2025 (€15,467) and January 2026 "
        "(€17,367) break well above it. February 2026 appears to fall off a cliff, but that "
        "month only has six orders on record in this export and should be read as incomplete "
        "data, not a real decline. The two genuine spikes are worth investigating against "
        "whatever promotional or seasonal calendar the business was running at the time.",
        styles["Body"],
    ))

    # --- Recommendations ----------------------------------------------------
    story.append(Paragraph("Recommendations", styles["H1"]))
    story.append(Paragraph(
        "First, treat pricing and product mix as the primary levers for order value, not "
        "basket size — the correlation gap between price and quantity is wide enough that a "
        "campaign built around \"buy more items per order\" is chasing the weaker signal. "
        "Second, run a manual audit of the thirteen flagged price outliers and the regional "
        "clustering behind them before using regional averages in any pricing decision; three "
        "or four bad rows in a dataset this size can meaningfully shift a regional mean. "
        "Third, before extending this analysis further, close the data-entry gaps at the "
        "source — the same category or region typed four different ways, and order amounts "
        "that don't match price times quantity, are cleanup costs that recur every time this "
        "export is pulled, and they are cheaper to fix upstream than downstream.",
        styles["Body"],
    ))

    # --- Technical appendix ---------------------------------------------------
    story.append(Paragraph("Technical Appendix", styles["H1"]))
    story.append(Paragraph(
        "Built in Python 3.9+ with pandas and numpy for cleaning and aggregation, matplotlib "
        "and seaborn for all charts, and ReportLab for this document. The dataset totals 368 "
        "raw rows and 10 raw columns, reduced to 351 rows and 13 columns after deduplication "
        "and feature derivation (order value, and year/month/day extracted from the sale "
        "date). Known limitations: missing categorical and numeric values were filled using "
        "the column mode, which is a defensible default but not the most precise option "
        "available; a group-aware fill (e.g. by product or category) would likely produce "
        "tighter estimates. A follow-up data-quality audit could still usefully investigate "
        "the thirteen flagged price outliers row-by-row, confirm whether the May 2025 and "
        "January 2026 spikes correspond to known promotional periods, and check whether the "
        "133 orders marked \"cancelled\" or \"returned\" — 38% of the cleaned dataset — "
        "should be excluded from revenue totals rather than counted alongside completed "
        "orders, since the figures in this report include them all.",
        styles["Body"],
    ))

    # --- Closing ---------------------------------------------------------
    story.append(Paragraph("Closing", styles["H1"]))
    story.append(Paragraph(
        "The most useful part of this project wasn't the charts — it was catching that the "
        "original cleaning logic quietly broke the price-times-quantity relationship for one "
        "in seven rows, and that a handful of price outliers cluster in specific regions "
        "rather than scattering randomly. Those are exactly the kind of issues that don't show "
        "up until someone actually sits with the data end to end. The next version of this "
        "project should push further into the data-quality side: source-level validation, a "
        "smarter imputation strategy, and a closer look at whether cancelled and returned "
        "orders belong in the same revenue figure as completed ones.",
        styles["Body"],
    ))

    doc.build(story)


if __name__ == "__main__":
    build_pdf()
