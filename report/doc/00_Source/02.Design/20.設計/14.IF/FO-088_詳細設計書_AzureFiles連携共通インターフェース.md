# FO-088 詳細設計書版：逐次変換・独立評価結果

## 結果

**未変換のFO-088詳細設計書版1件を可視範囲9章へ変換した。独立内容確認62/62、HTML表示確認14/14、Mermaid 7図×2設定の14描画を通過。選択式QA19項目・29回答単位は未回答。**

[本文](../../../../../../output/doc/00_Source/02.Design/20.設計/14.IF/FO-088_詳細設計書_AzureFiles連携共通インターフェース.md) ／ [QA](../../../../../../qa/doc/00_Source/02.Design/20.設計/14.IF/FO-088_詳細設計書_AzureFiles連携共通インターフェース.md)

変換済みのFO-088設計書版、FO-006・FO-007・FO-008・FO-014・FO-087等は再変換せず、既存のルール・Python・入力Excel・成果物も変更していない。組立・新規検査は一時領域のみで実行した。通過は原資料の保持・構成・表示の確認であり、原資料の矛盾解消や実装完了ではない。

## 入力・保存先

| 項目 | 内容 |
| --- | --- |
| 添付元 | 02.Design.zip |
| ZIP内の対象 | 02.Design/20.設計/14.IF/FO-088_詳細設計書_AzureFiles連携共通インターフェース.xlsx |
| リポジトリ入力 | input/doc/00_Source/02.Design/20.設計/14.IF/FO-088_詳細設計書_AzureFiles連携共通インターフェース.xlsx |
| 入力サイズ | 312281 bytes |
| 入力Git blob | c2250207badd19495250959dd8fec69169875784 |
| 入力SHA-256 | 095550fcc07e15c90e35bfcf46babe1d1268546961b138e9962dcc1fb66dfb9e |
| 原本整合性 | 全ZIPエントリのCRC、64 XML/Relationshipの構文検査を通過 |
| 開始時main | 947f85ee9d2cfd2d3ebb5a68d146fc4d5c6b9f8a |
| 適用ルールblob | 1a201ae35a411952088cd960cc1cd61527218055 |
| 保存先 | tujinrong/temp の main |
| 本文 | output/doc/00_Source/02.Design/20.設計/14.IF/FO-088_詳細設計書_AzureFiles連携共通インターフェース.md |
| 質問 | qa/doc/00_Source/02.Design/20.設計/14.IF/FO-088_詳細設計書_AzureFiles連携共通インターフェース.md |
| 結果報告 | report/doc/00_Source/02.Design/20.設計/14.IF/FO-088_詳細設計書_AzureFiles連携共通インターフェース.md |
| 文字コード・改行 | UTF-8、BOMなし、LF |

## 対象範囲と読み方

全17シートから非表示7シートと変更履歴1シートを除き、残る9シートをExcelタブ順に整理した。対象シートに非表示行・列、行高0・列幅0は検出されなかった。DFD、補足説明、プログラムフロー図の凡例区画は除外し、非表示内容をQAや補完の根拠へ戻していない。

表紙・同一共通ヘッダー・対象形式と保守責任を「はじめに」へ集約した。設計書／基本設計書／詳細設計書の文書種別は原表記を保持しQ01へ分離。空欄と明示された空文字・既定値Onceを区別する。第6章はこの版では元タブ7であり、前版のタブ位置を流用しない。

| 元タブ | 本文章 | 出典シート | 内容 |
| --- | --- | --- | --- |
| 1 | 1 | 表紙 | はじめに・共通情報 |
| 3 | 2 | 処理概要 | 対象テキスト形式、呼出タイミング、責任範囲 |
| 4 | 3 | テーブル一覧 | 3マスタの論理名・物理名・I/O |
| 5 | 4 | DFD | 出力・取込の2図 |
| 6 | 5 | イベント説明 | API、引数、戻り値、検索式、手順、メッセージ |
| 7 | 6 | 補足説明 | 役割別ファイル受渡し2図・出力6項目／取込7項目 |
| 14 | 7 | レビュー指摘事項 | 確認済み4件の原記録をQAへ分離 |
| 15 | 8 | オブジェクト一覧 | 2クラス |
| 16 | 9 | プログラムフロー図 | 出力・取込・共通認証の3図 |

