# Executed evolution-loop review

## Acceptance target

The specification should be understandable without mentally rebuilding the spreadsheet. Preserve requirements and associations rather than cell positions. Use semantic sections, prose, domain tables, and tentative Mermaid where connector meaning is not fully established. HTML controls are optional, not a quality requirement.

## What changed

Round 1 executes the unchanged renderer from repository commit `86f9e5741844af57c91f2782ae147976897c554e`. Its numeric score was 98.92, but source review found merged paragraphs rendered as headings, repeated metadata, a missing count, and an unconditional validation-to-API edge.

Rounds 2–4 use `src/semantic_repair.py`. The same 25 acceptance checks apply to every round. They check whole metadata/field/function/error records, security negation, the consecutive-failure threshold, guarded graph edges, and explicit treatment of source gaps. They also reject spreadsheet-shaped appendices and comment-only coverage.

The expected records in `tests/fixtures/japanese_program_spec.contract.json` were transcribed from the source workbook independently of the converter. Source ranges are kept in that sidecar, not in the main specification. The contract fingerprint checks sheet names and cell values/formulas, ignoring ZIP timestamps and formula caches. It does not verify all visual styling or drawing relationships.

## Run

From the repository root:

```bash
python tests/make_japanese_spec_test.py
python -m src.evolution_loop input/japanese_program_spec_test.xlsx \
  --contract tests/fixtures/japanese_program_spec.contract.json \
  --output output/japanese_program_spec_test.md \
  --report-dir reports/evolution
python -m unittest discover -s tests -p test_semantic_review.py -v
```

A new workbook needs a new reviewed contract. The loop does not silently adapt expected answers to its output. The legacy score remains visible for diagnosis but cannot override a failed acceptance check. The best checked candidate is selected; an unresolved run is marked REVIEW_REQUIRED. At most five rounds are allowed; unchanged output is flagged as no progress.

## Recorded result

| Round | Acceptance checks | Outcome |
|---|---:|---|
| 1 | 15/25 | RETRY |
| 2 | 19/25 | RETRY |
| 3 | 21/25 | RETRY |
| 4 | 25/25 | ACCEPTANCE_CHECKS_PASS |

Six unittest methods passed, including 13 deliberate-corruption subcases. The final source workbook hash was unchanged. No fifth round was necessary.

## What this does not establish

These are deterministic fixture acceptance tests plus assistant source review, not a blinded human study or downstream LLM benchmark. The checker recognizes the emitted Markdown/Mermaid subset; arbitrary equivalent paraphrases can require updated reviewed checks. A checksum match is not proof of semantic completeness.

The source does not specify the API endpoint, HTTP method, timeout/retry behavior, full validation-failure path, or detailed failure-counter reset/unlock rules. It uses a different cover function ID from the function-list IDs without explicitly mapping them. The final Markdown preserves these as review questions, not fabricated requirements. Flow connections inferred from visual placement remain explicitly tentative. Mermaid syntax was inspected but not rendered by a Mermaid browser engine in this run.
