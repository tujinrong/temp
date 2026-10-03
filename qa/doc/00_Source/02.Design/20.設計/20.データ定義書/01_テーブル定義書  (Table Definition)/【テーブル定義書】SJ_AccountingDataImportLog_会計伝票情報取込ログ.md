# SJ_AccountingDataImportLog 会計伝票情報取込ログ：質問・確認事項

[本文](../../../../../../../output/doc/00_Source/02.Design/20.%E8%A8%AD%E8%A8%88/20.%E3%83%87%E3%83%BC%E3%82%BF%E5%AE%9A%E7%BE%A9%E6%9B%B8/01_%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E5%AE%9A%E7%BE%A9%E6%9B%B8%20%20%28Table%20Definition%29/%E3%80%90%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E5%AE%9A%E7%BE%A9%E6%9B%B8%E3%80%91SJ_AccountingDataImportLog_%E4%BC%9A%E8%A8%88%E4%BC%9D%E7%A5%A8%E6%83%85%E5%A0%B1%E5%8F%96%E8%BE%BC%E3%83%AD%E3%82%B0.md) ／ [結果報告](../../../../../../../report/doc/00_Source/02.Design/20.%E8%A8%AD%E8%A8%88/20.%E3%83%87%E3%83%BC%E3%82%BF%E5%AE%9A%E7%BE%A9%E6%9B%B8/01_%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E5%AE%9A%E7%BE%A9%E6%9B%B8%20%20%28Table%20Definition%29/%E3%80%90%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E5%AE%9A%E7%BE%A9%E6%9B%B8%E3%80%91SJ_AccountingDataImportLog_%E4%BC%9A%E8%A8%88%E4%BC%9D%E7%A5%A8%E6%83%85%E5%A0%B1%E5%8F%96%E8%BE%BC%E3%83%AD%E3%82%B0.md)

以下は当該ファイルの記載を確認するための未回答質問である。選択肢は未承認の候補であり、本文の確定仕様として採用しない。原則単一選択。項目別の回答表は各行で選択する。

## 1. テーブル定義

<a id="q01"></a>
### Q01 システム日時項目の型名

**出典**：テーブル定義：No.42 createdDateTime、No.44 modifiedDateTime

**背景**：両項目の型はUtcDateTimと記載される。No.34のInvoiceReleaseDateとNo.35のInvoiceDateではUtcDateTimeと記載される。型名を統一せず、本文は原表記を保持している。

**質問**：2項目の正式な型名を、それぞれ選択してください。

| 選択肢 | 回答内容 |
| --- | --- |
| A | UtcDateTimeとする。 |
| B | UtcDateTimのままとする（この表記の意味を補足）。 |
| C | その他（正式な型名を補足）。 |
| D | 未定・要調査。 |

| 対象 | 回答 | 補足 |
| --- | --- | --- |
| No.42 createdDateTime | 未回答 |  |
| No.44 modifiedDateTime | 未回答 |  |

**回答者**：

**回答日**：

**補足**：

