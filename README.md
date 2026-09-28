# Takarda Decision Dossier — repository

This repository is the machine-readable half of the Takarda (Decide) assignment submission. The narrative dossier is `Takarda-Decision-Dossier.pdf` (Parts A–E, built from `dossier/*.md`); the one-page summary is `One-Page-Summary.pdf`.

## Structure

```
dossier/          Markdown source for the decision dossier (one file per Part A–D section)
ai-log/           Part E — the AI usage log
diagrams/         C4 diagrams as editable draw.io/diagrams.net files (context, container, one component)
api/openapi.yaml  The API contract — OpenAPI 3.1, validated (see below)
assumptions.md    Every stated assumption used anywhere in the dossier, collected in one place
build_dossier.py  Builds Takarda-Decision-Dossier.pdf from dossier/*.md + ai-log + assumptions
build_summary.py  Builds One-Page-Summary.pdf from dossier/00-one-page-summary.md
```

## Validating the API contract

```bash
pip install openapi-spec-validator
python -m openapi_spec_validator api/openapi.yaml
```

Expected output: `api/openapi.yaml: OK`.

## Viewing the diagrams

Open any `diagrams/*.drawio` file at [diagrams.net](https://app.diagrams.net) (File → Open From → Device), or in the draw.io desktop app / VS Code draw.io extension.

## Rebuilding the PDFs

```bash
pip install markdown xhtml2pdf
python build_dossier.py
python build_summary.py
```

## What this repository deliberately does not contain

No application code, no database, no seed data, no query text, and no measured timings — per the assignment's rules, this submission is answered on paper (and in the two files above that must validate/render as files: the API spec and the diagrams).
