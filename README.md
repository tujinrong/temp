# XLSX specification → Markdown

General-purpose converter aimed at Japanese Excel-based program/system specifications.

## What it handles

- cover sheets (`表紙`, `カバー`, etc.)
- repeated per-sheet headers such as `機能名`, `作成者`, `作成日`, version information
- very narrow grid columns (for example width `2`) without exploding them into unreadable Markdown columns
- merged cells
- normal lists and definition tables
- processing-flow sheets rendered as Mermaid when possible
- screen/form specifications rendered with HTML tables when merged-grid layout matters
- formulas, charts/images counts, and source-cell audit information at higher fidelity levels

## Install

```bash
python -m pip install -r requirements.txt
```

## Convert once

```bash
python -m src.xlsx_to_markdown input/spec.xlsx -o output/spec.md --fidelity 1
```

`--fidelity` is from 1 to 5. Higher levels append progressively more source/audit information.

## Convert + evaluate + retry

```bash
python -m src.quality_loop input/spec.xlsx
```

The loop evaluates every result and retries with a higher-fidelity conversion when needed, up to five passes.

Outputs:

- `output/spec.md` — final conversion
- `reports/spec.pass1.md` ... `pass5.md` — candidate Markdown from each executed loop
- `reports/spec.pass1.json` ... — machine-readable evaluation for each loop
- `reports/spec.evaluation.md` — human-readable report for every loop and final result
- `reports/spec.evaluation.json` — full machine-readable history

The evaluator measures worksheet coverage, source-cell coverage, formula coverage, semantic structure, and layout preservation.

## Included Japanese-style test

`tests/make_japanese_spec_test.py` creates the primary regression workbook at `input/japanese_program_spec_test.xlsx`. It includes a cover, repeated per-sheet headers, width-2 grid columns, merged screen layout, function list, process flow, article-style detailed specification, messages, and a formula.

Example:

```bash
python tests/make_japanese_spec_test.py
python -m src.quality_loop input/japanese_program_spec_test.xlsx
```

A successful regression currently requires four passes: semantic conversion first, then progressively higher fidelity until formulas and layout metadata are fully preserved.
