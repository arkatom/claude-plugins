---
name: testcase-generator
description: "QC/QA向けE2Eテストケース自動生成。docs/specs/とコードから網羅的に抽出、Markdown/Excel/JSON出力。リスクベース優先順位付け、Gherkin対応。"
---

# テストケース生成Skill

QC/QA向けの高品質なE2Eテストケースを自動生成します。

## 重要な原則

### 完全汎用化（プロジェクト非依存）

**絶対に避けること**:

- 特定のテーブル名、エンドポイント数、フレームワーク名をハードコード
- プロジェクト固有の情報を前提とした処理

**正しいアプローチ**:

- docs/specs/ から動的に発見
- コードベースから動的に抽出
- 技術スタックを自動判定

### 段階的アプローチ

**4フェーズワークフロー**:

```
UNDERSTAND → EXTRACT → REVIEW → GENERATE
    ↓          ↓         ↓         ↓
  対象理解    観点抽出   優先順位   TC生成
```

各フェーズでユーザー承認を求める（`--no-verify` オプションでスキップ可能）。

---

## 実行フロー

### Step 0: 初期化

**引数とオプションの解析**:

```
使用方法:
/testcase-generator <対象> [オプション]

オプション:
--format=md|excel|json  # 出力形式（デフォルト: excel + json）
--priority=critical|high|medium|low  # 優先度フィルタ
--no-verify  # ユーザー承認をスキップ
--dry-run  # 生成せず、概要のみ表示
-v, --verbose  # 詳細ログ
```

**引数がない場合**:

```
AskUserQuestion で対象を質問:
「どの画面または機能のテストケースを作成しますか？

例:
- 問い合わせフォーム
- ログイン画面
- すべて（全機能）
- （具体的な画面名・機能名）」
```

**Todoリスト作成**:

```
TodoWrite:
- Phase 1: UNDERSTAND - 対象理解
- Phase 2: EXTRACT - テスト観点抽出
- Phase 3: REVIEW - リスク評価と優先順位付け
- Phase 4: GENERATE - テストケース生成（Excel + JSON + Markdown）
```

**出力ディレクトリ作成**:

```bash
mkdir -p docs/_testcases/{testcases,exports,reports,_context}
```

---

### Step 1: UNDERSTAND（対象理解）

**目的**: ユーザー指定の対象を理解し、テスト対象を明確化する。

**処理**:

1. **docs/specs/ の存在確認**:

   ```bash
   if [ ! -d "docs/specs" ]; then
     echo "❌ docs/specs/ が見つかりません。"
     echo "📝 /mkdocs でドキュメントを生成してください。"
     exit 1
   fi
   ```

2. **対象検索（動的）**:

   ```
   mcp__serena__search_for_pattern(
     substring_pattern="<ユーザー指定の対象>",
     relative_path="docs/specs",
     context_lines_before=3,
     context_lines_after=3
   )
   ```

3. **該当ドキュメント特定**:

   - `docs/specs/routes/overview.md` または `routes/*.md`
   - `docs/specs/app/controllers/*.md`
   - `docs/specs/resources/views/*.md`
   - 該当する詳細ドキュメント

4. **対象の構造化**:

   ```json
   {
     "target": "<ユーザー指定>",
     "endpoints": [],
     "controllers": [],
     "views": [],
     "validations": [],
     "business_logic": []
   }
   ```

5. **ユーザー確認**（`--no-verify` がない場合のみ）:

   ```
   対象理解結果:

   - エンドポイント: X件
   - 画面: Y件
   - バリデーションルール: Z件
   - ビジネスロジック: W件

   この理解で正しいですか？
   (Y: 承認 / N: 中止 / 修正指示を入力)
   ```

6. **understand.json 保存**:

   ```bash
   Write: docs/_testcases/_context/understand.json
   ```

---

### Step 2: EXTRACT（テスト観点抽出）

**目的**: テストすべき観点を網羅的に抽出する。

**処理**:

1. **エンドポイント抽出**（動的）:

   ```bash
   # docs/specs/routes/ から全エンドポイントを抽出
   grep -E "^\| .* \| .* \|" docs/specs/routes/overview.md || \
   find docs/specs/routes -name "*.md" -exec grep -h "Route::" {} \;
   ```