## 詳細設計書版の保持事項

第1.1版、更新2025-03-10／JBS石岡を保持した。outPutTextFile()の4引数、loadTextFile()の2引数・2戻り値、3マスタ、6項目の出力設定と7項目の取込設定、Work/Send/Receive/Archive/Errorの役割を区別する。引用符を二重にする出力例と、コンマを含む項目の例をこの版から転記した。

この版のオブジェクト一覧にはSJ_AzureFilesUtilsとSJ_LoadTextFileValueの2クラスがある。前版の未記入状態を引き継がない。第5章の2戻り値との関係が明記されていない点はQ18に残した。検索式のアスタリスク、ドット、アンダースコア、全てのメッセージ・引数対応を原記載どおり保持し、取得元の誤記らしき箇所も自動修正しない。

### 原プログラムフローの不一致

原図のグループ内文字・コネクタ接続先・分岐のラベルと位置を突合した。3つのプログラムフローにある81本の接続の始点・終点を独立に照合し、追加の処理順や逆向きの線を作っていない。問題のある原図をそのまま確定仕様だと推奨するものではなく、次の不一致を本文に注記し選択式QAへ分離する。

| QA | 原資料のまま保持した論点 |
| --- | --- |
| Q14 | ファイル名がブランクかのYesが引数3、Noが出力定義を選ぶ原図と、イベント説明の反対の記載 |
| Q15 | 上書き禁止でファイルが存在するかのNoが警告、Yesがストリーム作成へ進む原図と、イベント説明の存在時拒否 |
| Q16 | 3つのループに「終了条件」として書かれたcounterの以下比較が、終了／継続のどちらを表すか |
| Q17 | 受領ファイル移動のリトライ設定元が、吹き出しではファイル取込定義、イベントではマウント定義となる差 |
| Q19 | 必須取込の件数0で、原図はfalse設定を経ず戻り値2設定へ進む一方、イベント表は異常終了 |

共通認証フローの初回はsleepなし、初回以外は1000ミリ秒停止してからマウントするという接続を保持した。原図の参照番号1・2は認証処理の共通参照点として説明する。通常の順序線とは違うループの開始／終了記号を、図にない戻り線やcounter初期化へ変換しない。

3つの比較式は図外のコード表記に原文を残した。図内だけは「以下」という等価な日本語へ置換し、文字参照が表示に残らないことを両描画設定で確認した。比較演算子の向きや条件を訂正したものではない。

## 表・図・注記と表示上の制約

この入力には変換対象の画面レイアウトがないため、架空の画面HTMLや入力部品は追加しない。HTMLプレビューは本文の表と描画済み7図を閲覧する確認用文書である。3つの補足注記とリトライ吹き出し1件を、対象付きHTMLコメントと可視注記で図の外に配置した。

表計算プレビューではグループ内の図形が一部描かれなかったため、そのプレビューだけでは判断していない。元のDrawingMLのグループ・接続ID・アンカー・位置と図形文字を確認し、位置関係確認用の描画およびMermaidプレビューを照合した。元のExcelをMicrosoft Excelアプリケーションで開く検査やピクセル単位の一致を保証するものではない。

記載されたnetUse、Azure Files接続、マウント、ファイル移動、マクロは実行しない。検証では元のExcelのバイト列も変更していない。原文に未定義の認証情報やネットワーク操作を補っていない。

## 評価ループ

| 変換候補 | 独立内容確認 | HTML表示確認 | Mermaid | 結果 |
| --- | --- | --- | --- | --- |
| 1 | 62/62 | 14/14 | 7図×2設定＝14描画 | PASS（業務QAは未回答） |

2～5回目は未実行。同一候補の再確認、組立コードの実行修正、評価器の負例試験は変換ループに加算しない。負例の初回試験では戻り値クラス名を説明段落だけで変更した場合を検出できなかったため、一時検査の段落とオブジェクト一覧の一致確認を強化した。実成果物は変えず62検査と負例12件を再実行して通過した。

