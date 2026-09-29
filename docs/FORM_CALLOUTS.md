# Form hard-copies and callout comments

## Output contract

A source screenshot is evidence, not the target specification. Preserve its original bytes, then express the reviewed arrangement in semantic HTML. Never rebuild the worksheet's narrow grid.

Floating DrawingML callouts are independent of cells. Extract their text from the workbook drawing parts. Preserve each callout ID, explicit target, original wording and source sheet. Do not guess a target from proximity alone.

Emit both an HTML comment and a visible specification note. Bind the visible note to the relevant input, button or message region. Comments must not become the only representation of an engineering requirement.

The HTML form is a **static layout reference**, not a working authentication application. Use source-backed labels, control types, required flags and limits. Blank screenshot inputs do not establish initial values. Do not invent an API endpoint, submission behavior or reset semantics.

## Executed fixture

`input/japanese_program_spec_with_callouts.xlsx` extends the five-sheet Japanese fixture with `画面ハードコピー_ログイン`: one embedded PNG and five editable rounded callout shapes. Existing sheet values and formulas are unchanged. The original workbook is retained separately.

| Callout | Target | Source note |
|---|---|---|
| C01 | userId | 半角英数字で入力。必須、最大50文字。 |
| C02 | password | マスク表示。必須、最大128文字。 |
| C03 | loginButton | 入力チェック成功後に認証APIを呼び出す。 |
| C04 | clearButton | 入力値を消去する。 |
| C05 | errorArea | エラーコードに対応するメッセージを画面上部に表示する。 |

## Fixture availability

The executed binary workbook and PNG assets are supplied in the downloadable conversation run bundle, not in this Git commit. Extract its `input/` directory into the repository before running the commands below. The bundle also contains the final Markdown, standalone HTML, all loop candidates and browser screenshots. No workbook is changed during conversion.

## Run

```bash
python -m pip install -r requirements.txt
python -m src.form_evolution input/japanese_program_spec_with_callouts.xlsx \
  --contract tests/fixtures/japanese_program_spec_with_callouts.contract.json \
  --layout-review tests/fixtures/login_hardcopy.layout.json
```

This produces the final Markdown, directly viewable HTML, extracted PNG, source map, and all executed candidates/reports. The same 39 checks apply to every loop. The previous semantic converter is the baseline; later revisions add HTML and callout handling. Stop on acceptance, at five loops, or when no candidate changes.

The bundle includes both the original five-sheet fixture and the expanded six-sheet fixture. With both files in `input/`, run:

```bash
python -m unittest discover -s tests -p test_semantic_review.py -v
python -m unittest discover -s tests -p test_form_callouts.py -v
```

The source is never saved by the converter. The reviewed contract binds both cell meaning and drawing/media/relationship bytes, so changing only a screenshot or callout invalidates the source review.

## Review boundary

The layout map records a **visually reviewed arrangement**, not OCR results. Control definitions are read from the workbook; callout text is read from DrawingML. The evaluator contract is not used as renderer input.

A new screenshot needs its own source review and image-bound layout map. Unbound notes, unknown controls, unsupported media and unreviewed images must be surfaced; do not declare a general-purpose image-understanding success. Traditional cell notes are inventoried, but their association/rendering is not part of this fixture's supported path. Legacy VML drawings, SmartArt, grouped diagram inference and text baked into images require additional work/review.

The fixture builder `tests/make_hardcopy_test.py` uses the artifact-tool editing runtime; this is not a runtime dependency of conversion. The browser QA script uses Playwright and system Chromium and is optional outside the supplied environment. Rebuilding the workbook can change drawing IDs; review the rebuilt file before refreshing the contract.

## HTML association references

The generated form uses explicit label/ID association and `aria-describedby` to link controls to explanatory notes:

- https://developer.mozilla.org/en-US/docs/Web/Accessibility/Guides/Understanding_WCAG/Text_labels_and_names
- https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-describedby