2. **バリデーション抽出**（動的）:

   ```
   mcp__serena__search_for_pattern(
     substring_pattern="required|email|max|min|regex|numeric|date",
     relative_path="docs/specs/app/requests",
     paths_include_glob="*.md"
   )
   ```

3. **UIパーツ抽出**（動的）:

   ```
   mcp__serena__search_for_pattern(
     substring_pattern="<input|<button|<select|<textarea",
     relative_path="docs/specs/resources/views"
   )
   ```

4. **ビジネスロジック抽出**（動的）:

   ```
   mcp__serena__search_for_pattern(
     substring_pattern="Auth::|Mail::|DB::|Storage::",
     relative_path="docs/specs/app/controllers"
   )
   ```

5. **テスト観点の分類**:

   **正常系**:
   - エンドポイントごとに最低1件
   - 主要な業務フロー

   **異常系**:
   - バリデーションルールごとに1件
   - 権限エラー、認証エラー

   **境界値**:
   - max/min制約ごとに1件
   - 文字数制限の境界

   **セキュリティ**:
   - CSRF、XSS、SQL Injection
   - 認証・認可の検証

6. **ユーザー確認**（`--no-verify` がない場合のみ）:

   ```
   抽出されたテスト観点（合計: XX件）:

   - 正常系: X件
   - 異常系: Y件
   - 境界値: Z件
   - セキュリティ: W件

   追加・削除したい観点はありますか？
   (承認 / 追加指示 / 削除指示)
   ```

7. **extract.json 保存**:

   ```bash
   Write: docs/_testcases/_context/extract.json
   ```

---

### Step 3: REVIEW（リスク評価と優先順位付け）

**目的**: 各テスト観点にリスクスコアを付与し、優先順位を決定する。

**処理**:

1. **リスクスコア計算**:

   ```bash
   cat docs/_testcases/_context/extract.json | \
     python3 "${CLAUDE_PLUGIN_ROOT}/skills/testcase-generator/scripts/calculate_risk.py" > \
     docs/_testcases/_context/review.json
   ```

   **計算式**（汎用的）:

   ```
   risk_score = business_impact (1-5) ×
                user_visibility (1-3) ×
                technical_complexity (1-3)
   ```

2. **優先度ラベル付与**:
   - Critical: スコア 20以上
   - High: スコア 10-19
   - Medium: スコア 5-9
   - Low: スコア 4以下

3. **優先順位ソート**:

   ```python
   sorted(testcases, key=lambda x: x['risk_score'], reverse=True)
   ```

4. **ユーザー確認**（`--no-verify` がない場合のみ）:

   ```
   リスク評価結果（上位10件）:

   1. [Critical, 30] <機能名> - 正常系
   2. [Critical, 28] <機能名> - セキュリティ
   3. [High, 15] <機能名> - 異常系
   ...

   この優先順位で問題ありませんか？
   (承認 / スコア調整指示)
   ```

5. **review.json 更新**:

   ```bash
   Write: docs/_testcases/_context/review.json
   ```

---

### Step 4: GENERATE（テストケース生成）

**目的**: 承認されたテスト観点から、3形式のテストケースを生成する。

**処理**:

1. **Markdown生成**（`--format=md` または デフォルト）:

   ```bash
   # assets/testcase.md.template を使用
   # 各テスト観点について1ファイル生成

   for tc in review.json['testcases']:
     output="docs/_testcases/testcases/${tc.feature}/TC_${tc.id}.md"
     # テンプレート置換で生成
   done
   ```

2. **Excel生成**（`--format=excel` または デフォルト）:

   ```bash
   cat docs/_testcases/_context/review.json | \
     python3 .claude/skills/testcase-generator/scripts/generate_excel.py \
     docs/_testcases/exports/$(date +%Y%m%d_%H%M%S)_testcases.xlsx
   ```

   **特徴**:
   - 画面・機能ごとにシートを分割
   - 優先度で行を色分け（Critical=赤、High=オレンジ、Medium=黄、Low=緑）
   - ヘッダー行を固定（スクロール時も表示）
   - フィルター機能を有効化
   - 列幅を自動調整
   - サマリーシート付き

