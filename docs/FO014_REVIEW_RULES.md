# FO-014の追加変換・独立評価規則

共通AGENTS.mdを変更せず、FO-014の特定入力版に対する追加検査として適用する。

- 対象入力SHA-256は8cfb0e50272542dc6270dd318d911b279661175a6b9433f7535930a3eb383d55。変更した版には内容確認と期待値の再審査が必要。
- 帳票47項目の出力値、取得元、Tmpフィールド、書式・配置・幅を別表に分けるが、番号の対応を失わない。
- Tmp20項目の論理名/物理名/設定式、15テーブル、7オブジェクトの対応を保持する。
- 保存済み文字列のふりがなメタデータを本文へ連結しない。表示されている文字を維持する。
- 取り消し線の旧要件や既存レビュー回答を、新規の現行仕様として復活させない。条件が矛盾するときはQAへ分離する。
- CommonMarkではHTML内の空行がHTMLブロックを切ることがある。画面/帳票フレームを単一のHTMLブロックとして出力し、MarkdownをHTMLへ変換した後にDOMを検査する。
- ファイル内の文字列存在だけで合格にしない。手数料/差引支払金額等が実際のtable/tr/tdに含まれることと、HTMLコードがpreへ漏れていないことを検査する。
- 現行帳票と旧帳票例を分離する。現行にないVAN立替金を現行仕様へ追加しない。
- source-specific tools/review_fo014.pyはbuilderをimportせず、添付原本と確定候補から独立判定する。Mermaid検査は既存の独立パーサー/描画器を変更せず使用する。
- 表示・印刷の余白やCSVの未記載契約、相殺抽出の仕入先/法人/年範囲、銀行手数料取得元を自動補完しない。
- 入力とFO-006/FO-007の確定成果物・共通コードを変更しない。新規追加コードは単体テストする。
- 再開はdocs/CHECKPOINTS.mdに従う。工程の保存成功と最終main納品成功を区別する。

## コードの配置と再現

GitHubのmainには、本規則、独立検査 `tools/review_fo014.py`、表示文字列ヘルパー、チェックポイント処理とそのテストを保存する。FO-014特定版の組立・QA生成・プレビュー処理を含む再現用コード一式は、納品の `FO-014_verification.zip` にまとめる。以下はこの検証ZIPを展開したルートで実行する。既存のFO-006・FO-007の変換器・成果物を上書きする操作ではない。

Python環境に既存依存とmarkdown-it-py、beautifulsoup4、Playwrightを用意し、ChromiumとローカルMermaidを使用する。原本はinput/へ置く。

```bash
python -m tools.inspect_source input/FO-014_詳細設計書_支払案内書.xlsx
python -m tools.build_fo014
python -m tools.build_qa
python -m tools.review_fo014 input/FO-014_詳細設計書_支払案内書.xlsx output/FO-014_詳細設計書_支払案内書.md qa/FO-014_詳細設計書_支払案内書.md --json verification/content.json
python -m src.independent_evaluate output/FO-014_詳細設計書_支払案内書.md --acceptance-json verification/content.json --expected-count 2 --asset-map work/mermaid-assets.json --browser-path /usr/bin/chromium --artifacts verification/svg-loop1 --json verification/independent.json
python -m tools.preview_and_browser --attempt 2
python -m unittest discover -s tests -v
```

この組立は確認済み画像解釈を含む特定版向け再現処理であり、任意の新しいExcelに対する無審査の汎用変換ではない。Mermaid実行資産は別途ローカルに用意し、版とハッシュを記録する。
