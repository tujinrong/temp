# SJ_AccountDebitAgreementLedger 口座引落契約台帳：テーブル定義書

<a id="table-definition"></a>
## 1. テーブル定義

### 1.1 文書情報・共通ヘッダー

| 項目 | 内容 |
| --- | --- |
| プロジェクト | 会計システム刷新プロジェクト（LIBRA） |
| 文書区分 | テーブル定義書 |
| 作成日 | 2024-06-06 |
| 作成者 | JBS　秋信 |
| 変更日 | 2024-10-15 |
| 変更者 | JBS　秋信 |

### 1.2 テーブル属性

| 属性 | 値 |
| --- | --- |
| テーブル名（論理） | 口座引落契約台帳 |
| ラベルID | SJ00202 |
| テーブル名（物理） | SJ_AccountDebitAgreementLedger |
| テーブルタイプ | Regular |
| テーブル種別 | 原資料空欄 |
| 開発区分 | アドオン |

### 1.3 フィールド定義

原資料の列名・型・桁数・PK・必須指定を対応付けて記載する。`原資料空欄`は未記載を表し、`-`、`NO`、`YES`とは区別する。

| No. | 列名（論理） | ラベルID | 列名（物理） | 型 | 拡張データ型／列挙型 | 桁数 | PK | 必須 | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 振替対象外 | SJ00203 | ExcludedTransfer | Enum | SJ_ExcludedTransfer | - | NO | NO | 原資料空欄 |
| 2 | 委託者番号 | SJ00204 | OutsourcingNumber | String | SJ_OutsourcingNumber | 10 | NO | NO | 原資料空欄 |
| 3 | 委託者名 | SJ00205 | OutsourcingName | String | SJ_OutsourcingName | 160 | NO | NO | 原資料空欄 |
| 4 | 摘要 | SJ00206 | Summary | String | SJ_Summary | 160 | NO | YES | 原資料空欄 |
| 5 | 需要家番号 | SJ00207 | ConsumerNumber | String | SJ_ConsumerNumber | 48 | NO | NO | 原資料空欄 |
| 6 | お客様番号 | SJ00208 | CustomerNumber | String | SJ_CustomerNumber | 255 | NO | NO | 原資料空欄 |
| 7 | 借方科目コード | SJ00209 | DebitAccountCode | String | SJ_DebitAccountCode | 20 | NO | YES | 原資料空欄 |
| 8 | 借方勘定細目 | SJ00706 | DebitAccountDetails | String | SJ_AccountDetails | 20 | NO | NO | 原資料空欄 |
| 9 | 借方原価センタ | SJ00210 | DebitCostCenter | String | SJ_DebitCostCenter | 30 | NO | NO | 原資料空欄 |
| 10 | 借方利益センタ | SJ00211 | DebitProfitCenter | String | SJ_DebitProfitCenter | 30 | NO | NO | 原資料空欄 |
| 11 | 貸方利益センタ | SJ00212 | CreditProfitCenter | String | SJ_CreditProfitCenter | 30 | NO | NO | 原資料空欄 |
| 12 | 消費税コード | - | TaxCode | String | TaxCode | 10 | NO | YES | 原資料空欄 |
| 13 | 備考 | SJ00213 | Comment | String | SJ_Comment | 255 | NO | NO | 原資料空欄 |
| 14 | 複数明細対象 | SJ00214 | MultipleLine | Enum | SJ_MultipleLine | - | NO | NO | 原資料空欄 |
| 15 | 金額(個別) | SJ00215 | IndividualAmout | Real | SJ_IndividualAmout | - | NO | NO | マイナス金額の入力は不可 |
| 16 | 指図コード | SJ00003 | OrderCode | String | SJ_OrderCode | 12 | NO | NO | 原資料空欄 |
| 17 | 借方チャネル | SJ00707 | DebitChannel | String | SJ_Channel | 10 | NO | NO | 原資料空欄 |
| 18 | 借方ブランド | SJ00708 | DebitBrand⇥⇥⇥⇥⇥⇥⇥⇥⇥ | String | SJ_BrandCode | 10 | NO | NO | 原資料空欄 |
| 19 | 借方カテゴリ | SJ00709 | DebitCategory⇥⇥⇥⇥⇥⇥⇥⇥⇥ | String | SJ_Category | 10 | NO | NO | 原資料空欄 |
| 20 | 契約番号(リース物件内容) | SJ00216 | AssetLeaseContractNumber | String | SJ_AssetLeaseContractNumber | 160 | NO | NO | 原資料空欄 |
| 21 | 区分(リース物件内容) | SJ00217 | AssetLeaseClassification | Enum | SJ_AssetLeaseClassification | - | NO | NO | 原資料空欄 |
| 22 | 開始年月日(リース物件内容) | SJ00218 | AssetLeaseStartDate | Date | SJ_AssetLeaseStartDate | - | NO | NO | 原資料空欄 |
| 23 | 総回数(リース物件内容) | SJ00219 | AssetLeaseTotalCount | Integer | SJ_AssetLeaseTotalCount | - | NO | NO | マイナスの入力は不可 |
| 24 | 総金額税込み(リース物件内容) | SJ00220 | AssetLeaseTotalAmountIncludingTax | Real | SJ_AssetLeaseTotalAmountIncludingTax | - | NO | NO | マイナスの入力は不可 |
| 25 | 作成者 | - | CreatedBy | String | CreatedBy | 20 | NO | NO | System項目　CreatedBy:Yes |
| 26 | 作成日時 | - | CreatedDateTime | UtcDateTime | CreatedDateTime | 原資料空欄 | NO | NO | System項目　CreatedDateTime:Yes |
| 27 | 更新者 | - | ModifiedBy | String | ModifiedBy | 20 | NO | NO | System項目　ModifiedBy:Yes |
| 28 | 更新日時 | - | ModifiedDateTime | UtcDateTime | ModifiedDateTime | 原資料空欄 | NO | NO | System項目　ModifiedDateTime:Yes |

