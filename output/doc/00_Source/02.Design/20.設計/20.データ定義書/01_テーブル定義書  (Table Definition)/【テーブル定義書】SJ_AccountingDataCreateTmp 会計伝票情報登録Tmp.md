# SJ_AccountingDataCreateTmp 会計伝票情報登録Tmp：テーブル定義書

<a id="table-definition"></a>
## 1. テーブル定義

### 1.1 文書情報・共通ヘッダー

| 項目 | 内容 |
| --- | --- |
| プロジェクト | 会計システム刷新プロジェクト（LIBRA） |
| 文書区分 | テーブル定義書 |
| 作成日 | 2026-06-19 |
| 作成者 | JBS山田 |
| 変更日 | 2026-06-19 |
| 変更者 | JBS山田 |

### 1.2 テーブル属性

| 属性 | 値 |
| --- | --- |
| テーブル名（論理） | 会計伝票情報登録Tmp |
| ラベルID | 原資料空欄 |
| テーブル名（物理） | SJ_AccountingDataCreateTmp |
| テーブルタイプ | TempDB |
| テーブル種別 | Miscellaneous |
| 開発区分 | アドオン |
| Save Data Per Company | Yes |

### 1.3 フィールド定義

原資料の列名・型・桁数・PK・必須指定を対応付けて記載する。`原資料空欄`は未記載を表し、`-`、`NO`、`YES`とは区別する。

| No. | 列名（論理） | ラベルID | 列名（物理） | 型 | 拡張データ型／列挙型 | 桁数 | PK | 必須 | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ファイル名 | SYS16423 | FileName | String | FileName | 原資料空欄 | NO | NO | Microsoft標準EDT |
| 2 | データ区分 | SJ00387 | DataClass | String | SJ_DataClass | 3 | NO | YES | 原資料空欄 |
| 3 | 会社 | SJ00029 | CompanyId | String | SJ_CompanyId | 4 | NO | YES | 原資料空欄 |
| 4 | 伝票キー | SJ00386 | VoucherKey | String | SJ_VoucherKey | 16 | NO | YES | 原資料空欄 |

テーブルタイプはTempDB、Save Data Per CompanyはYesという原記載を保持する。前のRegularテーブルの設定を流用しない。

FileNameの桁数は原資料空欄。データ区分・会社・伝票キーの必須YESを保持する。

<a id="other-definition"></a>
## 2. その他定義

### 2.1 フィールドグループ

原資料の可視範囲に定義行の記載はない。

### 2.2 インデックス

原資料の可視範囲に定義行の記載はない。

