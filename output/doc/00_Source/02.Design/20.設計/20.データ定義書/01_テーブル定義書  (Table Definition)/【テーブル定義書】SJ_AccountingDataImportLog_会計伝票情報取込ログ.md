# SJ_AccountingDataImportLog 会計伝票情報取込ログ：テーブル定義書

<a id="table-definition"></a>
## 1. テーブル定義

### 1.1 文書情報・共通ヘッダー

| 項目 | 内容 |
| --- | --- |
| プロジェクト | 会計システム刷新プロジェクト（LIBRA） |
| 文書区分 | テーブル定義書 |
| 作成日 | 2024-08-27 |
| 作成者 | JBS加藤 |
| 変更日 | 2025-11-17 |
| 変更者 | JBS井田 |

### 1.2 テーブル属性

| 属性 | 値 |
| --- | --- |
| テーブル名（論理） | 会計伝票情報取込ログ |
| ラベルID | SJ00500 |
| テーブル名（物理） | SJ_AccountingDataImportLog |
| テーブルタイプ | Regular |
| テーブル種別 | Transaction |
| 開発区分 | アドオン |
| Save Data Per Company | No |

### 1.3 フィールド定義

原資料の列名・型・桁数・PK・必須指定を対応付けて記載する。`原資料空欄`は未記載を表し、`-`、`NO`、`YES`とは区別する。

| No. | 列名（論理） | ラベルID | 列名（物理） | 型 | 拡張データ型／列挙型 | 桁数 | PK | 必須 | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 会社コード | SJ00734 | CompanyId | String | SJ_CompanyId | 4 | NO | YES | ※RecIDをPKとする |
| 2 | データ区分 | SJ00387 | DataClass | String | SJ_DataClass | 3 | NO | YES | 原資料空欄 |
| 3 | 伝票キー | SJ00386 | VoucherKey | String | SJ_VoucherKey | 16 | NO | YES | 原資料空欄 |
| 4 | 明細番号 | SJ00258 | RowNum | String | SJ_rowNumber | 3 | NO | YES | 原資料空欄 |
| 5 | 伝票タイプ | SJ00256 | DocumentNumber | String | SJ_DocumentNumber | 2 | NO | NO | 原資料空欄 |
| 6 | 仕訳帳ヘッダテキスト | SJ00384 | HeaderText | String | SJ_HeaderText | 25 | NO | NO | 原資料空欄 |
| 7 | 転記日付 | SJ00340 | PostingDate | Date | SJ_PostingDate | 原資料空欄 | NO | YES | 原資料空欄 |
| 8 | 税額計算 | SJ00378 | TaxCalculation | Enum | SJ_TaxCalculation | 原資料空欄 | NO | NO | 0：外税計算, 1：内税計算 |
| 9 | 伝票日付 | SJ00255 | VoucherDate | Date | SJ_VoucherDate | 原資料空欄 | NO | YES | 原資料空欄 |
| 10 | 勘定タイプ | SJ00377 | AccountType | Enum | SJ_AccountType | 原資料空欄 | NO | YES | 原資料空欄 |
| 11 | 勘定 | SJ00653 | AccountID | String | SJ_AccountID | 20 | NO | NO | 原資料空欄 |
| 12 | 勘定細目 | SJ00401 | AccountDetails | String | SJ_AccountDetails | 20 | NO | NO | 原資料空欄 |
| 13 | 明細テキスト | SJ00385 | DetailsText | String | SJ_DetailsText | 50 | NO | NO | 原資料空欄 |
| 14 | 貸方金額 | SJ00241 | CreditAmount | Real | SJ_CreditAmount | 原資料空欄 | NO | NO | 原資料空欄 |
| 15 | 借方金額 | SJ00240 | DebitAmount | Real | SJ_DebitAmount | 原資料空欄 | NO | NO | 原資料空欄 |
| 16 | 税額 | SJ00382 | TaxAmount | Real | SJ_TaxAmount | 原資料空欄 | NO | NO | 原資料空欄 |
| 17 | 通貨 | SJ00630 | CurrencyCode | String | CurrencyCode | 3 | NO | NO | 原資料空欄 |
| 18 | 為替レート | SJ05078 | ExchRate | Real | ExchRate | 原資料空欄 | NO | NO | 小数点以下12桁 |
| 19 | 税コード | SJ05061 | TaxCode | String | SJ_TaxCode | 2 | NO | NO | 原資料空欄 |
| 20 | 利益センタ | SJ00262 | Department | String | SJ_Department | 10 | NO | NO | 原資料空欄 |
| 21 | 原価センタ | SJ00381 | CostCenter | String | SJ_CostCenter | 10 | NO | NO | 原資料空欄 |
| 22 | チャネル | SJ00263 | Channel | String | SJ_Channel | 10 | NO | NO | 原資料空欄 |
| 23 | ブランド | SJ00264 | BrandCode | String | SJ_BrandCode | 10 | NO | NO | 原資料空欄 |
| 24 | カテゴリー | SJ00265 | Category | String | SJ_Category | 10 | NO | NO | 原資料空欄 |
| 25 | 指図コード | SJ00003 | OrderCode | String | SJ_OrderCode | 12 | NO | NO | 原資料空欄 |
| 26 | 品番 | SJ00498 | ItemNumber | String | SJ_ItemNumber | 20 | NO | NO | 原資料空欄 |
| 27 | 参照伝票番号 | SJ00257 | RefVoucher | String | SJ_RefVoucher | 16 | NO | NO | 原資料空欄 |
| 28 | 社内稟議書番号 | SJ00374 | ApprovalDocumentNumber | String | SJ_ApprovalDocumentNumber | 20 | NO | NO | 原資料空欄 |
| 29 | 得意先コード | SJ00373 | CustNumber | String | SJ_CustNumber | 20 | NO | NO | 原資料空欄 |
| 30 | 転記プロファイル | SJ05637 | PostingProfile | String | PostingProfile | 10 | NO | NO | 原資料空欄 |
| 31 | 請求書 | SJ05638 | InvoiceId | String | InvoiceId | 50 | NO | NO | 原資料空欄 |
| 32 | 支払方法 | SJ00641 | PaymMode | String | SJ_PaymMode | 10 | NO | NO | 原資料空欄 |
| 33 | 支払基準日 | SJ00001 | PaymBaseDate | Date | SJ_PaymBaseDate | 原資料空欄 | NO | NO | 原資料空欄 |
| 34 | 請求書支払リリース日 | SJ05639 | InvoiceReleaseDate | UtcDateTime | InvoiceReleaseDate | 原資料空欄 | NO | NO | 原資料空欄 |
| 35 | 請求日付 | SJ05640 | InvoiceDate | UtcDateTime | InvoiceDate | 原資料空欄 | NO | NO | 原資料空欄 |
| 36 | ファイル名 | SJ00030 | FileName | String | FileName | 259 | NO | NO | 原資料空欄 |
| 37 | 行番号 | SJ00297 | LineNum | Integer | SJ_LineNum | 原資料空欄 | NO | NO | 原資料空欄 |
| 38 | 処理ステータス | SJ00028 | ProcessStatus | Enum | SJ_ProcessStatus | 原資料空欄 | NO | NO | 0:(None), 1:正常終了(Success), 2:異常終了(Error), 3:作成済(Created), 4:転記処理中(Posting), 5:削除対象(Deleting), 6:処理中(Processing), 7:作成中(Creating) |
| 39 | 伝票番号 | SJ00254 | Voucher | String | SJ_Voucher | 10 | NO | NO | 原資料空欄 |
| 40 | ログ | SJ00194 | Log | String | SJ_Log | 原資料空欄 | NO | NO | 原資料空欄 |
| 41 | 作成者 | - | createdBy | String | CreatedBy | 20 | NO | NO | system項目　CreatedBy:Yes |
| 42 | 作成日時 | - | createdDateTime | UtcDateTim | CreatedDateTime | 原資料空欄 | NO | NO | system項目　CreatedDateTime:Yes |
| 43 | 更新者 | - | modifiedBy | String | ModifiedBy | 20 | NO | NO | system項目　ModifiedBy:Yes |
| 44 | 変更日時 | - | modifiedDateTime | UtcDateTim | ModifiedDateTime | 原資料空欄 | NO | NO | system項目　ModifiedDateTime:Yes |

