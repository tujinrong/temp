# LedgerJournalTrans 仕訳帳明細行：テーブル定義書：変換・独立評価結果

## 結果

**未変換の1ファイルを2章のMarkdownへ変換。独立内容確認23/23、HTML表示確認11/11を通過。原資料に対象図はなく、Mermaidは期待図数0として対象外。新規QAは2件。**

[本文](../../../../../../../output/doc/00_Source/02.Design/20.設計/20.データ定義書/01_テーブル定義書%20%20%28Table%20Definition%29/【テーブル定義書】LedgerJournalTrans%20_仕訳帳明細行.md) ／ [QA](../../../../../../../qa/doc/00_Source/02.Design/20.設計/20.データ定義書/01_テーブル定義書%20%20%28Table%20Definition%29/【テーブル定義書】LedgerJournalTrans%20_仕訳帳明細行.md)

## 入力と保存先

| 項目 | 内容 |
| --- | --- |
| 添付元 | 02.Design.zip |
| 原本 | input/doc/00_Source/02.Design/20.設計/20.データ定義書/01_テーブル定義書  (Table Definition)/【テーブル定義書】LedgerJournalTrans _仕訳帳明細行.xlsx |
| 入力サイズ | 58357 bytes |
| 入力Git blob | 2da653e9e470a04d946852358622411a6846529f |
| 入力SHA-256 | 55ab034994ecc8f89e63e1e3dbea66ca3d2769dbebb0f455d92a02d83d3bc879 |
| 入力整合性 | ZIPの全CRCと46 XML/Relationshipの構文検査を通過 |
| 保存先 | tujinrong/temp / main |
| 文字コード・改行 | UTF-8、BOMなし、LF |

input/を除いた相対パスとファイル名をoutput・qa・reportに保持し、拡張子のみ.mdへ変更する。フォルダ名の2つの空白と括弧、ファイル名の空白も変更しない。リンク内だけ必要な文字をエンコードする。

## 対象範囲と読み方

全4シートから非表示1シート・変更履歴1シートを除き、可視の2シートをExcelタブ順で整理した。可視シートに非表示行・列やゼロ寸法は検出されなかった。保存状態で非表示のノート表示枠12件は本文・QAへ転記しない。

| 元タブ | 本文章 | 元シート | 内容 |
| --- | --- | --- | --- |
| 2 | 1 | テーブル定義 | 文書情報、テーブル属性、1項目のフィールド定義 |
| 3 | 2 | その他定義 | フィールドグループ、インデックス、リレーション、Deleteアクション、メソッド |

表紙はないため、可視のテーブル定義とその他定義の2章とした。番号のみの未使用行と、非表示のノート枠は仕様として転記しない。

原資料の右欄にある列挙値「０:No,1:Yes」を、見出しのない補足欄の内容として保持した。０は原資料の全角文字のままであり、明記されていない初期値へは変換しない。

テーブル物理名末尾の半角空白は␠で可視化し、型名内部の半角空白とともにQAへ分離した。表示上の空白を理由に識別子を無断で修正しない。

原資料プレビューのヘッダー数式は未対応のため#NAME?が表示された。本文はExcel内部に保存された日付・著者の表示値を採用し、非表示参照元は展開していない。

原資料空欄と「-」、NO・YESを区別した。番号しかない未使用テンプレート行はフィールドや業務要件として数えない。未記載の区分は「定義が存在しない」とは断定せず、未記載と記述する。

## 独立評価

| 候補 | 内容確認 | HTML確認 | Mermaid | 結果 |
| --- | --- | --- | --- | --- |
| 1 | 23/23 | 11/11 | NOT_APPLICABLE（期待0・出力0） | PASS |

候補1が最終検査を通過したため、候補2～5は生成していない。検査プログラムの起動経路の調整や、同じ候補の再検査を変換ループへ加算しない。

