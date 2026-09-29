# AGENTS.md

## Purpose

This repository converts Excel workbooks—especially Japanese programming/system specifications—into AI-readable, human-style Markdown specifications.

The Excel workbook is the source of truth, but its cell grid is not the target document structure.

## Primary principle

A good result should look like a specification an engineer intentionally wrote in Markdown. It should let an AI answer questions such as:

- What does this function do?
- What are the inputs, outputs, constraints, and validations?
- What happens on success and failure?
- Which messages and error conditions exist?
- What security rules apply?
- What is the processing flow?
- Which UI fields, APIs, tables, and dependencies are involved?

Do not optimize for reproducing Excel coordinates, merged cells, column widths, colors, or page layout.

## Japanese Excel patterns

Common source workbooks contain:

- a cover sheet such as 表紙 or カバー;
- repeated headers with 機能名, 作成者, 作成日, 版数, etc.;
- many narrow layout columns, often width 2;
- merged cells used for visual placement;
- screen/form layouts;
- function lists and field definitions;
- processing-flow sheets;
- detailed specifications, validations, messages, interfaces, and security notes.

Treat narrow columns and merged cells as layout hints for interpretation, not content that should normally appear in Markdown.

## Target Markdown rules

1. Produce one coherent Markdown specification from the workbook.
2. Preserve source meaning and important values, but reorganize them semantically.
3. Use one H1 document title.
4. Convert the cover into document information and revision history.
5. Convert repeated sheet headers into compact metadata.
6. Prefer semantic sections such as Overview, Inputs/Outputs, UI Fields, Validation, Processing Flow, Business Rules, Interfaces, Error Handling, Messages, Security, and Data Changes.
7. Use Markdown tables for compact domain data; split very wide tables by concept.
8. Use Mermaid for flows when sequence and branches can be inferred reliably.
9. HTML forms are allowed when useful. Do not recreate the Excel grid as a giant HTML table.
10. State conditions and actions explicitly; do not rely on visual position to imply logic.
11. Preserve IDs, codes, limits, dates, status values, and message text.
12. Do not invent, translate, or silently reinterpret requirements.
13. If a source fact cannot be placed naturally, preserve it under Additional source facts as a normal bullet.
14. Keep traceability at sheet/section level. Cell coordinates are normally unnecessary.

## Anti-patterns

The final Markdown should normally not contain:

- Source grid sections;
- rows keyed by A1, B17, and similar coordinates;
- merged-range inventories such as merge=A1:D1;
- col_width or data-grid-width metadata;
- Excel layout-attribute lists;
- giant HTML tables that imitate the worksheet;
- duplicated raw source data added only to increase literal coverage.

## Quality evaluation

Run:

    python -m src.quality_loop input/spec.xlsx

The evaluator scores:

- source-sheet traceability;
- meaningful content coverage;
- document/function metadata;
- specification structure;
- explicit requirements and rules;
- AI readability.

Excel-shaped artifacts reduce the AI-readability score.

Default pass gates:

- total score: 88/100;
- sheet traceability: 100%;
- meaningful content coverage: 80%;
- metadata: 80%;
- specification structure: 75%;
- requirement explicitness: 80%;
- AI readability: 80%.

The quality loop may run up to five semantic passes and stops as soon as a pass succeeds. Report every executed pass.

## Reference files

- docs/AI_MARKDOWN_SPEC_RULES.md — detailed normative rules.
- examples/login_spec.sample.md — reference output.

## Completion

A task is complete when the final Markdown reads like a standalone engineering specification, remains traceable to the workbook, passes the AI-readability evaluator (or reaches pass 5 and is marked review-required), and the evaluation history is written to reports/.
