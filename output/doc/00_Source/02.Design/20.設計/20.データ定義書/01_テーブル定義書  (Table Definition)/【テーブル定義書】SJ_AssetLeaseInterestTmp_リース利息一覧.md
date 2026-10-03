# SJ_AssetLeaseInterestTmp リース利息一覧：テーブル定義書

<a id="table-definition"></a>
## 1. テーブル定義

### 1.1 文書情報・共通ヘッダー

| 項目 | 内容 |
| --- | --- |
| プロジェクト | 会計システム刷新プロジェクト（LIBRA） |
| 文書区分 | テーブル定義書 |
| 作成日 | 2024-08-13 |
| 作成者 | JBS盧 |
| 変更日 | 2026-05-29 |
| 変更者 | JBS井田 |

### 1.2 テーブル属性

| 属性 | 値 |
| --- | --- |
| テーブル名（論理） | リース利息一覧 |
| ラベルID | 原資料空欄 |
| テーブル名（物理） | SJ_AssetLeaseInterestTmp |
| テーブルタイプ | Tmp |
| テーブル種別 | Miscellaneous |
| 開発区分 | アドオン |

### 1.3 フィールド定義

原資料の列名・型・桁数・PK・必須指定を対応付けて記載する。`原資料空欄`は未記載を表し、`-`、`NO`、`YES`とは区別する。

| No. | 列名（論理） | ラベルID | 列名（物理） | 型 | 拡張データ型／列挙型 | 桁数 | PK | 必須 | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | リースID | - | LeaseID | String | AssetLeaseLeaseId | 40 | YES | YES | 原資料空欄 |
| 2 | 帳簿タイプ | - | BookType | String | AssetLeaseBookType | 20 | YES | YES | 原資料空欄 |
| 3 | リースの説明 | - | LeaseDescription | String | AssetLeaseLeaseDescription | 60 | NO | NO | 原資料空欄 |
| 4 | リースグループ | - | LeaseGroup | String | AssetLeaseGroup | 10 | NO | NO | 原資料空欄 |
| 5 | 場所番号 | - | LocationNumber | String | AssetLeaseLocationNumber | 30 | NO | NO | 原資料空欄 |
| 6 | 日付 | - | LeaseDate | Date | AssetLeaseDate | 原資料空欄 | NO | NO | 原資料空欄 |
| 7 | 期間終了日 | - | EndDate | Date | AssetLeaseDate | 原資料空欄 | NO | NO | 原資料空欄 |
| 8 | リース開始日 | - | LeaseStartDate | Date | AssetLeaseLeaseStartDate | 原資料空欄 | NO | NO | 原資料空欄 |
| 9 | 期首日 | SJ00188 | LeaseFromDate | Date | SJ_LeaseFromDate | 原資料空欄 | NO | NO | 原資料空欄 |
| 10 | 期首残高 | - | BeginningBalance | Real | AssetLeaseBeginningBalance | 原資料空欄 | NO | NO | 原資料空欄 |
| 11 | 元本残高 | - | Subtotal | Real | AssetLeaseBeginningBalance | 原資料空欄 | NO | NO | 原資料空欄 |
| 12 | 期末日 | SJ00189 | LeaseToDate | Date | SJ_LeaseToDate | 原資料空欄 | NO | NO | 原資料空欄 |
| 13 | 期末残高 | - | EndingBalance | Real | AssetLeaseEndingBalance | 原資料空欄 | NO | NO | 原資料空欄 |
| 14 | 期間支払利息 | - | InterestExpense | Real | Amount | 原資料空欄 | NO | NO | 原資料空欄 |
| 15 | 利息累計額 | SJ05087 | AccumulatedInterest | Real | SJ_AccumulatedInterest | 原資料空欄 | NO | NO | 原資料空欄 |
| 16 | 定期支払タイプ | 原資料空欄 | AnnuityType | Enum | AssetLeaseAnnuityType | 原資料空欄 | NO | NO | 原資料空欄 |
| 17 | 作成者 | - | CreatedBy | String | CreatedBy | 20 | NO | NO | System項目　CreatedBy:Yes |
| 18 | 作成日時 | - | CreatedDateTime | UtcDateTime | CreatedDateTime | 原資料空欄 | NO | NO | System項目　CreatedDateTime:Yes |
| 19 | 更新者 | - | ModifiedBy | String | ModifiedBy | 20 | NO | NO | System項目　ModifiedBy:Yes |
| 20 | 更新日時 | - | ModifiedDateTime | UtcDateTime | ModifiedDateTime | 原資料空欄 | NO | NO | System項目　ModifiedDateTime:Yes |

`LeaseID`と`BookType`はPK・必須ともに`YES`。他の18項目はPK・必須ともに`NO`である。インデックスの指定は第2章に記載する。

`AnnuityType`は型`Enum`・拡張データ型／列挙型`AssetLeaseAnnuityType`と記載され、ラベルIDと桁数は原資料空欄。System項目4件のプロパティ指定を備考欄に保持する。

テーブルタイプは原記載の`Tmp`を保持する。未記載の桁数・精度や法人別保存設定を補完しない。

<a id="other-definition"></a>
## 2. その他定義

### 2.1 フィールドグループ

原資料の可視範囲に定義行の記載はない。

### 2.2 インデックス

| No. | インデックス名 | 重複許可 | フィールド | その他プロパティ |
| --- | --- | --- | --- | --- |
| 1 | SJ_LeaseIDIdx | Yes | LeaseID,BookType | 原資料空欄 |

関連する確認事項：[Q01 PK指定とインデックスの重複許可の関係](../../../../../../../qa/doc/00_Source/02.Design/20.%E8%A8%AD%E8%A8%88/20.%E3%83%87%E3%83%BC%E3%82%BF%E5%AE%9A%E7%BE%A9%E6%9B%B8/01_%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E5%AE%9A%E7%BE%A9%E6%9B%B8%20%20%28Table%20Definition%29/%E3%80%90%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB%E5%AE%9A%E7%BE%A9%E6%9B%B8%E3%80%91SJ_AssetLeaseInterestTmp_%E3%83%AA%E3%83%BC%E3%82%B9%E5%88%A9%E6%81%AF%E4%B8%80%E8%A6%A7.md#q01)。

### 2.3 リレーション

原資料の可視範囲に定義行の記載はない。

### 2.4 Deleteアクション

原資料の可視範囲に定義行の記載はない。

### 2.5 メソッド

原資料の可視範囲に定義行の記載はない。

