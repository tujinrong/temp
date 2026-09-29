# XLSX specification → AI-readable Markdown

General-purpose converter for Excel-based programming/system specifications, with special handling for common Japanese specification styles.

## Goal

The target is not an Excel transcription. The target is a Markdown specification that a human engineer could have written directly and that an AI can analyze reliably.

The converter interprets workbook layout, then rewrites the information into semantic sections, compact tables, lists, Mermaid flows, and optional HTML form mockups.

## Source styles handled

- cover sheets such as 表紙 and カバー
- per-sheet headers such as 機能名, 作成者, 作成日, 版数
- width-2 layout grids and merged cells
- function/item lists
- screen and form specifications
- processing flows
- detailed/article-style specifications
- messages, validations, security notes, and formulas/data values

## Install

    python -m pip install -r requirements.txt

## Convert once

    python -m src.xlsx_to_markdown input/spec.xlsx -o output/spec.md --fidelity 1

The fidelity option remains 1–5 for compatibility, but the levels now represent semantic recovery strategies, not increasingly literal Excel dumps.

## Convert + evaluate + retry

    python -m src.quality_loop input/spec.xlsx

The process stops as soon as the Markdown passes. If it does not pass, it can retry up to five strategies:

1. semantic-baseline
2. analysis-index
3. requirements-explicit
4. traceability-enhanced
5. semantic-recovery

Outputs include the final Markdown, each executed pass, machine-readable JSON evaluations, and a human-readable report.

## Evaluation philosophy

The evaluator rewards semantic specification structure, explicit rules, meaningful source coverage, metadata, Mermaid flows, compact domain tables, readable forms, and sheet-level traceability.

It penalizes Source grid dumps, cell-coordinate tables, merged-cell/column-width metadata, HTML that recreates an Excel grid, and very wide hard-to-chunk tables.

A file can therefore have 100% literal Excel-cell coverage and still fail if it is poor for AI understanding.

## Style guide and sample

- docs/AI_MARKDOWN_SPEC_RULES.md — normative conversion/evaluation rules.
- examples/login_spec.sample.md — reference output for a Japanese login specification.

## Regression fixture

    python tests/make_japanese_spec_test.py
    python -m src.quality_loop input/japanese_program_spec_test.xlsx

The fixture includes a cover, repeated sheet metadata, width-2 layout grids, screen definition, flow, detailed rules, messages, and a formula.
