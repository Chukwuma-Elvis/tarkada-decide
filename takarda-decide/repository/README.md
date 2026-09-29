# Takarda Decision Dossier — repository()

This folder is the machine-readable half of the Takarda (Decide) assignment submission, per the brief's requirement for "a repository containing the API contract as a specification file that validates, and the diagrams as files rather than as images pasted into the PDF." The narrative dossier and one-page summary are the two documents one level up, in `submission/`.

## Project layout

This is one git repository with two top-level folders:

```
submission/                    What actually gets handed in
  Takarda-Decision-Dossier.pdf   Parts A-E, contents page, numbered sections
  Takarda-Decision-Dossier.docx  Same content, Word format
  One-Page-Summary.pdf           The five most consequential decisions
  One-Page-Summary.docx          Same content, Word format
  repository/                    <- you are here
    api/openapi.yaml               The API contract, OpenAPI 3.1, validated
    diagrams/*.drawio               C4 diagrams as editable files

working-files/                 Drafting source, not itself submitted
  dossier/*.md                    Markdown source, one file per dossier section
  ai-log/ai-usage-log.md          Part E source
  assumptions.md                  Appendix source
  build_dossier.py                Builds the dossier PDF from dossier/*.md
  build_summary.py                Builds the one-page summary PDF
  build_docx.py                   Builds both .docx copies
  scripts/render_drawio_check.py  Renders each .drawio's own geometry and
                                   flags overlapping boxes or dangling edges
```

## Validating the API contract

```bash
pip install openapi-spec-validator
python -m openapi_spec_validator api/openapi.yaml
```

Expected output: `api/openapi.yaml: OK`.

## Viewing the diagrams

Open any `diagrams/*.drawio` file at [diagrams.net](https://app.diagrams.net) (File → Open From → Device), or in the draw.io desktop app / VS Code draw.io extension.

## Rebuilding the documents

From `working-files/`:

```bash
pip install markdown xhtml2pdf python-docx
python build_dossier.py   # -> ../submission/Takarda-Decision-Dossier.pdf
python build_summary.py   # -> ../submission/One-Page-Summary.pdf
python build_docx.py      # -> ../submission/*.docx
```

## What this repository deliberately does not contain

No application code, no database, no seed data, no query text, and no measured timings — per the assignment's rules, this submission is answered on paper (and in the two files above that must validate/render as files: the API spec and the diagrams).
