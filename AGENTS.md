# AGENTS.md

## Purpose and delivery

Convert Excel programming/system specifications into human-style, AI-readable Markdown, interpreting the document a person can see rather than reproducing the Excel grid. Do not modify the source workbook without an explicit request.

Operate directly on `main` in `tujinrong/temp`. Do not create or use work branches. For `input/<relative-directory>/<name>.xlsx`, write UTF-8 without BOM, LF Markdown to:

- `output/<relative-directory>/<name>.md`: specification only.
- `qa/<relative-directory>/<name>.md`: questions, inconsistencies and unresolved matters.
- `report/<relative-directory>/<name>.md`: results, scope, reading guide, mappings, exclusions and verification.

Preserve exact relative directories and filename stems. Use singular `report`. An input directly under `input` produces files directly under each output root. Re-read files on main and compare hashes before claiming successful delivery. A local attachment, status-only report or empty directory is not completed GitHub delivery.

## Mandatory visible-only scope

Exclude hidden and veryHidden sheets, hidden rows and columns (including grouped column ranges and filter-hidden rows), zero-height rows and zero-width columns. Inspect saved visibility; outlineLevel alone does not mean hidden. Scrolling, frozen panes, viewport and print area alone do not exclude content.

Apply exclusions before extracting text, requirements, questions, comments, source mappings and evaluation expectations. Do not recover excluded information through fallback extraction, appendices or repair loops. Do not unhide the workbook or use hidden dependencies to fill visible requirements. Excluded content is not a coverage failure.

Keep a visible formula's saved displayed result without expanding hidden references or fetching external workbooks. Report an unavailable result instead of inventing it. For partially hidden merged cells and floating drawings, inspect actual visible content and anchoring; do not assume the top-left anchor determines the whole object's visibility. Exclude hidden drawing objects and hidden parent groups. Record ambiguity for visual review.

Exclude legends (凡例) and revision/change histories (変更履歴・改訂履歴). Current cover version, author, dates and approval information remain in scope. Report exclusion counts/reasons without transcribing hidden content or asking questions about intentionally excluded material.

## Introduction and Excel sheet order

Use one H1 document title. Rename a leading cover chapter to `## 1. はじめに` and do not create an additional 表紙 chapter. Consolidate visible cover information, identical common header metadata and reviewed common content there. Retain exact original source keys and stable anchors; the display title is not a replacement source key.

After exclusions, keep all later chapters in saved Excel tab order, with consecutive numbers and source sheet names. Do not sort by sheetId, internal worksheet filename, alphabet or business topic. Trim trailing layout-only spaces only for display; preserve the original keys in mappings.

Consolidate a shared rule only when meaning, conditions, units and applicability agree. Assign a stable common-rule ID/anchor and link the applicable original chapters to it. Do not widen a single-sheet or field-specific rule into an all-function rule. Keep sheet-specific details, examples, exceptions and conflicting wording in their source chapters. Do not silently choose between conflicting values or promote unanswered choices to requirements.

Forms, figures, tables and source callouts remain with their source sheet. A verbatim callout may repeat a shared rule when necessary to preserve its target and wording. Do not combine DFD, event, screen or other sheets into new topic-based chapters. Use semantic H3/H4 sections, prose, lists and compact domain tables within each chapter, not coordinate-keyed rows or empty width-2 grid columns.

QA groups follow their primary source-sheet order and corresponding output chapter numbers. Use はじめに for the cover/common-header group. Preserve existing QA IDs, choices, answers and status; cross-sheet questions appear once with all sources. Keep a short QA reference in a QA-only output chapter rather than inventing content.

Report the source-to-chapter mapping in Excel order, including original tab position, output chapter and any common information moved to the introduction. Scope, reading instructions and conversion results belong in report, not in はじめに. See `docs/SHEET_ORDER.md`. `src/sheet_order.py` assembles reviewed fragments; it does not automatically infer common facts or interpret images. A workbook without a leading cover requires an explicitly reviewed mapping before restructuring.

## Human-view interpretation

Preserve identifiers, conditions, negation, units, values, required/optional distinctions and field/record associations. Empty cells do not automatically specify an empty-string default or optional status. Distinguish requirements, examples, comments and uncertain interpretations. Do not infer logic from color or left/right placement alone.

## HTML screen layout and comments

Use semantic HTML inside the Markdown. Respect the visible source screen and the existing verified HTML as far as practical: retain control types, order, grouping, column order, example rows and target IDs. Do not redesign the screen or revive obsolete text covered by newer source shapes.

Give the screen a clearly visible outer border. Keep controls and data inside that frame; place explanatory comments, callout text and conversion notes outside the frame but in the same source-sheet chapter. Preserve target associations with IDs, links and aria-describedby where appropriate. Do not overlay commentary over input fields or rows.

HTML is a static specification mockup, not a working application. Do not invent endpoints or behavior. Preserve fields' specified required/optional status; mockup disabling is not a business rule. Retain an external visible copy of any specification note stored in an HTML comment. Questions and unresolved callouts go to QA, not to confirmed specification text.

## Mermaid generation and mandatory independent validation

Use Mermaid only for source-verified relationships. Preserve branch conditions, node meaning, direction and source ownership. Unsupported details require an explicit limitation or a faithful textual/table alternative; never silently remove them to obtain PASS.

Avoid label syntax that can be interpreted as Markdown lists, including `1. ` and `- `. Preserve displayed numbering when possible, for example `A["1#46; 画面初期表示"]`. Confirm the rendered text; escaping must not alter conditions or identifiers. Do not assume quoting alone prevents renderer-specific issues.

Run `src/mermaid_validate.py` independently on the final Markdown bytes. It must extract all Mermaid fences, reject empty/unclosed blocks and missing expected diagrams, check portability risks, call the actual Mermaid parser, render SVG in Chromium and detect error text/graphics such as `Unsupported markdown: list`. Regex/fence checks alone are not grammar validation. A parser success is not a rendering success.

Test both htmlLabels=true and htmlLabels=false and record the actual engine version, runtime fingerprint, browser version, file hash, block/line and per-stage results. Missing runtime or unavailable rendering is BLOCKED, never PASS. Keep input Markdown read-only and do not auto-repair it inside the evaluator. Do not send private diagram content to an external rendering service.

`src/independent_evaluate.py` is the final production gate: independent content acceptance AND Mermaid validation must pass for the same current Markdown hash. A content score cannot compensate for a Mermaid failure. Expected diagram count comes from source review, not merely from counting whatever the converter emitted. Old/synthetic evaluators remain diagnostic and cannot waive this gate. See `docs/MERMAID_VALIDATION.md` for commands and limitations.

## Questions, repair and completion

Prefer selection-based questions with stable IDs, source, brief context, one clear question and unselected answer fields. Include その他 and 未定・要調査 where appropriate, state single/multiple selection and split compound questions. Preserve existing answers.

Evaluate only in-scope visible content and semantic associations. A heuristic score is not proof of AI understanding. Repair actual omissions or misinterpretations and re-evaluate up to five executed conversion passes. Report every executed pass without inventing iterations or reusing past results as current tests. Stop on a genuine pass; an unverified required figure remains review-required regardless of score.

Save specification, QA and report to main, read them back, verify their hashes, then report the commit and exact paths. Distinguish completed conversion, partial conversion, unresolved source QA, unavailable runtime and unexecuted evaluation. Latest user rules and this file supersede older guides and examples.
