# Form hard-copy and callout evolution run

The same 39 checks (25 existing + 14 drawing/HTML checks) were applied to every revision.

| Loop | Change | Checks | Outcome |
|---|---|---:|---|
| 1 | Previous accepted semantic converter, on expanded workbook | 26/39 | RETRY |
| 2 | Extract drawing text and reconstruct HTML; literal HTML comments | 37/39 | RETRY |
| 3 | Retain comments visibly and link notes to controls for AI analysis | 39/39 | ACCEPTANCE_CHECKS_PASS |

## Loop 1

Candidate SHA-256: `cee6cf62d42c8b2eba16815dee0791d99384f95f9ed410120553422585590fdf`

- H01: Original hard-copy image preserved and linked. Require the actual embedded PNG bytes; filename occurrence is not coverage.
- H02: Semantic HTML form, not an image-only or Excel-grid export. One real form; no raw spreadsheet HTML table.
- H03: Control type, ID, required flag and limit remain associated. Check exact source field tuples, including password masking and both length limits.
- H04: Login and clear represented without invented runtime behavior. Static type=button controls; actual event requirements remain in source-backed text.
- H05: Mockup explicitly distinguished from functioning application. Do not claim a working login page or infer API URLs from a screenshot.
- H06: All five source callouts exported as associated HTML comments. Compare original DrawingML text and target together; do not read notes from cells.
- H07: Callout meaning remains visible to Markdown/HTML analysis. HTML comments alone are insufficient. Keep a visible specification-comment copy.
- H08: Each field or region references its own comment. Use explicit target IDs; never attach a nearby bubble by guesswork.
- H09: Message, user ID, password, then buttons follow reviewed layout. Use semantic order and grouped actions rather than width-2 spreadsheet coordinates.
- H10: Visible labels bind to the correct controls. A label for userId must not point to password, and vice versa.
- H12: Unspecified defaults are not fabricated. An empty screenshot input is not evidence of a specified empty-string default.
- H13: Standalone HTML and Markdown contain the same form. Publish a directly viewable HTML file and the same semantic HTML in the Markdown.
- H14: Buttons grouped; IDs unique; no silently unsupported drawings. Group both actions on one row and surface unsupported drawing content.

## Loop 2

Candidate SHA-256: `1a0b5042c7f1a70b5281f33a26a5551589474c80a619d07c01cb91885b4a37b6`

- H07: Callout meaning remains visible to Markdown/HTML analysis. HTML comments alone are insufficient. Keep a visible specification-comment copy.
- H08: Each field or region references its own comment. Use explicit target IDs; never attach a nearby bubble by guesswork.

## Loop 3

Candidate SHA-256: `6eea623f25e8b4934aa5636011c133bfbdaeb9f2a85f9b6939805f7b25bc7979`

All acceptance checks passed.

## Final result

Selected loop: 3. Status: **ACCEPTANCE_CHECKS_PASS**.

The expanded workbook contains one embedded hard-copy PNG and five editable DrawingML callouts. Callouts export as HTML comments plus visible, target-linked specification notes. The HTML is a static form layout, not a login implementation.

Source unchanged during the conversion run: true.

Synthetic source-reviewed screenshot. Deterministic acceptance checks, not an AI-understanding score. Other screenshots need their own visual mapping; no automatic OCR/vision service is included.

Source SHA-256: `d4154974ef09a102eed06758d5be77453140f37f6dab3cf78e8bfd249e02981f`

## Additional verification executed

- Original five sheets: source cell values/formulas matched after adding the sixth sheet.
- New regression suite: all 9 test methods passed; 19 Markdown corruption subcases plus one standalone-HTML drift case were rejected.
- Existing regression suite: all 6 test methods passed, including its 13 corruption subcases.
- Browser checks: 8/8 passed in system Chromium (desktop layout, field attributes, note visibility, ordering, no network requests or JavaScript errors, and no narrow-view horizontal overflow).
- Embedded PNG: exact source bytes recovered and hash-verified.
- Floating callouts: five DrawingML rounded callout shapes with their own text, not duplicate cell notes.

The HTML was visually inspected in Chromium. The workbook's native image placement has been validated at the OOXML relationship/anchor/media level; Microsoft Excel itself was not available for an application-level smoke test. The spreadsheet preview renderer displayed the callout shapes but omitted the picture after import, so picture contents were also inspected separately.
