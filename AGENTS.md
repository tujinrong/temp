# AGENTS.md

## Purpose

This repository converts Excel workbooks, especially Japanese programming/system specification workbooks, into readable Markdown and evaluates the conversion for fidelity.

## Directory structure

- `input/` — source `.xlsx` workbooks.
- `output/` — final generated Markdown.
- `reports/` — per-loop candidates and evaluation reports.
- `src/` — converter, workbook reader, evaluator, and quality-loop programs.

## Expected source style

Japanese program specifications often contain:

- a cover sheet such as `表紙` or `カバー`;
- a repeated header on each sheet with `機能名`, `作成者`, `作成日`, `版数`, etc.;
- many very narrow layout-grid columns, often width `2`;
- merged cells spanning those narrow columns;
- function/item lists;
- screen/form design sheets;
- processing-flow sheets;
- detailed article-like specification sections and message/validation tables.

The converter must treat narrow columns as a visual layout grid rather than blindly creating dozens of empty Markdown columns.

## Conversion rules

1. Read source workbooks from `input/`.
2. Never modify or delete the original workbook unless explicitly instructed.
3. Preserve every non-empty worksheet and meaningful source value.
4. Preserve formulas and important layout metadata at higher fidelity levels.
5. Convert cover sheets to Markdown title/metadata sections.
6. Extract repeated sheet headers separately so function name, author, date, version, and document type remain visible.
7. Convert lists/definition tables to Markdown tables or lists.
8. Convert processing flows to Mermaid when a reliable sequence can be inferred. State when branch direction is inferred.
9. Convert screen/form layouts to HTML tables when merged cells/colspan are needed. Markdown tables may be used for simple field definitions.
10. Convert detailed prose specifications to Markdown headings, paragraphs, lists, and tables rather than one giant grid.
11. Escape Markdown pipe characters when necessary and preserve Unicode/Japanese text.
12. Do not invent, summarize, translate, or reinterpret requirements unless explicitly requested.

## Quality loop

Use `python -m src.quality_loop <xlsx>` for normal work.

The quality loop may run up to **5 passes**. Each pass increases fidelity if the evaluator rejects the previous result.

For every executed loop, report:

- loop number and fidelity mode;
- total score and PASS/RETRY status;
- worksheet coverage;
- source-cell coverage;
- formula coverage;
- structure score;
- layout score;
- detected problems;
- changes recommended for the next loop.

Stop early if a pass meets the configured threshold. If all five fail, keep the fifth-pass output as best effort and clearly mark it for review.

## Completion

A task is complete when:

- the final Markdown exists in `output/`;
- the evaluation history exists in `reports/`;
- all non-empty worksheets are represented;
- the evaluator has passed, or the fifth pass has been reported as review-required;
- the final response summarizes every executed loop and the final result.
