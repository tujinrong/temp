# FO-088 設計書版：単独変換・独立評価結果

## 結果

**次の未変換ファイル「FO-088_設計書_AzureFiles連携共通インターフェース.xlsx」1件を対象に、可視範囲を9章へ変換した。修正後は独立内容確認49/49、HTML表示確認12/12、Mermaid 4図×2設定の8描画を通過。業務QA13項目（回答単位20件）は未回答。**

[本文](../../../../../../output/doc/00_Source/02.Design/20.設計/14.IF/FO-088_設計書_AzureFiles連携共通インターフェース.md) ／ [QA](../../../../../../qa/doc/00_Source/02.Design/20.設計/14.IF/FO-088_設計書_AzureFiles連携共通インターフェース.md)

既存のFO-087設計書版・詳細設計書版は保存済みであることを確認し、再変換していない。FO-088詳細設計書版も今回の対象外。合格は原資料の保持・構成・表示の確認であり、未確定の仕様承認やアプリケーションの実装完了ではない。

## 入力・保存先

| 項目 | 内容 |
| --- | --- |
| 添付元 | 02.Design.zip |
| ZIP内の対象 | 02.Design/20.設計/14.IF/FO-088_設計書_AzureFiles連携共通インターフェース.xlsx |
| リポジトリ入力 | input/doc/00_Source/02.Design/20.設計/14.IF/FO-088_設計書_AzureFiles連携共通インターフェース.xlsx |
| 入力サイズ | 266783 bytes |
| 入力Git blob | 97f67b07e639a37d4e29886331a5ebdcb4992f88 |
| 入力SHA-256 | d0adcb2d9fb077f4e02434e1b2a232a4ba03772e2d8958b3ac9b5cd768e21b75 |
| 整合性 | ZIP全エントリのCRC・XML構文検査通過 |
| 開始時main | 8bfdc69fe6806d6c45561f8ccd8ae015da82b8b3 |
| 適用ルールblob | 1a201ae35a411952088cd960cc1cd61527218055 |
| 保存先 | tujinrong/temp の main |
| 本文 | output/doc/00_Source/02.Design/20.設計/14.IF/FO-088_設計書_AzureFiles連携共通インターフェース.md |
| 質問 | qa/doc/00_Source/02.Design/20.設計/14.IF/FO-088_設計書_AzureFiles連携共通インターフェース.md |
| 報告 | report/doc/00_Source/02.Design/20.設計/14.IF/FO-088_設計書_AzureFiles連携共通インターフェース.md |
| 文字コード・改行 | UTF-8、BOMなし、LF |

## 対象範囲と読み方

全17シートから非表示7シート・変更履歴1シートを除き、残る9シートを保存されたExcelタブ順で章にした。対象シートでは非表示行・列、行高0・列幅0は検出されなかった。DFD、補足説明、プログラムフロー図の凡例を除外し、非表示内容をQAや補完の根拠へ戻していない。

表紙・同じ共通ヘッダー・共通条件は「はじめに」へ集約。文書種別の設計書／基本設計書／詳細設計書という表記差はQ01へ残す。「原資料空欄」は未指定であって、空文字や任意を新たに指定する表現ではない。引数3のデフォルト空文字と起動回Onceは、明示された指定として保持する。

| 元タブ | 本文章 | 出典シート | 主な内容 |
| --- | --- | --- | --- |
| 1 | 1 | 表紙 | はじめに、文書情報、対象形式・保守・アーカイブ責任 |
| 3 | 2 | 処理概要 | 出力・取込の目的、使用タイミング、制限 |
| 4 | 3 | テーブル一覧 | 3マスタの論理名・物理名・I/O |
| 5 | 4 | DFD | 出力・取込それぞれの処理順とDB・ファイルの参照方向 |
| 6 | 5 | イベント説明 | 2メソッド、引数・戻り値、認証・検索・移動・リトライ・エラー |
| 13 | 6 | 補足説明 | 役割別のファイル受渡し2図、出力6項目・取込7項目の設定 |
| 14 | 7 | レビュー指摘事項 | 確認済み回答の適用範囲。原記録4件はQAへ分離 |
| 15 | 8 | オブジェクト一覧 | 具体的な一覧は未記入 |
| 16 | 9 | プログラムフロー図 | 具体的なフローは未記入 |

第8・9章は読み取り失敗ではない。番号だけのオブジェクト行や凡例だけのフローを、内容があるものとして扱わない。他版の実装一覧・フローや、別資料にあった「詳細設計・開発時に記載」という文言は持ち込まない。第5章にあるClasses/SJ_AzureFilesUtilsの呼出定義は、未記入のオブジェクト一覧とは区別する。