内容検査は組立プログラムをimportせず、原Excelの保存済みセル値・可視状態と、Markdownから生成したHTML表の行を照合する。文字の存在だけでなく、論理名・物理名・型・拡張データ型・桁数・PK・必須の対応を行単位で確認した。既存の独立最終判定器にも同じ本文ハッシュを渡した。

| ID | 内容・構造の検査 | 判定 |
| --- | --- | --- |
| A01 | Exact input edition and source integrity | PASS |
| A02 | Two visible sheet chapters in source order | PASS |
| A03 | Hidden/history scope independently checked | PASS |
| A04 | Only one title; no invented cover or report chapters | PASS |
| M01 | All saved cover/header metadata associations | PASS |
| M02 | All table properties and explicit blank label | PASS |
| F01 | Field column count and declared names | PASS |
| F02 | All non-template field rows included once | PASS |
| F03 | Every field attribute association matches source | PASS |
| F04 | No duplicated physical field definitions | PASS |
| O01 | Five other-definition sections keep source headings | PASS |
| O02 | Other-definition rows or blank state retained | PASS |
| S01 | Domain tables not worksheet grids | PASS |
| S02 | Hidden note boxes not converted; no invented visual objects | PASS |
| S03 | Rendered data not leaked into code blocks | PASS |
| S04 | Document encoding is UTF8 no BOM and LF | PASS |
| S05 | No rendering-only formula errors imported | PASS |
| Q01 | QA scope does not invent unanswered questions | PASS |
| Q02 | QA links resolve with spaces and parentheses encoded | PASS |
| Q03 | All specification links and anchors resolve | PASS |
| G01 | Reviewed diagram expectation zero has no source figures | PASS |
| P01 | Original workbook bytes remain unchanged | PASS |
| P02 | Significant edge spaces are explicit and reversible | PASS |

| ID | ブラウザー検査 | 判定 |
| --- | --- | --- |
| H01 | All domain tables are actual DOM tables | PASS |
| H02 | Field rows visible in correct column count | PASS |
| H03 | Displayed field values match reviewed rows | PASS |
| H04 | One title and two source chapters | PASS |
| H05 | No HTML source leaked into pre/code | PASS |
| H06 | No invented screen or executable input controls | PASS |
| H07 | No duplicate element IDs | PASS |
| H08 | Cached dates retained instead of renderer errors | PASS |
| H09 | At 420px only tables scroll horizontally | PASS |
| H10 | No browser errors or external requests | PASS |
| H11 | Evaluation did not change Markdown bytes | PASS |

ブラウザー：Chromium 144.0.7559.96。Markdownから生成した実DOMを検査し、幅420pxでも文書全体は横にはみ出さず、必要な表だけが横スクロールする。外部通信・JavaScriptエラーは0件。画面レイアウトは原資料にないため、HTMLフォームを創作していない。

負例検査は8件すべて不合格を検出した。桁数変更、物理名の誤り、必須属性の破壊、フィールド行削除、テーブルタイプの誤り、章名変更、原資料にない図の追加、QAリンク破壊を対象とする。変更は一時領域の検査用コピーのみで、実成果物へは適用していない。

## 制約・保存と保護

これは原資料の保持と表示の検証であり、実装全体の業務的な正しさやMicrosoft Excelとのピクセル単位の一致を保証しない。QAが0件の場合も、空欄を仕様として確定したことを意味しない。

既存のAGENTS.md、docs、src、tools、tests、入力Excel、変換済みの他ファイルは変更しない。補助コード・改善は今回のtmp配下だけで行った。ファイル単位で検証を完了してからmainへ保存し、保存先のGit blobを再取得して照合する。ローカル検査の成功だけをGitHub保存成功として扱わない。

| 成果物 | SHA-256 |
| --- | --- |
| output | d163fecbfddab34263528dab1f68fbc55f50bf7faddc47ff731dd66ac76d0efa |
| qa | e0950da5f05f4bf6e34030486a80b486fbc0c2c1d23a185c3382c3e9e742f78e |
