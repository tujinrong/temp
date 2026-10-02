# SJ_AccountDebitAgreementLedgerTmp 口座引落契約台帳Tmp：テーブル定義書

<a id="sheet-table"></a>
## 1. テーブル定義

### 1.1 文書情報

| 項目 | 内容 |
| --- | --- |
| プロジェクト名 | 会計システム刷新プロジェクト（LIBRA） |
| 区分 | テーブル定義書 |
| 作成日時 | 2024-08-16 |
| 作成者 | JBS　秋信 |
| 変更日時 | 2025-04-11 |
| 変更者 | JBS　秋信 |

### 1.2 テーブル属性

| 項目 | 内容 |
| --- | --- |
| テーブル名（論理） | 口座引落契約台帳Tmp |
| テーブルのラベルID | - |
| テーブル名（物理） | SJ_AccountDebitAgreementLedgerTmp |
| テーブルタイプ | Tmp |
| テーブル種別 | 原資料空欄 |
| 開発区分 | アドオン |

### 1.3 フィールド定義

| No. | 列名（論理） | ラベルID | 列名（物理） | 型 | 拡張データ型／列挙型 | 桁数 | PK | 必須 | 補足（原資料の右欄） |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 委託者番号 | SJ00204 | OutsourcingNumber | String | SJ_OutsourcingNumber | 10 | NO | NO | 原資料空欄 |
| 2 | 需要家番号 | SJ00207 | ConsumerNumber | String | SJ_ConsumerNumber | 48 | NO | NO | 原資料空欄 |
| 3 | 借方科目コード | SJ00209 | DebitAccountCode | String | SJ_DebitAccountCode | 20 | NO | NO | 原資料空欄 |
| 4 | 借方原価センタ | SJ00210 | DebitCostCenter | String | SJ_DebitCostCenter | 30 | NO | NO | 原資料空欄 |
| 5 | 借方利益センタ | SJ00211 | DebitProfitCenter | String | SJ_DebitProfitCenter | 30 | NO | NO | 原資料空欄 |
| 6 | 貸方利益センタ | SJ00212 | CreditProfitCenter | String | SJ_CreditProfitCenter | 30 | NO | NO | 原資料空欄 |
| 7 | 消費税コード | SYS21877 | TaxCode | String | TaxCode | 10 | NO | NO | 原資料空欄 |
| 8 | 備考 | SJ00213 | Comment | String | SJ_Comment | 255 | NO | NO | 原資料空欄 |
| 9 | 金額(個別) | SJ00215 | IndividualAmout | Real | SJ_IndividualAmout | - | NO | NO | マイナス金額の入力は不可 |
| 10 | 指図コード | SJ00003 | OrderCode | String | SJ_OrderCode | 12 | NO | NO | 原資料空欄 |
| 11 | 借方勘定細目 | SJ00706 | DebitAccountDetails | String | SJ_AccountDetails | 20 | NO | NO | 原資料空欄 |
| 12 | 借方チャネル | SJ00707 | DebitChannel | String | SJ_Channel | 10 | NO | NO | 原資料空欄 |
| 13 | 借方ブランド | SJ00708 | DebitBrand⇥⇥⇥⇥⇥⇥⇥⇥⇥ | String | SJ_BrandCode | 10 | NO | NO | 原資料空欄 |
| 14 | 借方カテゴリ | SJ00709 | DebitCategory⇥⇥⇥⇥⇥⇥⇥⇥⇥ | String | SJ_Category | 10 | NO | NO | 原資料空欄 |
| 15 | 区分(リース物件内容) | SJ00217 | AssetLeaseClassification | Enum | SJ_AssetLeaseClassificationEnum | - | NO | NO | 原資料空欄 |
| 16 | 開始年月日(リース物件内容) | SJ00218 | AssetLeaseStartDate | Date | SJ_AssetLeaseStartDate | - | NO | NO | 原資料空欄 |
| 17 | グループID | SJ00318 | GroupId | String | SJ_WithdrawalDataJournalGroupId | 20 | NO | NO | 原資料空欄 |

全17項目のPKと必須は、原資料でいずれもNOと指定されている。これをテーブル全体の主キー不存在と解釈せず、未記載の初期値は追加しない。

金額(個別)は原資料の指定によりマイナス金額の入力不可。物理名IndividualAmoutと拡張データ型SJ_IndividualAmoutの綴り、テーブルタイプTmpは原表記のまま保持する。

借方ブランドと借方カテゴリの物理名末尾には、それぞれタブ文字（U+0009）が9文字含まれる。表中の「⇥」はタブ1文字の可視化記号であり、正式名称として追加した文字ではない。

末尾タブを含む2つの物理名の扱いは[Q01](../../../../../../../qa/doc/00_Source/02.Design/20.設計/20.データ定義書/01_テーブル定義書%20%20%28Table%20Definition%29/【テーブル定義書】SJ_AccountDebitAgreementLedgerTmp_口座引落契約台帳Tmp.md#q01)を参照する。

<a id="sheet-other"></a>
## 2. その他定義

### 2.1 フィールドグループ

定義行は原資料未記載。不要または存在しないという指定ではない。

### 2.2 インデックス

定義行は原資料未記載。不要または存在しないという指定ではない。

### 2.3 リレーション

定義行は原資料未記載。不要または存在しないという指定ではない。

### 2.4 Deleteアクション

定義行は原資料未記載。不要または存在しないという指定ではない。

### 2.5 メソッド

定義行は原資料未記載。不要または存在しないという指定ではない。