3. **JSON生成**（`--format=json` または デフォルト）:

   ```bash
   cp docs/_testcases/_context/review.json \
     docs/_testcases/exports/$(date +%Y%m%d_%H%M%S)_testcases.json
   ```

4. **目次生成**:

   ```markdown
   # docs/_testcases/testcases/index.md

   # テストケース目次

   生成日時: YYYY-MM-DD HH:MM:SS
   対象: <ユーザー指定>
   総テストケース数: XX件

   ## 優先度別

   ### Critical（XX件）
   - [TC_XXX_001](xxx/TC_XXX_001.md) - <説明>

   ## 機能別

   ### <機能名>（XX件）
   - [TC_XXX_001](xxx/TC_XXX_001.md) - <説明>
   ```

5. **サマリーレポート生成**:

   ```markdown
   # docs/_testcases/reports/<timestamp>_generation_report.md

   # テストケース生成レポート

   生成日時: YYYY-MM-DD HH:MM:SS
   対象: <ユーザー指定>
   オプション: <使用されたオプション>

   ## 統計

   - 総テストケース数: XX件
   - 優先度別:
     - Critical: XX件
     - High: XX件
     - Medium: XX件
     - Low: XX件
   - カテゴリ別:
     - 正常系: XX件
     - 異常系: XX件
     - 境界値: XX件
     - セキュリティ: XX件

   ## 生成ファイル

   - Markdown: XX件（docs/_testcases/testcases/）
   - Excel: 1ファイル（docs/_testcases/exports/*.xlsx）
   - JSON: 1ファイル（docs/_testcases/exports/*.json）

   ## 次のステップ

   1. docs/_testcases/testcases/index.md で全体を確認
   2. docs/_testcases/exports/*.xlsx をExcelで開く（日本語対応、色分け、フィルター付き）
   3. docs/_testcases/exports/*.json を自動化ツールにインポート
   ```

---

### Step 5: 完了報告

```
✅ テストケース生成完了

生成結果:
- Markdownテストケース: XX件
- Excel: 1ファイル（.xlsx形式、日本語対応）
- JSON: 1ファイル
- 目次: 1ファイル
- レポート: 1ファイル

出力先:
- docs/_testcases/testcases/
- docs/_testcases/exports/
- docs/_testcases/reports/

次のステップ:
1. docs/_testcases/testcases/index.md で全テストケースを確認
2. docs/_testcases/exports/*.xlsx をExcelで開く（優先度別に色分け済み）
3. Critical優先度のテストケースから実行開始
```

---

## オプション詳細

### --no-verify

各フェーズでのユーザー承認をスキップします。

**使用例**:

```bash
/testcase-generator "すべて" --no-verify
```

**動作**:

- UNDERSTAND フェーズ: 自動承認
- EXTRACT フェーズ: 自動承認
- REVIEW フェーズ: 自動承認
- GENERATE フェーズ: 実行（Excel + JSON + Markdown を生成）

**推奨される使用場面**:

- 既にテスト対象が明確な場合
- 過去に同じ対象で生成済みで、再生成する場合
- 信頼できるdocs/specs/が存在する場合

**注意**:

- 誤った対象でテストケースが生成される可能性
- 不要なテスト観点が含まれる可能性
- 初回実行時は `--no-verify` を使用しないことを推奨

---

## 品質保証

### 網羅性の確保

**自動カウント検証**（完了時に実行）:

```bash
# エンドポイント数検証
endpoint_count=$(grep -c "Route::" docs/specs/routes/*.md 2>/dev/null || echo 0)
testcase_endpoint_count=$(jq '[.testcases[] | select(.type=="endpoint")] | length' docs/_testcases/exports/*.json)

if [ "$endpoint_count" -eq "$testcase_endpoint_count" ]; then
  echo "✅ 全エンドポイントがカバーされています"
else
  echo "⚠️  カバー率: $testcase_endpoint_count / $endpoint_count"
fi
```

### トレーサビリティ

各テストケースには以下のメタデータを含める:

- **エンドポイント**: 該当するルート
- **コントローラー**: 該当するコントローラーファイル
- **バリデーション**: 該当するバリデーションルール
- **仕様書**: docs/specs/ 内の該当ドキュメント

