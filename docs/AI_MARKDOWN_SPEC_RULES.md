# AI-readable Markdown specification rules

## 1. Objective

Convert an Excel programming/system specification into a standalone semantic Markdown specification optimized for machine reasoning and human review.

The output should answer engineering questions without requiring the reader to reconstruct the workbook's visual layout.

## 2. Core transformation rule

Preserve meaning; normalize presentation.

Excel coordinates, merged cells, borders, narrow columns, colors, and visual spacing are interpretation signals. They are not normally specification content.

A width-2 Japanese layout grid may help identify which labels and values belong together, but the final Markdown should express that relationship directly.

## 3. Recommended document shape

Use only sections supported by the source.

- Document information
- Revision history
- Overview
- Inputs and outputs
- UI fields
- Validation
- Processing flow
- Business rules
- APIs / external interfaces
- Data changes
- Error handling
- Messages
- Security
- Source traceability

## 4. Cover and sheet headers

Convert cover metadata into a compact Item/Value table. Keep revision history in a separate table.

For repeated sheet headers, prefer a compact metadata block such as:

    > **機能名:** ログイン認証処理
    > **作成者:** 山田 太郎
    > **作成日:** 2026-09-28
    > **版数:** 1.0

Do not render header information as A1, E1, O1, S1 cell rows.

## 5. Tables and lists

Use Markdown tables when information is naturally tabular: field definitions, message catalogs, function lists, interface parameters, and code/value mappings.

Prefer roughly 3–8 meaningful columns. If a source table is extremely wide, split it by concept instead of carrying the workbook width into Markdown.

Use lists for rules, notes, preconditions, postconditions, and compact key/value information.

## 6. Screen/form specifications

For a screen sheet, prioritize:

1. screen purpose or overview;
2. field-definition table;
3. validation and interaction rules;
4. optional HTML form mockup.

A useful form mockup expresses control semantics, for example:

    <form aria-label="ログイン">
      <label>ユーザーID <input type="text" name="userId" maxlength="50" required></label>
      <label>パスワード <input type="password" name="password" maxlength="128" required></label>
      <button type="button" id="loginButton">ログイン</button>
    </form>

Do not reproduce a 26-column width-2 Excel grid as HTML cells.

## 7. Processing flows

Use Mermaid when relationships can be inferred with reasonable confidence. A good flow exposes sequence and decision branches explicitly.

If branch direction is uncertain, state the uncertainty rather than inventing logic.

## 8. Requirements and rules

Make requirements explicit. Good statements identify a condition, constraint, action, or result.

Examples:

- ユーザーIDは必須かつ50文字以内。
- APIの戻り値がSUCCESSの場合は認証成功とする。
- パスワードはログへ出力しない。
- 認証失敗が5回連続した場合はアカウントをロックする。

Do not infer new business rules from colors, spacing, or formatting alone.

## 9. Traceability

Traceability should normally be at sheet or logical-section level.

Example:

- 表紙: 文書情報・改訂履歴
- 画面仕様_ログイン: 画面項目・フォーム
- 処理フロー_ログイン: Mermaid処理フロー
- 詳細仕様_ログイン: バリデーション・エラー・セキュリティ・メッセージ

Cell coordinates may be used for debugging exceptional ambiguity, but they should not be the primary final format.

## 10. Penalized patterns

The evaluator penalizes these because they reduce AI readability:

- Source grid sections
- tables keyed by A1, B17, and similar cell coordinates
- merge=A1:D1 style metadata
- col_width metadata
- data-grid-width metadata
- long merged-range inventories
- giant HTML tables representing the worksheet grid
- duplicated raw source content added only to increase literal coverage

## 11. Evaluation rubric

| Dimension | Weight | Intent |
|---|---:|---|
| Sheet traceability | 10% | Every meaningful sheet is represented semantically |
| Meaningful content coverage | 20% | Important source facts remain available |
| Metadata | 10% | Function/document identity is preserved |
| Specification structure | 20% | Output looks like an engineering specification |
| Requirement explicitness | 20% | Conditions, constraints, actions, and outcomes are explicit |
| AI readability | 20% | Output is chunkable and free of spreadsheet-shaped noise |

Default PASS gates:

- total score at least 88;
- sheet traceability 100%;
- meaningful content coverage at least 80%;
- metadata at least 80%;
- specification structure at least 75%;
- requirement explicitness at least 80%;
- AI readability at least 80%.

Literal cell coverage is intentionally not a pass gate.

## 12. Five-pass behavior

The quality loop stops as soon as the result passes.

If it fails, later passes add semantic aids rather than raw Excel detail:

1. semantic baseline;
2. analysis index;
3. extracted explicit requirements;
4. sheet-level traceability;
5. additional unmapped source facts as normal bullets.

The fifth pass must still avoid raw cell dumps.