### 独立内容確認

検査は一時領域のreview.pyで行い、組立プログラムをimportしていない。元ZIPの可視データと出力の表・条件の組を独立に照合する。全81接続と接続済みノードの文言の一致も、原DrawingMLから独立に検査した。単語の出現数やAI理解率の点数ではない。

| ID | 検査 | 結果 |
| --- | --- | --- |
| A01 | Exact source edition and CRC | PASS |
| A02 | Nine chapters in source tab order | PASS |
| A03 | Saved visible scope excludes seven hidden and one history sheet | PASS |
| A04 | No invented screens, raw grid, legend/history or report chapters | PASS |
| A05 | One H1 and UTF8 without BOM, LF | PASS |
| M01 | Cover/header metadata tuples | PASS |
| M02 | Shared scope, maintenance and receiving-side responsibility | PASS |
| F01 | Three exact table name/type/I-O associations | PASS |
| F02 | Output interface four arguments and defaults | PASS |
| F03 | Input interface two arguments and two returns | PASS |
| B01 | Outer joins and exact output query | PASS |
| B02 | Output incorrect argument references retained and queried | PASS |
| B03 | Input inconsistent query and argument references retained | PASS |
| B04 | Authentication bypass and device/user/password association | PASS |
| B05 | Lookup/auth warning message and translation IDs | PASS |
| B06 | Output folder path and warning parameter association | PASS |
| B07 | NonUpdate existence truth table | PASS |
| B08 | Output wildcard search patterns | PASS |
| B09 | Stream completion precedes file creation; source encoding and examples | PASS |
| B10 | Literal filename concatenation not silently fixed | PASS |
| B11 | Output work-to-send move paths | PASS |
| B12 | Success return excludes earlier failures | PASS |
| B13 | Input folder expressions retain wrong source master plus warning mapping | PASS |
| B14 | Input detection path and wildcard | PASS |
| B15 | Input existence truth table and early return | PASS |
| B16 | Busy-file retry policy retains exact settings and ambiguous break | PASS |
| B17 | Input renamed work path, extension and seconds timestamp | PASS |
| B18 | Read encoding and start-line 0/unspecified are equivalent to 1 | PASS |
| B19 | Quote removal preserved but ambiguity unresolved | PASS |
| B20 | Returned filename/data nested example preserved | PASS |
| B21 | Normal archive paths and continue | PASS |
| B22 | Read failure moves entire file to Error and stops | PASS |
| B23 | Final return count truth table | PASS |
| B24 | All six output and seven input function settings | PASS |
| R01 | Four original review questions and answers preserved verbatim in QA | PASS |
| R02 | Caller-level validation and partial import not common-IF behavior | PASS |
| R03 | All four review confirmation dates retained | PASS |
| G01 | Seven source diagrams including three real program flows | PASS |
| G02 | DFD six steps per direction in original order | PASS |
| G03 | DB reads target validation, not writes | PASS |
| G04 | DFD file read/write direction | PASS |
| G05 | Supplement roles, directories and outcome mapping | PASS |
| G06 | Original input file reference target preserved, not invented precedence | PASS |
| D01 | Output quoted stream and doubled-quote example retained | PASS |
| D02 | Wildcard examples not treated as defaults | PASS |
| D03 | Conflicting import type table heading is retained | PASS |
| D04 | Source blank-filename branches retained and queried | PASS |
| D05 | Source existing-file polarity retained and queried | PASS |
| D06 | Three literal loop end expressions retained as code | PASS |
| D07 | First/non-first mounting and 1000 millisecond sleep preserved | PASS |
| D08 | Retry note different source master preserved and queried | PASS |
| D09 | Mandatory zero-count source path not silently repaired | PASS |
| D10 | Both API contract and return helper class are kept | PASS |
| D11 | All 81 source connector endpoints preserved without extra graph edges | PASS |
| D12 | Every connected program node label retained; only documented safe notation changes | PASS |
| R04 | Rendered tables have no accidental separator/header rows | PASS |
| N01 | Four source notes retain visible wording and resolvable targets | PASS |
| P01 | Two detailed-edition class records | PASS |
| Q01 | Nineteen unique QA IDs; twenty-nine unanswered answer units | PASS |
| Q02 | Each QA has alternatives and uncertainty | PASS |
| Q03 | QA chapter order and no accepted candidate answers | PASS |
| Q04 | All current output/QA anchor links resolve; report path planned correctly | PASS |