## 重要な意味と原資料の不一致

出力メソッドoutPutTextFile()の4引数、取込メソッドloadTextFile()の2引数と2戻り値を保持。NonUpdateの既存ファイル拒否、NonNormalのファイルなし正常終了、NonErrorのファイルなし異常終了を条件と結果の組として検査した。認証・フォルダ・ファイル・リトライの各メッセージID、文言、引数、ラベルIDの対応を保持した。

Work経由の出力、ストリーム完成後の実ファイル出力、受領ファイルのタイムスタンプ付きリネーム、正常時Archive移動、異常時Error移動と中断を区別する。読み込み開始行0／未設定は1行目と同様。受領側がアーカイブする責任と、桁数・必須等の業務チェックは各機能側で行うという確認済みレビューを保持した。

原資料の引数番号、取込処理が参照する出力定義マスタ、ファイル名のドット・アンダースコア、リトライ上限後の「手順[2-5]へ。（ループのbreak）」の不一致・曖昧さは修正せずQAへ分離した。Q02～Q05は論点別の回答表を設け、選択式QA13項目を20回答単位に分けた。既存レビュー4件は全件確認済みの原記録として扱い、未回答質問には数えない。

## 図・表示の確認

原資料の可視セル、DrawingMLの文字・グループ・コネクタ接続先と矢印向き、画像を突き合わせた。対象シートの描画要素154件のうち凡例26件を除外し、残る128要素の役割を確認した。これは128件の独立した図を意味しない。外部システムの画像は役割アイコンとして扱い、原図にない機能を追加していない。

変換対象の画面レイアウトはないため、画面HTML・入力部品は作成しない。HTMLプレビューはMarkdown表と4つのMermaidを表示する確認用文書であり、原資料に新しい画面を追加するものではない。注記3件は対象付きHTMLコメントと可視本文を併記し、図の外に置いた。

DFDの2マスタを囲むDB群は各マスタの参照線へ展開したが、SQLや取得順序を新たに定義しない。補足説明の取込図にあるWorkから認証への原参照線は保持し、それを新しい実行順の要件にはしないと図外へ明記した。囲みはD365・共通IF・Azure Filesの役割として表し、単なる囲みを処理ステップへ変えない。

表計算プレビューでは一部のグループ内図形や接続が省略されたため、プレビューだけで判断していない。Microsoft Excelアプリケーションでの表示、ピクセル単位の配置一致、全エディタでのMermaid互換性は保証していない。記載されたnetUseやAzure Filesの接続処理は実行せず、マクロ・外部システムへの通信も行っていない。

## 評価ループ

同じ最終49内容検査・12表示検査を、保存した2候補に適用した。描画が成功しても、検索式の意味が失われる候補は合格にしない。

| ループ | 独立内容確認 | HTML表示確認 | Mermaid | 判定・修正 |
| --- | --- | --- | --- | --- |
| 1 | 47/49 | 11/12 | 4図×2設定＝8描画成功 | RETRY。3つの検索式のアスタリスクがMarkdown強調として解釈され、表示上消える問題を検出。 |
| 2 | 49/49 | 12/12 | 4図×2設定＝8描画成功 | PASS。3式をコード表記に変更し、原式の文字・値・参照先を維持。 |

変更は3式を囲む6個のバッククォートだけ。QA、処理条件、メッセージ、図の接続は変えていない。3～5回目は不要のため未実行。途中の組立コードの構文修正、同じ候補の再検査、負例試験は変換ループに加算していない。

### 独立内容確認

内容検査は一時領域のreview.pyで実施し、組立プログラムをimportしない。原Excelの可視データを独立に読み、MarkdownをHTML化した後の表の値・参照・条件の組を照合した。

| ID | 検査 | 判定 |
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
| G01 | Four source diagrams; no invented program flow | PASS |
| G02 | DFD six steps per direction in original order | PASS |
| G03 | DB reads target validation, not writes | PASS |
| G04 | DFD file read/write direction | PASS |
| G05 | Supplement roles, directories and outcome mapping | PASS |
| G06 | Original input file reference target preserved, not invented precedence | PASS |
| N01 | Three source notes retain visible wording and resolvable targets | PASS |
| P01 | Object chapter not filled with another edition | PASS |
| Q01 | Thirteen unique QA IDs; twenty unanswered answer units | PASS |
| Q02 | Each QA has alternatives and uncertainty | PASS |
| Q03 | QA chapter order and no accepted candidate answers | PASS |
| Q04 | All current output/QA anchor links resolve; report path planned correctly | PASS |

