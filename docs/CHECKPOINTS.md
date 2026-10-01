# チェックポイントと途中再開

## 保存単位

`checkpoint/<機能ID>-<入力SHA256先頭12桁>/<工程>-<試行>/` に、`state.json` と中間成果物を保存する。必ず保存済みの可視範囲だけを含める。取得全体、スコープ抽出、シート断片、本文/QA候補、独立評価の各工程で段階保存する。工程単位の入力・ルール・処理コード・描画ライブラリの指紋を記録する。

`src/checkpoint.py` の save はZIP方式、save_filesは通常ファイル方式。同じ工程ディレクトリを上書きしない。GitHubに保存する際は全ファイルを1つのmainコミットに含め、コミットのref反映と読み戻しを確認する。ローカル保存、blob作成、tree作成だけをGitHub保存完了と報告しない。

## 再開

1. 最新の入力・ルール・工程コードから依存ハッシュを再計算する。state.jsonの値を無条件に信頼して流用しない。
2. state.jsonとZIPまたは通常ファイルを取得し、verifyで依存と全成果物ハッシュを照合する。
3. restoreで別作業ディレクトリへ復元する。異なる既存ファイル、ディレクトリ外へのパス、シンボリックリンクを拒否する。
4. next_actionから再開する。依存が変わった工程だけ無効化する。変換が同じでも評価器やMermaid実行環境が変わったときは評価をやり直す。
5. 評価FAILをPASSとして引き継がない。再開で以前の不合格候補を変更した場合は新しい試行として記録する。

```bash
python -m src.checkpoint verify checkpoint/FO-014-<hash>/candidate-02 --dependencies current-dependencies.json
python -m src.checkpoint restore checkpoint/FO-014-<hash>/candidate-02 --dependencies current-dependencies.json --destination restored
```

GitHubへの保存・取得は連携ツールまたは認証済みGitで行う。モジュール自体はネットワーク接続やブランチ変更を行わない。

## 完了後の削除

最終output/qa/reportをmainに保存し、再取得内容のハッシュを照合した後に、その文書の中間成果物だけを削除してよい。cleanupは呼出側が実際に検証したmainコミットと各最終ファイルハッシュのreceiptを必須とする。receiptは自動的にGitHubの正しさを保証する署名ではないため、通信層が検証する。

本文やQAに未回答の業務事項があっても、変換と納品が合格すれば中間ファイル削除は可能。変換未完了、評価BLOCKED、GitHub保存失敗の間は中間結果を残す。入力・確定成果物・他機能・既存回答は削除しない。通常の削除コミットはGit履歴を消去しない。