---

## 出力形式

### Markdown形式

詳細は `assets/testcase.md.template` を参照。

**含まれる情報**:

- テストケースID、説明、優先度、リスクスコア
- 前提条件
- テストステップ（表形式）
- テストデータ
- Gherkin形式シナリオ
- リスク評価詳細
- 関連情報（トレーサビリティ）

### Excel形式（推奨・デフォルト）

**出力ファイル**: `.xlsx`形式（Microsoft Excel 2007以降）

**フォーマット**: **1ステップ=1行**（実務標準）

1つのテストケースに複数のステップがある場合、各ステップを1行ずつ記載します。
これにより、どのステップで失敗したかを明確に記録できます。

**特徴**:

- **1テストケース × Nステップ = N行**: テストケースIDを繰り返し、各ステップを1行で記載
- 画面・機能ごとにシートを分割
- 優先度で行を色分け:
  - Critical: 赤（#FFCCCC）
  - High: オレンジ（#FFCC99）
  - Medium: 黄（#FFFFCC）
  - Low: 緑（#CCFFCC）
- ヘッダー行を固定（スクロール時も表示）
- フィルター機能を有効化（ドロップダウンで絞り込み可能）
- 列幅を自動調整（内容に応じて最適化）
- サマリーシート付き（優先度別統計、結果コード説明）

**列定義**:

```
テストケースID | ステップ番号 | 優先度 | リスクスコア | カテゴリ | サブカテゴリ |
タイトル | 前提 | 操作 | 期待挙動 | 結果 | 実施日 | 実施者 | 備考
```

**データの繰り返しルール**:

- **繰り返す**: テストケースID、優先度、リスクスコア、カテゴリ、サブカテゴリ、タイトル
- **最初のステップのみ**: 前提条件（2ステップ目以降は「-」）
- **各ステップごと**: ステップ番号、操作、期待挙動
- **テスト実施後に記入**: 結果（OK/NG/PN/NA）、実施日、実施者、備考

**結果コード**:

- **OK**: 合格
- **NG**: 不合格
- **PN**: Pending（未実施・保留）
- **NA**: Not Applicable（該当なし・スキップ）

**依存関係**:

```bash
pip install openpyxl
```

### CSV形式

**出力ファイル**: `.csv`形式（UTF-8 BOM付き）

**フォーマット**: **1ステップ=1行**（Excel形式と同じ）

**特徴**:

- UTF-8 BOM付き（Excelで開いても文字化けしない）
- QAツールへのインポート対応

**列定義**: Excel形式と同じ

### JSON形式

**出力ファイル**: `.json`形式

**構造**:

```json
{
  "meta": {
    "generated_at": "ISO 8601",
    "target": "ユーザー指定",
    "total_testcases": 0,
    "by_priority": {
      "Critical": 0,
      "High": 0,
      "Medium": 0,
      "Low": 0
    }
  },
  "testcases": [
    {
      "id": "TC_XXX_001",
      "priority": "Critical",
      "risk_score": 45,
      "category": "正常系",
      "subcategory": "基本フロー",
      "title": "...",
      "description": "...",
      "steps": ["操作1", "操作2", ...],
      "expected_results": ["期待1", "期待2", ...],
      "business_impact": 5,
      "user_visibility": 3,
      "technical_complexity": 3
    }
  ]
}
```

**用途**: 自動化ツール（TestRail、Jira/Xray等）へのインポート

---

## エラーハンドリング

| エラー | 対応 |
|-------|------|
| docs/specs/ が存在しない | `/mkdocs` の実行を提案して終了 |
| 対象が見つからない | 類似キーワードを提案、再入力を促す |
| バリデーションルールが抽出できない | 警告を表示し、正常系のみ生成 |
| スクリプト実行エラー | エラー内容を表示し、手動生成を提案 |

---

## 参照

詳細なガイドは `references/` を参照:

- `testcase-best-practices.md`: テストケースのベストプラクティス
- `gherkin-guide.md`: Gherkin形式の書き方
- `risk-assessment-matrix.md`: リスク評価基準
- `qa-terminology.md`: QA用語集
