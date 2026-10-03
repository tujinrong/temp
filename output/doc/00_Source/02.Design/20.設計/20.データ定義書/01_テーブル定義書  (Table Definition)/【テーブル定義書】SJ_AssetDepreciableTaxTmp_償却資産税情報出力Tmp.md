# SJ_AssetDepreciableTaxTmp 償却資産税情報出力Tmp：テーブル定義書

<a id="table-definition"></a>
## 1. テーブル定義

### 1.1 文書情報・共通ヘッダー

| 項目 | 内容 |
| --- | --- |
| プロジェクト | 会計システム刷新プロジェクト（LIBRA） |
| 文書区分 | テーブル定義書 |
| 作成日 | 2025-06-04 |
| 作成者 | JBS石岡 |
| 変更日 | 2025-06-04 |
| 変更者 | JBS石岡 |

### 1.2 テーブル属性

| 属性 | 値 |
| --- | --- |
| テーブル名（論理） | 償却資産税情報出力Tmp |
| ラベルID | - |
| テーブル名（物理） | SJ_AssetDepreciableTaxTmp |
| テーブルタイプ | TempDB |
| テーブル種別 | 原資料空欄 |
| 開発区分 | アドオン |

### 1.3 フィールド定義

原資料の列名・型・桁数・PK・必須指定を対応付けて記載する。`原資料空欄`は未記載を表し、`-`、`NO`、`YES`とは区別する。

| No. | 列名（論理） | ラベルID | 列名（物理） | 型 | 拡張データ型／列挙型 | 桁数 | PK | 必須 | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 増減区分 | - | IncOrDecCategory | Integer | - | - | NO | NO | 原資料空欄 |
| 2 | 固定資産番号 | - | AssetId | String | AssetId | 20 | NO | NO | 原資料空欄 |
| 3 | 固定資産名前 | - | AssetName | String | AssetName | 150 | NO | NO | 原資料空欄 |
| 4 | 主要タイプ | - | AssetType_JP | Enum | AssetType_JP | - | NO | NO | 原資料空欄 |
| 5 | 数量 | - | Quantity | Real | AssetQuantity | - | NO | NO | 原資料空欄 |
| 6 | 耐用年数 | - | ServiceLife | Real | AssetServiceLife | - | NO | NO | 原資料空欄 |
| 7 | 取得日付 | - | AcquisitionDate | Date | AssetAcquisitionDate | - | NO | NO | 原資料空欄 |
| 8 | 取得価額 | - | AcquisitionPrice | Real | AssetAcquisitionPrice | - | NO | NO | 原資料空欄 |
| 9 | 取得方法 | - | AcquisitionMethod | String | AssetAcquisitionMethodId | 20 | NO | NO | 原資料空欄 |
| 10 | 減価償却プロファイル | - | DepreciationProfile | String | - | 10 | NO | NO | 原資料空欄 |

テーブルタイプは`TempDB`。テーブル種別の空欄と、ラベルID・一部の拡張データ型／桁数の`-`は別の記載として保持する。

10項目すべてのPK・必須欄は`NO`。増減区分（IncOrDecCategory）の型は`Integer`であり、原資料にない区分コードや既定値は追加しない。

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

