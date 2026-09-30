# HTML画面とMermaidの独立評価

## 必須の合格条件

独立した内容確認と、Mermaidの合法性・実描画確認の両方が、同じ最終Markdownに対して通過すること。旧評価の高得点だけで合格にはしない。変換器が「生成成功」と返しても、それを描画成功の証拠にしない。

`src/mermaid_validate.py` は変換器を呼ばず、出力MDを読み取り専用で検査する。検査中にラベルや矢印を修正しない。修正は変換側で行い、変更後のMDを再評価する。

| 段階 | 確認 |
|---|---|
| ブロック抽出 | 空・閉じ忘れのMermaidフェンス、期待図数の不足。別のコードフェンス内の例やHTMLコメント内は実図として数えない。 |
| 互換性検査 | `1. `、`- `等のリスト扱いされる可能性のあるラベル。これは独自の互換性ルールであり、構文パーサーではない。 |
| 構文検査 | 実際の `mermaid.parse()` による解析。未知の図種や不正構文を不合格にする。 |
| 実描画 | `mermaid.render()` でSVGを作り、非空・非ゼロ寸法とエラー表示を確認する。 |
| 描画設定 | `htmlLabels=true` と `htmlLabels=false` の両方で確認する。 |
| 最終判定 | 内容確認と描画結果のMDハッシュが現在のMDと一致し、必須確認が全て通過すること。 |

`Unsupported markdown`、`Syntax error`、`Parse error`等の文字列やエラー用図形が描画結果にある場合は、パーサーが通っていても不合格。未実行、依存ライブラリなし、ブラウザー起動不可はBLOCKED（検証不能）であり、PASSにしない。図を削除して検査を回避できないよう、期待図数を原資料の確認結果から指定する。

## 番号付きラベル

以下のようなラベルは、環境によってMarkdownリストとして解釈されるため避ける。

```text
A["1. 画面初期表示"]
```

番号と表示上のピリオド・空白を残す例：

```text
A["1#46; 画面初期表示"]
```

FO-006では、表示文字列が実際に「1. 画面初期表示」「2. 値入力時」になることも検証した。互換性修正は図のラベル表現だけとし、元の業務仕様や処理番号を変更しない。

Mermaidの対応範囲はバージョンで異なる。今回使用した11.12.2では通常の番号付きラベルを描画できたが、旧環境での問題を避ける互換性規則として元の2ラベルを不合格にした。「この実行環境でも必ず同じUnsupported markdownエラーを再現した」という意味ではない。

## 実行方法

PlaywrightとChromium、信頼できるバージョン固定のMermaidブラウザーバンドルを用意する。

```bash
python -m pip install -r requirements-render.txt
python -m playwright install chromium
python -m src.mermaid_validate output/spec.md \
  --bundle /path/to/mermaid.min.js --version 11.12.2 \
  --expected-count 3 --json /tmp/mermaid-check.json
```

ESM環境では、ローカルのモジュールを `--asset-map` で読み込める。JSON形式は `entry`、`version`、`modules`。modulesは相対ファイル名からJS本文への辞書で、相対importを `offline-assets/<相対名>` に解決済みとする。`tools/prepare_mermaid_assets.cjs` はこのマップを作成する補助処理であり、Mermaidのパーサーや描画アルゴリズムは変更しない。

```bash
npm install --no-save mermaid@11.12.2 typescript
node tools/prepare_mermaid_assets.cjs node_modules/mermaid/dist \
  mermaid.esm.min.mjs /tmp/mermaid-assets.json 11.12.2
python -m src.independent_evaluate output/spec.md \
  --acceptance-json /tmp/content-acceptance.json \
  --asset-map /tmp/mermaid-assets.json --expected-count 3 \
  --json /tmp/independent-evaluation.json
```

内容確認JSONは、独立に実施した出典・意味・値対応等の確認結果を渡す。`markdown_sha256` と、非空の `checks` 配列（各要素の `passed` は真偽値）が必要。変換器が自己申告した成功フラグをそのまま渡さない。MDを変更したら内容確認もやり直す。必要に応じて `--browser-path` と `--artifacts` を指定できる。

戻り値はPASSなら0、FAILなら1、実行環境等のBLOCKEDなら2。Mermaidだけの検証成功は業務仕様全体の正しさを保証しない。

## HTML画面

画面には外枠を付け、原画面と既存HTMLの部品順、グループ、列順、入力種別、値をなるべく維持する。Excelの幅2グリッドの再現や画面の独自再設計は行わない。

注記、吹き出しの本文、説明コメントは外枠の外へ置く。同じ画面章の中で、対象IDと可視注記の対応を維持する。入力欄や表の上に説明を重ねない。HTMLコメントだけに仕様を隠さず、可視の説明も残す。

ブラウザーで外枠、部品配置、値、注記が枠外にあることを確認する。表示側がstyle属性やformタグを制限する場合は表示差が残るため、別途提供する静的HTMLプレビューとMDソースを区別する。

## 報告する内容

Mermaid版、ブラウザー版、ランタイム指紋、検査したMDのSHA-256、図番号・開始行、構文・描画・互換性の個別結果、実施した変換ループ、未確認事項をreportに残す。描画するために意味を削除したり、原資料の情報を消してPASSにしない。

## 技術資料

- Mermaid API（parse/render）：https://mermaid.js.org/config/usage
- Mermaidのリスト表示問題の報告：https://github.com/mermaid-js/mermaid/issues/6099
- 数値エンティティによる互換性対処の記録：https://gitlab.com/gitlab-org/gitlab/-/issues/554889
