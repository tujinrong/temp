# AGENTS.md

## Purpose

Convert Excel programming/system specifications into human-style, AI-readable Markdown. Interpret the document a person can see; do not reproduce the Excel cell grid. The source workbook is read-only unless the user explicitly requests editing it.

## Repository and output paths

Operate directly on `main` in `tujinrong/temp`. Do not create or use work branches.

For an input `input/<relative-directory>/<name>.xlsx`, create these UTF-8 (without BOM) Markdown files:

- `output/<relative-directory>/<name>.md`: specification content only.
- `qa/<relative-directory>/<name>.md`: questions, inconsistencies, unresolved matters and requests for missing referenced material.
- `report/<relative-directory>/<name>.md`: conversion results, scope and reading guide, source mapping, exclusions, verification and limitations.

Preserve the exact relative directories and filename stem in all three destinations. Use singular `report`, not `reports`, for new production conversions. An input directly under `input` produces files directly under the three output roots.

## Visible-only scope (mandatory)

1. Exclude sheets whose saved state is `hidden` or `veryHidden`.
2. Exclude rows and columns hidden in the saved workbook, including grouped column ranges, collapsed groups and filter-hidden rows. Inspect the actual hidden state; `outlineLevel` alone does not mean hidden.
3. Exclude zero-height rows and zero-width columns. Do not treat scrolling, frozen panes, the current viewport or print area alone as hidden content.
4. Apply exclusions before extracting requirements, tables, questions, comments, formulas, source maps or evaluation expectations. Hidden content must not reappear through appendices, fallback extraction, QA generation or coverage-repair loops.
5. Do not unhide the workbook. Do not use hidden cells to fill missing visible requirements.
6. A visible formula's saved displayed result may be retained, even if its formula references hidden data. Do not expand hidden dependencies or recalculate external workbooks. Unavailable displayed results are reported as limitations, not fabricated.
7. For merged regions, keep only text actually visible in the saved view. An anchor in a hidden row/column is not automatically permission to copy its text to a visible cell. Ambiguous partial visibility requires visual review.
8. Exclude hidden drawing objects and objects fully suppressed by hidden sheet/row/column layout. For floating or partially overlapping objects, inspect their visible area and anchoring behavior rather than relying only on the top-left anchor. Do not silently discard a visibly floating object.
9. Report exclusion counts/reasons when useful, but do not transcribe hidden contents or generate questions about deliberately excluded data.

## Other exclusions

Do not convert legend sections (凡例) or revision/change histories (変更履歴・改訂履歴). Cover metadata such as current version, author and date remains in scope. Excluded content is not a coverage failure.

## Human-view interpretation

- Inspect visible sheet layout, merged headings, reading order, tables, screenshots, connectors and callout targets.
- Many Japanese specifications use width-2 columns as a visual grid. Convert their relationships to headings, prose and compact domain tables, not dozens of empty columns or coordinate-keyed rows.
- Reorganize visible source sections into a coherent engineering specification. Consolidate repeated metadata without losing visible overrides.
- Preserve identifiers, values, conditions, negation, units, required/optional distinctions, messages and record/field associations.
- Empty cells do not automatically mean a specified empty-string default or an optional field.
- Distinguish current requirements, illustrative examples, source comments and uncertain interpretations. Never promote a question into a confirmed requirement.
- Do not infer logic from color or left/right placement alone. Keep unresolved matters in QA; the output may contain a short QA-ID cross-reference rather than the whole question.

## Forms, flows and callouts

Use semantic HTML inside the `.md` for form/screen layout when present. Labels, controls, groups and associated notes should reflect visible source content; do not reconstruct the worksheet grid. HTML is a static specification mockup, not an implemented application, and must not invent live endpoints or behavior.

Use Mermaid for verified processing relationships. Preserve branch conditions and distinguish inferred connections. Unsupported images/shapes must be reported, not silently omitted or marked fully converted.

Convert visible callouts (吹き出し) to target-associated comments and readable notes. Specification notes stay in `output`; questions and unresolved callouts go to `qa`. Preserve original wording where needed and keep a visible copy so HTML-comment stripping does not remove requirements.

## Questions

Prefer selection-based questions with stable QA IDs, source section, brief context, a single clear question and an unselected answer field. Include `その他` and `未定・要調査` where appropriate. State whether one or multiple choices are allowed. Split compound questions. Do not invent source facts or preselect answers.

## Evaluation and repair

Evaluate only the in-scope visible content. Test semantic associations and critical constraints, not only substring presence. A high heuristic score is not proof of AI understanding.

When quality is insufficient, repair actual omissions or misinterpretations and re-evaluate, up to five executed passes. Record each candidate's findings, changes and outcome in `report`; do not invent iterations or scores. Stop when the relevant checks pass. An unverified figure or unmet requirement remains review-required regardless of total score. Never recover excluded content to improve a score.

## Completion

Save the actual specification, QA and result report to the required paths on `main`, then read them back to verify existence and content. Report the commit and exact paths. A local attachment, a status-only report or an empty directory is not completion of GitHub output delivery. Distinguish completed conversion from partial conversion, failed retrieval and unexecuted evaluation.

Existing guides/examples are references only; this file and the user's latest explicit scope rules take precedence over older examples and legacy evaluators.
