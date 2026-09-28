import markdown
from xhtml2pdf import pisa
import os

BASE = os.path.dirname(os.path.abspath(__file__))

CSS = """
@page { size: A4; margin: 2.2cm 2cm; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10.5pt; line-height: 1.4; color: #222222; }
h1 { font-size: 16pt; color: #111111; border-bottom: 2px solid #b30000; padding-bottom: 6px; margin-top: 0; }
p { margin: 6px 0; text-align: justify; }
strong { font-weight: bold; }
"""

def build():
    with open(os.path.join(BASE, "dossier", "00-one-page-summary.md"), encoding="utf-8") as f:
        text = f.read()
    html_fragment = markdown.markdown(text, extensions=["tables", "sane_lists"])
    full_html = f"<html><head><meta charset='utf-8'/><style>{CSS}</style></head><body>{html_fragment}</body></html>"
    out_path = os.path.join(BASE, "One-Page-Summary.pdf")
    with open(out_path, "wb") as out_file:
        result = pisa.CreatePDF(src=full_html, dest=out_file)
    print("ERR" if result.err else "OK", out_path)

if __name__ == "__main__":
    build()