### Mermaid合法性・実描画

既存のmermaid_validate.pyとindependent_evaluate.pyを、GitHubと同じバイト列のコピーのまま使用した。正規表現だけの検査ではなく、実パーサー・SVG描画を実行し、Unsupported markdown等のエラー文字や図形がないことを確認した。4図は原資料の出力DFD・取込DFD・出力補足図・取込補足図に対応する独立した期待数。

| 項目 | 値 |
| --- | --- |
| Mermaid | 11.12.2 |
| Chromium | 144.0.7559.96 |
| 設定 | securityLevel=strict、htmlLabels=true/false |
| ランタイムSHA-256 | 625c6c7a184d2943daa91b6db511d03463089e7cac78c535091715e9b181f496 |
| 外部送信 | なし。ローカルのESM資産を使用。 |

| 図 | MD開始行 | HTMLラベル設定 | SVGテキスト設定 |
| --- | --- | --- | --- |
| 1 | 76 | PASS | PASS |
| 2 | 97 | PASS | PASS |
| 3 | 446 | PASS | PASS |
| 4 | 480 | PASS | PASS |

### HTML表示確認

これは画面再現の評価ではなく、Markdownから生成した文書・表・図の表示検査。画面・フォームが対象外であることも検査する。

| ID | 検査 | 判定 |
| --- | --- | --- |
| H01 | Nine rendered sheet chapters | PASS |
| H02 | No fabricated screen controls or executable scripts | PASS |
| H03 | All table rows have matching column counts and no separator rows | PASS |
| H04 | Unique HTML/SVG element identifiers | PASS |
| H05 | No HTML leaked as code | PASS |
| H06 | Three wildcard expressions remain visible including both asterisks | PASS |
| H07 | Four actual nonempty SVG diagrams | PASS |
| H08 | No renderer error graphics or text | PASS |
| H09 | Visible source notes and stable targets | PASS |
| H10 | No browser errors or external requests | PASS |
| H11 | Document fits 420px viewport; wide tables scroll locally | PASS |
| H12 | Source Markdown unchanged by preview/evaluation | PASS |

### 評価器の負例試験

10種類の意図的な改変を、すべて不合格と判定した。改変はテスト用文字列だけで、実成果物を変更していない。

| 改変 | 検出された内容検査 |
| --- | --- |
| Table physical name corruption | F01 |
| Wrong output container argument | F02 |
| Overwrite prohibition accepts existing file | B07 |
| Wildcard expression loses code protection | B08 |
| Required input accepts no file | B15 |
| Business review silently changes receiving responsibility | M02 |
| DFD table input reversed | G03 |
| File move success goes to error | G05 |
| Required diagram deleted | G01, G02, G03, G04 |
| QA answer incorrectly preselected | Q01, Q03 |

内容確認とMermaidの両方を同一MDハッシュで照合する既存の独立最終判定に、今回のブラウザー確認も合わせて最終PASSとした。これらは本入力版の受入検査であり、AI理解率100%や任意Excelの汎用変換精度を保証するものではない。

## 保存・再開・保護範囲

既存AGENTS.md、docs、src、tools、tests、元Excel、変換済み成果物は変更しない。今回の組立・検査の補助処理は一時フォルダに限定した。検証ZIPには、候補2件、本文・QA、可視抽出データ、検証JSON、ローカル実描画SVG、再現用の一時コードを含める。除外した非表示内容を抽出データとして収録しない。

789039aのコミットで冒頭3章と入力ハッシュ・次工程の状態をcheckpoint/FO-088-design-d0adcb2d9fb0へ保存した。これは最終変換完了ではなく途中保存。最終3ファイルをmainへ保存し、再取得したblobハッシュが一致してから、この文書のチェックポイントだけを削除する。他文書の中間状態や入力は削除しない。通常の削除なのでGit履歴は残る。

完了時のコミット番号と再取得照合は納品記録に記載する。本報告自体には自己参照のコミット番号や自己ハッシュを埋め込まない。

## 成果物のハッシュ

| 成果物 | SHA-256 |
| --- | --- |
| output | 1349ce364a0de601a4d205ced20ec0a2c2c824a345ed108d463a9f3658605c2e |
| qa | f70740a10499cf6b86070151bb5257478861d75202740a30186923b0f861f92a |

入力は変換後も同じサイズ・ハッシュを維持する。未回答QAの候補を確定仕様にしたり、未記入の一覧を他版で埋めたりしていない。
