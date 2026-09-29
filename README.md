# XLSX specification → AI-readable Markdown

The target is a human-style engineering specification, not an Excel grid copied into Markdown.

## Validated workflow

The 2026-09-29 execution found that the existing heuristic evaluator awarded 98.92/100 to an output that failed 10 of 25 source-reviewed acceptance checks. Do not treat the old score as proof of AI understanding.

The new optional workflow uses a reviewed source contract, checks field/error associations and processing conditions, and applies deterministic repair strategies. It is not an autonomous code-writing or LLM-evaluation agent.

```bash
python -m pip install -r requirements.txt
python tests/make_japanese_spec_test.py
python -m src.evolution_loop input/japanese_program_spec_test.xlsx \
  --contract tests/fixtures/japanese_program_spec.contract.json
python -m unittest discover -s tests -p test_semantic_review.py -v
```

The recorded Japanese fixture run required four rounds: 15/25, 19/25, 21/25, then 25/25 checks. Thirteen deliberately corrupted outputs were rejected. See `reports/evolution/evaluation.md` and `output/japanese_program_spec_test.md`.

## Other workbooks

```bash
python -m src.semantic_repair input/spec.xlsx -o output/spec.md
```

This creates a candidate, not a certification. Prepare an independently reviewed source contract for each new workbook before using `evolution_loop`. Unknown source fingerprints are rejected. Do not derive the expected answers from the candidate being evaluated.

The repair converter consolidates metadata, keeps paragraphs as prose, retains field columns and blank cells, preserves recognized conditions in tentative Mermaid diagrams, and exposes review questions. Only a direct local COUNTA over literal cells is independently evaluated; other missing formula results remain unresolved. Images, charts and arbitrary drawing connectors require source review.

`src.quality_loop` and `src.evaluate_markdown` remain as legacy diagnostics for comparison. Their scores are not the new acceptance gate.

## Output and audit files

- `output/`: final selected Markdown.
- `reports/evolution/`: per-loop candidates, JSON checks and summary after execution.
- `tests/fixtures/`: reviewed source contracts with semantic source fingerprints.
- `docs/EVOLUTION_RUN.md`: rubric scope and reproduction notes.

A passing fixture test is not a measured score for LLM task accuracy or proof of general-purpose conversion quality. Review unspecified source behavior before implementation.
