import markdown
from xhtml2pdf import pisa
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(BASE, "dossier")
AILOG = os.path.join(BASE, "ai-log", "ai-usage-log.md")
ASSUMPTIONS = os.path.join(BASE, "assumptions.md")

ORDER = [
    ("dossier/part-a1-brd.md", "Part A.1 - Business Requirements Document"),
    ("dossier/part-a2-prd.md", "Part A.2 - Product Requirements Document"),
    ("dossier/part-a3-frd.md", "Part A.3 - Functional Requirements Document"),
    ("dossier/part-a4-wbs.md", "Part A.4 - Work Breakdown Structure"),
    ("dossier/part-b0-conflicts.md", "Part B.0 - The Stakeholder Conflicts"),
    ("dossier/part-b1-quality-attributes.md", "Part B.1 - Quality Attributes, Ranked"),
    ("dossier/part-b2-c4-diagrams.md", "Part B.2 - C4 Diagrams"),
    ("dossier/part-b3-architecture-pattern.md", "Part B.3 - The Architecture Pattern"),
    ("dossier/part-b4-adrs.md", "Part B.4 - Architecture Decision Records"),
    ("dossier/part-b5-tradeoffs.md", "Part B.5 - The Trade-off Register"),
    ("dossier/part-b6-not-building.md", "Part B.6 - What You Are Not Building"),
    ("dossier/part-c1-protocols.md", "Part C.1 - Protocol Choice Per Consumer"),
    ("dossier/part-c2-transport-security.md", "Part C.2 - Transport Security"),
    ("dossier/part-c3-api-contract.md", "Part C.3 - The API Contract"),
    ("dossier/part-c4-pin-fix.md", "Part C.4 - The PIN Purchase, Fixed"),
    ("dossier/part-d1-data-model.md", "Part D.1 - The Data Model"),
    ("dossier/part-d2-db-architecture.md", "Part D.2 - The Database Architecture"),
    ("dossier/part-d3-queries.md", "Part D.3 - Five Queries, Predicted"),
    ("dossier/part-d4-index-costs.md", "Part D.4 - What Every Index Costs"),
    ("dossier/part-d5-falsification.md", "Part D.5 - What Would Prove You Wrong"),
    ("ai-log/ai-usage-log.md", "Part E - How You Worked With AI"),
    ("assumptions.md", "Appendix - Stated Assumptions"),
]

CSS = """
@page {
    size: A4;
    margin: 2.2cm 2cm 2.4cm 2cm;
    @frame footer {
        -pdf-frame-content: footerContent;
        bottom: 0.8cm;
        margin-left: 2cm;
        margin-right: 2cm;
        height: 1cm;
    }
}
body { font-family: Helvetica, Arial, sans-serif; font-size: 10.2pt; line-height: 1.42; color: #222222; }
h1 { -pdf-outline: true; -pdf-outline-level: 0; page-break-before: always; font-size: 19pt; color: #111111;
     border-bottom: 2px solid #b30000; padding-bottom: 6px; margin-top: 0; }
h2 { -pdf-outline: true; -pdf-outline-level: 1; font-size: 13pt; margin-top: 16px; color: #b30000; }
h3 { font-size: 11pt; margin-top: 10px; color: #333333; }
p { margin: 6px 0; text-align: justify; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 12px 0; font-size: 8.6pt; }
th, td { border: 0.75pt solid #999999; padding: 2px 5px; text-align: left; vertical-align: top; }
.wbs table { font-size: 7.6pt; }
.wbs th, .wbs td { padding: 1.5px 4px; }
th { background-color: #eeeeee; font-weight: bold; }
code { font-family: Courier, monospace; font-size: 9pt; background-color: #f2f2f2; }
strong { font-weight: bold; }
ul, ol { margin: 4px 0 8px 18px; padding: 0; }
li { margin: 2px 0; }
.titlepage { page-break-after: always; text-align: center; padding-top: 220px; }
.titlepage h1 { border: none; page-break-before: avoid; font-size: 30pt; }
.tocpage { page-break-after: always; }
.tocpage h1 { page-break-before: avoid; }
.toc-entry { margin: 5px 0; font-size: 11pt; }
"""

def md_to_html(path):
    with open(os.path.join(BASE, path), encoding="utf-8") as f:
        text = f.read()
    return markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])

def build():
    body_parts = []

    body_parts.append("""
    <div class="titlepage">
      <h1>Takarda Decision Dossier</h1>
      <p style="font-size:14pt; margin-top:30px;">Architecture and decision record for the Takarda results-checking platform,
      prepared for the National Secondary Certificate Council contract.</p>
      <p style="font-size:11pt; margin-top:60px; color:#555555;">TeSA Africa &mdash; Assignment: Takarda (Decide)</p>
    </div>
    """)

    toc_items = "".join(
        f'<div class="toc-entry">{title}</div>' for _, title in ORDER
    )
    body_parts.append(f"""
    <div class="tocpage">
      <h1>Contents</h1>
      {toc_items}
    </div>
    """)

    for relpath, title in ORDER:
        html_fragment = md_to_html(relpath)
        if "part-a4-wbs" in relpath:
            html_fragment = f'<div class="wbs">{html_fragment}</div>'
        body_parts.append(html_fragment)

    footer = '<div id="footerContent" style="text-align:center; font-size:8pt; color:#777777;">Takarda Decision Dossier &mdash; Page <pdf:pagenumber /> of <pdf:pagecount /></div>'

    full_html = f"""<html><head><meta charset="utf-8"/><style>{CSS}</style></head>
    <body>{footer}{''.join(body_parts)}</body></html>"""

    out_path = os.path.join(BASE, "Takarda-Decision-Dossier.pdf")
    with open(out_path, "wb") as out_file:
        result = pisa.CreatePDF(src=full_html, dest=out_file)

    if result.err:
        print("ERRORS:", result.err)
    else:
        print("PDF built:", out_path)

if __name__ == "__main__":
    build()