### Mermaid合法性・実描画

既存の独立検査器を変更せず使用した。構文解析、SVG描画、エラー文字／図形、文字参照の表示残りを分けて確認し、表示不能を合格へ置き換えていない。

| 項目 | 値 |
| --- | --- |
| Mermaid | 11.12.2 |
| Chromium | 144.0.7559.96 |
| 設定 | securityLevel=strict、htmlLabels=true／false |
| MD SHA-256 | 9f9488a8302279869893d45faddfc06a536143cf3e45b1351ae6a18bc8c73164 |
| ランタイムSHA-256 | 625c6c7a184d2943daa91b6db511d03463089e7cac78c535091715e9b181f496 |
| 通信 | 外部通信を遮断しローカルJSのみ使用 |

| 図 | 開始行 | HTMLラベル | SVGテキスト |
| --- | --- | --- | --- |
| 1 | 76 | PASS | PASS |
| 2 | 97 | PASS | PASS |
| 3 | 457 | PASS | PASS |
| 4 | 491 | PASS | PASS |
| 5 | 580 | PASS | PASS |
| 6 | 647 | PASS | PASS |
| 7 | 735 | PASS | PASS |

ローカルESMのimport解決とプリロードをオフライン用に調整した既存資産を使用し、Mermaidの構文解析・描画実装自体は変更していない。今回の版・設定での結果であり、未検証のすべてのエディタに対する表示保証ではない。

### HTML表示確認

| 検査 | 結果 |
| --- | --- |
| Nine rendered sheet chapters | PASS |
| No fabricated screen controls or executable scripts | PASS |
| All table rows have matching column counts and no separator rows | PASS |
| Unique HTML/SVG element identifiers | PASS |
| No HTML leaked as code | PASS |
| Three wildcard expressions remain visible including both asterisks | PASS |
| Seven actual nonempty SVG diagrams | PASS |
| No renderer error graphics or text | PASS |
| Visible source notes and stable targets | PASS |
| No browser errors or external requests | PASS |
| Document fits 420px viewport; wide tables scroll locally | PASS |
| Source Markdown unchanged by preview/evaluation | PASS |
| Program labels do not expose entity placeholders | PASS |
| Three loop formulas remain literal in rendered tables | PASS |

### 評価器の負例試験

入力版、引数型、物理名、NonUpdate条件、必須ファイルなしの動作、ファイル名分岐、既存ファイル分岐、比較演算子、sleep時間、取込0件分岐、戻り値クラス名、QAの回答注入の12候補をすべて不合格と判定した。これらの誤りを実成果物には保存していない。

## 中間保存・保護・残る作業

checkpoint/FO-088-detail-095550fcc07e/へ冒頭3章の実データと入力・ルールのハッシュ、次工程を保存した。メモだけの状態と完全な候補を区別し、最終3ファイルがmainに保存され、再取得で照合されるまでは削除しない。完了後に削除してよいのはこの入力に対応する中間ファイルのみ。他の文書の状態や既存成果物は変更しない。

これは逐次処理の1ファイル分の報告であり、残る全ファイルを完了したという報告ではない。最終成果物と実行検証JSON、候補、一時コードを検証用ZIPへ保存する。バックグラウンドで未処理ファイルを自動変換する機能ではない。

業務QAは19項目・29回答単位で未回答。4件の既存レビューは原記録で、確認済み回答への再回答を求めない。特に原プログラムフローの分岐とイベント説明の不一致は、実装前に回答する必要がある。

## 出力ハッシュ

| 成果物 | SHA-256 |
| --- | --- |
| output | 9f9488a8302279869893d45faddfc06a536143cf3e45b1351ae6a18bc8c73164 |
| qa | 6b4e0fff496999a41a4493ed50a6bcdb6116a515b2334eed7fdb3efce2e51130 |