本表の原価センタ（CostCenter）と伝票番号（Voucher）の桁数はともに10。請求日付（InvoiceDate）の型は`UtcDateTime`。各値はこの原資料のまま保持する。

システム日時項目No.42・44の型`UtcDateTim`と各プロパティ指定は、自動補正せず保持する。

関連する確認事項：[Q01 システム日時項目の型名](../../../../../../../qa/doc/00_Source/02.Design/20.%E8%A8%AD%E8%A8%88/20.%E3%83%87%E3%83%BC%E3%82%BF%E5%AE%9A%E7%BE%A9%E6%9B%B8/01_%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E5%AE%9A%E7%BE%A9%E6%9B%B8%20%20%28Table%20Definition%29/%E3%80%90%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E5%AE%9A%E7%BE%A9%E6%9B%B8%E3%80%91SJ_AccountingDataImportLog_%E4%BC%9A%E8%A8%88%E4%BC%9D%E7%A5%A8%E6%83%85%E5%A0%B1%E5%8F%96%E8%BE%BC%E3%83%AD%E3%82%B0.md#q01)。

<a id="other-definition"></a>
## 2. その他定義

### 2.1 フィールドグループ

原資料の可視範囲に定義行の記載はない。

### 2.2 インデックス

原資料の可視範囲に定義行の記載はない。

### 2.3 リレーション

原資料の可視範囲に定義行の記載はない。

### 2.4 Deleteアクション

原資料の可視範囲に定義行の記載はない。

### 2.5 メソッド

原資料の可視範囲に定義行の記載はない。

