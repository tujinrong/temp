# Executed specification evolution loop

The same 25 workbook-specific acceptance checks were applied to every candidate. The old heuristic score is shown for comparison, not as a measure of AI understanding.

| Loop | Strategy | Legacy score | Acceptance checks | Outcome |
|---|---|---:|---:|---|
| 1 | Repository baseline (unmodified renderer) | 98.92 | 15/25 | RETRY |
| 2 | Repair prose, domain organization and repeated metadata | 98.74 | 19/25 | RETRY |
| 3 | Resolve supported counts; distinguish unspecified defaults | 98.74 | 21/25 | RETRY |
| 4 | Preserve flow conditions and expose inference/source gaps | 98.74 | 25/25 | ACCEPTANCE_CHECKS_PASS |

## Loop 1

Candidate SHA-256: `fa555f4f6c7306172bcba8b3c153669303b9bcc2436b6c5957a0e25704b0bbc0`

- S02: Requirements are prose, not headings. Merged prose must remain a paragraph or list item.
- S03: Repeated metadata consolidated. Retain overrides but do not repeat identical per-sheet headers.
- S04: Domain sections rather than worksheet transcription. Put source sheet names in traceability, not the main outline.
- F04: Function count is usable and labelled. COUNTA over four literal function IDs; report derived count, not a generic placeholder.
- F08: Blank defaults explicitly distinguished from empty strings. A blank initial-value cell is not a specified empty-string default.
- F10: Diagram retains validation-success precondition. Detailed specification conditions must also hold in Mermaid; unconditional API edges fail.
- F16: Layout-derived graph marked as tentative. Unverified visual connections cannot silently become normative behavior.
- F17: Unspecified interface behavior and validation failures surfaced. Source review found no interface contract or complete failed-validation path.
- F18: Unresolved identifier correspondence surfaced. Cover ID and function-list IDs have no explicit correspondence.
- F19: All source sheets mapped. Sheet names are allowed in a compact traceability table.

## Loop 2

Candidate SHA-256: `f98fc5810e66ba9f860101e7008812ad72df88ebb8010b69fc13832340fc19a0`

- F04: Function count is usable and labelled. COUNTA over four literal function IDs; report derived count, not a generic placeholder.
- F08: Blank defaults explicitly distinguished from empty strings. A blank initial-value cell is not a specified empty-string default.
- F10: Diagram retains validation-success precondition. Detailed specification conditions must also hold in Mermaid; unconditional API edges fail.
- F16: Layout-derived graph marked as tentative. Unverified visual connections cannot silently become normative behavior.
- F17: Unspecified interface behavior and validation failures surfaced. Source review found no interface contract or complete failed-validation path.
- F18: Unresolved identifier correspondence surfaced. Cover ID and function-list IDs have no explicit correspondence.

## Loop 3

Candidate SHA-256: `8d0f4c6a6eead2bfdedab6e64072a2260819682a178303c04c30e20fdf2cec49`

- F10: Diagram retains validation-success precondition. Detailed specification conditions must also hold in Mermaid; unconditional API edges fail.
- F16: Layout-derived graph marked as tentative. Unverified visual connections cannot silently become normative behavior.
- F17: Unspecified interface behavior and validation failures surfaced. Source review found no interface contract or complete failed-validation path.
- F18: Unresolved identifier correspondence surfaced. Cover ID and function-list IDs have no explicit correspondence.

## Loop 4

Candidate SHA-256: `48f21e2daf88e26bc594004af9017223654965cbb9dfb503f31b01f6fbeca794`

All checks passed.

## Final result

Selected loop: 4. Status: **ACCEPTANCE_CHECKS_PASS**.

The source workbook was not modified. Unspecified interface behavior and uncertain diagram connections remain explicit review questions, not invented requirements.

**Scope:** This run uses the synthetic Japanese login specification. A new workbook requires its own reviewed source contract. Passing these checks is not proof of visual fidelity, Mermaid browser rendering, LLM task accuracy, or general conversion accuracy.

Source SHA-256: `adee23e3448da6dc4013d7d7fbbe939d5aa79b34521876a01e3e2ce3d7952bd7`

Contract SHA-256: `35fd918c0f0537c921f0b2af6b56b6d4195575d8da428c2388ea96ed2eff3cb7`

## Regression tests executed

`python -m unittest discover -s tests -p test_semantic_review.py -v`

All 6 test methods passed. The corruption test contains 13 changed-output subcases; all were rejected. They include wrong field limits, optional-required flips, missing password masking, wrong clear action, reversed branches, unconditional API calls, removed security negation, a wrong lock threshold, changed or deleted messages, comment-only coverage, conflicting duplicate fields, and appended source grids.

## Source review conclusion

The fourth candidate is suitable as the reference format for this synthetic workbook: domain sections, prose, compact tables, tentative Mermaid and explicit unanswered questions. This is not approval of the incomplete source requirements or a claim that arbitrary Japanese Excel specifications are now supported correctly.