金額(個別)・総回数(リース物件内容)・総金額税込み(リース物件内容)のマイナス入力禁止は、各項目の備考に保持する。`IndividualAmout`の綴りは原資料どおりとする。

CreatedBy・CreatedDateTime・ModifiedBy・ModifiedDateTimeのSystem項目設定は備考に保持する。PKの全行NOを、テーブル全体に主キーが存在しないという意味へ拡張しない。

物理名に保存されているタブ文字は、1文字ごとに「⇥」で表示する。この記号は正式な物理名へ追加する文字ではない。

関連する確認事項：[Q01 物理名末尾のタブ文字](../../../../../../../qa/doc/00_Source/02.Design/20.%E8%A8%AD%E8%A8%88/20.%E3%83%87%E3%83%BC%E3%82%BF%E5%AE%9A%E7%BE%A9%E6%9B%B8/01_%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E5%AE%9A%E7%BE%A9%E6%9B%B8%20%20%28Table%20Definition%29/%E3%80%90%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E5%AE%9A%E7%BE%A9%E6%9B%B8%E3%80%91SJ_AccountDebitAgreementLedger_%E5%8F%A3%E5%BA%A7%E5%BC%95%E8%90%BD%E5%A5%91%E7%B4%84%E5%8F%B0%E5%B8%B3.md#q01)。

<a id="other-definition"></a>
## 2. その他定義

### 2.1 フィールドグループ

原資料の可視範囲に定義行の記載はない。

### 2.2 インデックス

| No. | インデックス名 | 重複許可 | フィールド | その他プロパティ |
| --- | --- | --- | --- | --- |
| 1 | SJ_sortIdx | Yes | OutsourcingNumber | 原資料空欄 |
| 2 | SJ_sortIdx | Yes | ConsumerNumber | 原資料空欄 |

関連する確認事項：[Q02 同名インデックス2行の解釈](../../../../../../../qa/doc/00_Source/02.Design/20.%E8%A8%AD%E8%A8%88/20.%E3%83%87%E3%83%BC%E3%82%BF%E5%AE%9A%E7%BE%A9%E6%9B%B8/01_%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E5%AE%9A%E7%BE%A9%E6%9B%B8%20%20%28Table%20Definition%29/%E3%80%90%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E5%AE%9A%E7%BE%A9%E6%9B%B8%E3%80%91SJ_AccountDebitAgreementLedger_%E5%8F%A3%E5%BA%A7%E5%BC%95%E8%90%BD%E5%A5%91%E7%B4%84%E5%8F%B0%E5%B8%B3.md#q02)。

### 2.3 リレーション

| No. | リレーション名（テーブル名） | リレーションタイプ | 基数 | 関連テーブル基数 | リレーション内容 |
| --- | --- | --- | --- | --- | --- |
| 1 | MainAccount | NotSpecified | NotSpecified | NotSpecified | DebitAccountCode == MainAccountId |
| 2 | OMOperatingUnit | NotSpecified | NotSpecified | NotSpecified | DebitCostCenter == OMOperatingUnitNumber &amp;&amp; OMOperatingUnitType == OMOperatingUnitType::OMCostCenter |
| 3 | OMOperatingUnit | NotSpecified | NotSpecified | NotSpecified | DebitProfitCenter == OMOperatingUnitNumber &amp;&amp; OMOperatingUnitType == OMOperatingUnitType::OMDepartment |
| 4 | OMOperatingUnit | NotSpecified | NotSpecified | NotSpecified | CreditProfitCenter == OMOperatingUnitNumber &amp;&amp; OMOperatingUnitType == OMOperatingUnitType::OMDepartment |
| 5 | TaxData | NotSpecified | NotSpecified | NotSpecified | TaxCode == TaxCode |
| 6 | SJ_OrderTable | NotSpecified | NotSpecified | NotSpecified | OrderCode == OrderCode &amp;&amp; DeleteFlg == NoYes::No |

### 2.4 Deleteアクション

原資料の可視範囲に定義行の記載はない。

### 2.5 メソッド

原資料の可視範囲に定義行の記載はない。

