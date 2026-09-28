# AGENTS.md

## Purpose

This repository is a workspace for converting Excel workbooks into clean, readable Markdown files.

## Directory structure

- `input/` — source Excel files (`.xlsx`, `.xlsm`, or `.xls` when supported).
- `output/` — generated Markdown files.
- `AGENTS.md` — instructions for agents working in this repository.

## Workflow

When asked to convert an Excel file to Markdown:

1. Look for the source workbook in `input/`.
2. Inspect the workbook before converting it:
   - identify all worksheets;
   - determine the used range on each worksheet;
   - preserve meaningful headings, labels, and table structure;
   - note formulas, merged cells, dates, percentages, and numeric formatting when they affect meaning.
3. Create Markdown output in `output/`.
4. Use the workbook filename as the base output name. For example:
   - `input/report.xlsx` → `output/report.md`
5. If a workbook contains multiple worksheets, put them in one Markdown file by default:
   - start with a level-1 heading using the workbook name;
   - use a level-2 heading for each worksheet;
   - convert tabular data to Markdown tables where practical.
6. Preserve the data faithfully. Do not invent, summarize, translate, or reinterpret cell values unless explicitly requested.
7. For blank cells, use an empty Markdown table cell.
8. If a worksheet is too complex for a normal Markdown table, preserve the information in the clearest Markdown structure possible and briefly note any conversion limitation.
9. Do not modify or delete the original Excel file unless explicitly instructed.
10. After conversion, verify that all non-empty worksheets and meaningful data from the source are represented in the Markdown output.

## Output quality

- Use UTF-8 text.
- Keep Markdown valid and easy to read.
- Escape pipe characters inside table cells when needed.
- Avoid unnecessary HTML.
- Preserve Unicode text.
- Keep numeric identifiers as text when leading zeros are meaningful.
- Prefer displayed/formatted values when formatting carries business meaning.

## File handling

Treat files in `input/` as source material and files in `output/` as generated artifacts. Do not overwrite unrelated files.

## Completion

A conversion task is complete when the Markdown file exists in `output/`, the workbook's relevant sheets and data have been checked against the source, and any unavoidable conversion limitations have been reported.
