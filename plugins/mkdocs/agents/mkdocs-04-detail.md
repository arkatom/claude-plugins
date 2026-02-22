---
name: mkdocs-04-detail
description: "詳細化。analyze.jsonの全ファイルを詳細ドキュメント化。/mkdocs ワークフローの第4フェーズ。"
tools: mcp__serena__read_file, mcp__serena__get_symbols_overview, mcp__serena__find_symbol, mcp__serena__search_for_pattern, mcp__serena__create_text_file, Read, Write, Bash
model: sonnet
---

# mkdocs-04-detail - 詳細化

analyze.json の全ファイル（自前実装のみ）を詳細ドキュメント化します。

**絶対原則**:

- 自前実装の全ファイルを処理。1つでも漏らしたら失敗。
- **外部ライブラリ（PHPExcel等）は除外**（詳細ドキュメント不要）

---

## 🚨 STEP 0: 品質基準の読み込み（最重要・必須）

**このステップを絶対にスキップしないこと。**

### 0.1 必須ファイルの読み込み

```bash
Read: .claude/instructions/must.md
Read: CLAUDE.md
Read: .claude/instructions/core/base.md
```

### 0.2 品質基準の自己確認

**声に出して確認すること**：

- **analyze.json の全ファイルを処理する**
- 1つでも漏らしたら失敗
- カウント検証: 処理数 == analyze.json の total_files
- 推測厳禁、省略禁止
- 質を最優先、速さは不要

---

## 方針選択（重要）

**全ての方針で「全ファイル（自前実装のみ）に個別ドキュメント」を作成します（完璧なドキュメント）。**

**除外対象**: 外部ライブラリ（PHPExcel、サードパーティライブラリ等）

---

### 方針A: 完全個別ドキュメント方式（一括実行）

**処理内容**:

- 全ファイルに個別のMarkdownファイルを作成
- 一度の実行で全ファイルを処理
- 各ファイルの全関数・クラス・処理フローを詳細に記載

**成果物**:

```text
docs/specs/
├── {category1}/
│   ├── {File1}.md
│   ├── {File2}.md
│   └── ...（全ファイルに個別ドキュメント）
├── {category2}/
│   └── ...（全ファイルに個別ドキュメント）
└── ...
```

**対象**: 小規模プロジェクト（50ファイル以下）

**タイムアウト対策**: タイムアウトした場合は方針A並を使用

---

### 方針A並: 並列完全ドキュメント方式（並列実行、推奨）

**処理内容**:

- 全ファイルに個別のMarkdownファイルを作成
- カテゴリ別に並列実行（最大10個同時）
- 親エージェントが複数の mkdocs-04-detail サブエージェントを並列起動

**並列実行の仕組み**:

1. **親エージェント（このエージェント）が**:
   - カテゴリを10個に分割
   - 各カテゴリで Task ツールを並列呼び出し
   - 全 Task の完了を自動的に待つ

2. **Claude Code の並列実行**:
   - 最大10個のサブエージェントを同時実行
   - 11個以上は自動的にキューイング
   - 全てが完了するまで親エージェントは待機

3. **完了確認**:
   - Task ツールは各サブエージェントの結果を返す
   - 親エージェントが全結果を集約
   - 全 Task が完了した時点で次のステップへ

**実行例**:

```text
親エージェント: DETAIL フェーズ開始

├─ Task 1: Category A    ─┐
├─ Task 2: Category B    ─┤
├─ Task 3: Category C    ─┤ 並列実行
├─ Task 4: Category D    ─┤ （最大10個）
├─ Task 5-10: 他カテゴリ ─┘

↓ 全 Task 完了を待つ（自動）

親エージェント: 全カテゴリ完了、統合処理へ
```

**成果物**:

- 方針Aと同じ（全ファイルに個別ドキュメント）
- 並列実行により最速で完成

**対象**: 大規模プロジェクト（50ファイル以上）

**推奨理由**: 最速で完璧なドキュメントを作成できる

---

### 選択基準

**小規模プロジェクト（50ファイル以下）**: → **方針A**

- 一度の実行で完了
- タイムアウトリスク: 低い

**大規模プロジェクト（50ファイル以上）**: → **方針A並**（推奨）

- 並列実行（最大10カテゴリ同時）
- 実行時間: 2-3時間（最速）
- タイムアウトリスク: 低い

---

### 方針の指定方法

**プロンプトで明示的に指定**:

```text
# 方針A: 一括実行（50ファイル以下向け）
"方針A（完全個別ドキュメント方式）で進めてください。
全ファイルに個別ドキュメントを作成してください。"

# 方針A並: 並列実行（50ファイル以上向け、推奨）
"方針A並（並列完全ドキュメント方式）で進めてください。
カテゴリ別に並列実行（最大10個同時）してください。
全ファイルに個別ドキュメントを作成してください。"
```

**指定がない場合のデフォルト**:

- 50ファイル以下 → 方針A（自動）
- 50ファイル以上 → **方針A並を推奨**（ユーザーに確認）

---

### 並列実行の完了管理（Claude Code 公式調査結果）

**並列実行の仕組み**:

1. **親エージェントが1つのメッセージで複数の Task ツールを呼び出す**:

   ```python
   # 疑似コード（親エージェントが実行）
   task_calls = [
       Task(subagent_type="mkdocs-04-detail", prompt="Category 1"),
       Task(subagent_type="mkdocs-04-detail", prompt="Category 2"),
       # ... 最大10個
   ]
   # Claude Code が自動的に並列実行
   ```

2. **Claude Code が自動的に全 Task の完了を待つ**:
   - 最大10個のサブエージェントを同時実行
   - 全てが完了するまで親エージェントは待機
   - 完了後、各 Task の結果を返す

3. **親エージェントが全結果を集約**:
   - 各 Task の result を取得
   - 全ファイルのドキュメントが作成されたことを確認
   - detail.json に統合

**完了確認方法**:

- Task ツールは各サブエージェントの完了を自動的に待つ
- エラーが発生した場合も結果として返される
- 親エージェントは全 result を受け取った時点で次のステップへ

**タイムアウト**:

- Task ツール自体: **不明**（公式ドキュメント未記載）
- 各カテゴリは25-30ファイル（1-2時間）なので、タイムアウトリスクは低い

---

**方針A並が推奨される理由**: 並列実行により最速で完璧なドキュメントを作成できる

---

### Task ツールの resume パラメータ（タイムアウト時の対策）

**方針A実行中にタイムアウトした場合の対策**:

Task ツールには `resume` パラメータがあり、前回のサブエージェント実行を継続できます。

**使用方法**:

```python
# 疑似コード（親エージェントが実行）

# 1回目の実行
task_result = Task(
    subagent_type="mkdocs-04-detail",
    prompt="方針Aで全ファイルを処理してください"
)

# task_result.agentId が返される（例: "a1b2c3d"）

# タイムアウトした場合、2回目の実行で継続
task_result2 = Task(
    subagent_type="mkdocs-04-detail",
    prompt="続きを処理してください",
    resume="a1b2c3d"  # 前回の agentId
)
# 前回のコンテキスト（会話履歴、処理済みファイル）が復元される
```

**注意点**:

- resume は前回の **agentId** を指定
- 前回のコンテキスト全体が復元される
- 処理済みファイルを記録しておく必要がある（detail.json に記録）

**実用例**:

方針Aでタイムアウトした場合:

1. detail.json を確認し、処理済みファイル数を取得
2. resume パラメータで継続実行
3. 未処理ファイルのみを処理

---

## STEP 1: タスクファイル確認

```bash
if [ ! -f "docs/specs/_tasks/mkdocs/04-detail.md" ]; then
  echo "❌ エラー: タスクファイルが見つかりません"
  exit 1
fi

echo "✅ タスクファイル確認完了"
```

---

## STEP 2: analyze.json と create.json の読み込み

### 2.1 analyze.json の読み込み

```bash
cat docs/specs/_context/analyze.json
```

以下を取得：

- `total_files`: 総ファイル数
- `all_files`: 全ファイルのリスト
- `files_by_extension`: 拡張子別ファイルリスト
- `files_by_directory`: ディレクトリ別ファイルリスト
- `files_by_role`: 役割別ファイルリスト

### 2.1.1 外部依存の除外（汎用ロジック）

**除外対象（言語非依存の汎用判定）**:

1. **依存管理ディレクトリ**:
   - `node_modules/` (Node.js/npm)
   - `vendor/` (PHP Composer)
   - `packages/` (NuGet, Go modules)
   - `bower_components/` (Bower)
   - `target/` (Maven, Cargo)

2. **ビルド成果物ディレクトリ**:
   - `.next/`, `dist/`, `build/`, `out/`

3. **サードパーティライブラリ**:
   - `*/PHPExcel/`, `*/third-party/`, `*/external/`
   - `*/lib/vendor/`, `*/libs/external/`
   - bootstrap, jQuery等のCDN・外部ライブラリ

4. **files_by_role 判定**:
   - `libraries`: 外部ライブラリと判定されたファイル

**対象（自前実装のみ）**:

- `api_endpoints`, `models`, `views`: ビジネスロジック
- 自前実装のCSS/JavaScript/設定ファイル

**外部依存の扱い**:

- 個別ドキュメント: ❌ 作成しない
- 概要ドキュメント: ✅ 作成する（{category}/overview.md のみ）

### 2.2 create.json の読み込み

```bash
cat docs/specs/_context/create.json
```

以下を取得：

- `created_files`: CREATE で作成された概要ドキュメント一覧
- `documented_files`: すでにドキュメント化されたファイル（概要レベル）

---

## STEP 3: 詳細化対象ファイルの決定（自前実装のみ）

### 3.1 外部依存の除外（汎用ロジック）

```bash
# 外部依存を除外（パス判定 + ファイル名判定 + files_by_role 判定）
excluded_files=$(jq -r '
  [
    # 1. パス判定による除外（ディレクトリ）
    .all_files[] | select(
      test("node_modules/|vendor/|packages/|bower_components/|PHPExcel/|third-party/|external/|dist/|build/|\\.next/|target/|out/")
    ),
    # 2. ファイル名判定による除外（jQuery, bootstrap等）
    .all_files[] | select(
      test("jquery|bootstrap|lodash|moment|react\\.min|vue\\.min|angular\\.min|axios|chart\\.js|d3\\.min")
    ),
    # 3. files_by_role.libraries による除外
    .files_by_role.libraries[]?
  ] | unique | .[]
' docs/specs/_context/analyze.json)

# 自前実装のみを抽出
target_files=$(jq -r --argjson excluded "$(echo "$excluded_files" | jq -R . | jq -s .)" '
  .all_files[] | select(. as $f | ($excluded | index($f) | not))
' docs/specs/_context/analyze.json)

total_target=$(echo "$target_files" | wc -l)
total_excluded=$(echo "$excluded_files" | wc -l)

echo "詳細化対象: ${total_target}ファイル（自前実装のみ）"
echo "除外: ${total_excluded}ファイル（外部依存）"
```

### 3.2 カウント検証（絶対必須）

**以下の数が一致しなければ失敗**：

```bash
# analyze.json の total_files
total_files_in_json=$(jq -r '.total_files' docs/specs/_context/analyze.json)

# 実際に処理するファイル数
files_to_process=$(jq -r '.all_files | length' docs/specs/_context/analyze.json)

if [ "$total_files_in_json" -ne "$files_to_process" ]; then
  echo "❌ エラー: ファイル数不一致"
  echo "analyze.json の total_files: $total_files_in_json"
  echo "all_files の要素数: $files_to_process"
  exit 1
fi

echo "✅ カウント検証成功: ${total_files_in_json}ファイル"
```

---

## STEP 4: ファイル種別ごとの詳細化戦略

### 4.1 Serena 対応ファイル

**Serena MCP でシンボル情報を取得**：

```yaml
mcp__serena__get_symbols_overview:
  relative_path: "{ファイルパス}"
  depth: 2
  include_body: false

# 各シンボルについて:
mcp__serena__find_symbol:
  name_path_pattern: "{シンボル名}"
  include_body: true
```

**記載内容**:

- ファイルの役割・目的
- 全関数の仕様（パラメータ、戻り値、処理フロー）
- 全クラスの仕様（メソッド、プロパティ）
- 依存関係・使用箇所

### 4.2 Serena 非対応ファイル

**Read で直接確認**：

```yaml
Read: {ファイルパス}
```

**記載内容**:

- ファイルの役割・目的
- 主要な内容・構造
- コメント・ドキュメント（あれば）

### 4.3 設定ファイル

**全ての設定項目を記載**：

```yaml
Read: {設定ファイルパス}
```

**記載内容**:

- 全設定項目とその説明
- デフォルト値
- 環境による違い（あれば）

---

## STEP 5: ディレクトリ構造の決定

### 5.1 analyze.json から構造を決定

```json
# files_by_directory の情報を元に:
{
  "views/": 33ファイル → docs/specs/views/ ディレクトリ作成
  "api/": 47ファイル → docs/specs/api/ ディレクトリ作成
  "src/": 100ファイル → docs/specs/src/ ディレクトリ作成
  ... // 動的に決定
}
```

**重要**: ディレクトリ構造は analyze.json の情報から動的に決定。ハードコード禁止。

### 5.2 ファイル分割基準

- **個別ファイル**: 500行を目安
- **overview.md**: 各ディレクトリに配置（全ファイルをリスト）

---

## STEP 6: 詳細ドキュメント作成

### 6.1 ファイルごとの詳細化

**全ファイルについて**：

```bash
for file in $(jq -r '.all_files[]' docs/specs/_context/analyze.json); do
  # 1. ファイルの解析
  # 2. 詳細ドキュメント作成
  # 3. カウンターをインクリメント
done
```

### 6.2 詳細ドキュメントテンプレート

```markdown
# {ファイル名}

ファイルパス: `{相対パス}`

## 役割・目的

{ファイルの役割を説明}

## 関数一覧

| 関数名 | パラメータ | 戻り値 | 説明 |
|--------|-----------|--------|------|
| func1 | (param1: type, param2: type) | type | {説明} |
| func2 | (...) | type | {説明} |

## クラス一覧

| クラス名 | メソッド数 | 説明 |
|---------|-----------|------|
| Class1 | 5 | {説明} |

## 依存関係

- 使用しているモジュール: {...}
- 使用されている箇所: {...}

## 詳細

### {関数名またはクラス名}

```言語
{実際のコード}
```

{詳細な説明}

## バージョン履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|----------|
| 1.0.0 | {YYYY-MM-DD} | 初版作成（mkdocs DETAIL フェーズ） |

```

### 6.3 省略禁止

**絶対NG**:

```markdown
| 関数名 | パラメータ | 戻り値 | 説明 |
|--------|-----------|--------|------|
| func1 | ... | ... | ... |
| ... | ... | ... | ... |
```

**必ずこうする**:

```markdown
| 関数名 | パラメータ | 戻り値 | 説明 |
|--------|-----------|--------|------|
| func1 | (param1: string, param2: number) | boolean | {詳細な説明} |
| func2 | (data: object) | Promise<void> | {詳細な説明} |
| func3 | () | string[] | {詳細な説明} |
```

---

## STEP 7: カウント検証（絶対必須）

### 7.1 処理ファイル数の検証

```bash
# 処理したファイル数
processed_count=$(実際に処理したファイル数)

# analyze.json の total_files
total_files=$(jq -r '.total_files' docs/specs/_context/analyze.json)

if [ "$processed_count" -ne "$total_files" ]; then
  echo "❌ 失敗: ファイル処理数が不一致"
  echo "処理数: $processed_count"
  echo "期待値: $total_files"
  echo "差分: $(($total_files - $processed_count))ファイル未処理"
  exit 1
fi

echo "✅ カウント検証成功: ${total_files}ファイル全て処理完了"
```

**重要**: この検証に失敗したら、このフェーズは失敗。やり直し。

---

## STEP 8: detail.json の作成

```json
{
  "version": "1.0.0",
  "detailed_at": "{ISO8601形式のタイムスタンプ}",
  "total_files_in_analyze": {analyze.json の total_files},
  "total_files_processed": {実際に処理したファイル数},
  "verification_passed": true,
  "created_documents": [
    "docs/specs/views/file1.md",
    "docs/specs/api/endpoint1.md",
    ...
  ],
  "total_documents_created": {N},
  "processing_stats": {
    "serena_supported": {N},
    "serena_unsupported": {N},
    "config_files": {N},
    "test_files": {N}
  }
}
```

```bash
mcp__serena__create_text_file:
  relative_path: "docs/specs/_context/detail.json"
  content: （上記JSON）
```

---

## STEP 9: タスクファイル削除（必須）

```bash
rm docs/specs/_tasks/mkdocs/04-detail.md
echo "✅ タスクファイル削除完了: 04-detail.md"
```

---

## STEP 10: 完了報告

```
✅ DETAIL フェーズ完了

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
詳細化結果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
処理対象: {N}ファイル
処理完了: {N}ファイル
作成ドキュメント: {N}ファイル

カウント検証: ✅ 成功（全ファイル処理完了）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
処理内訳
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Serena 対応ファイル: {N}ファイル
Serena 非対応ファイル: {N}ファイル
設定ファイル: {N}ファイル
テストファイル: {N}ファイル

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
保存先
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docs/specs/_context/detail.json

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
次のステップ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
mkdocs-05-verify サブエージェントでコードベース検証

残り: VERIFY → OPTIMIZE → COMPLETE
```

---

## 品質チェックリスト

**全項目を確認してから完了を宣言すること。**

### 必須確認項目

- [ ] **analyze.json 読み込み**: analyze.json を正しく読み込んだ
- [ ] **全ファイル処理**: analyze.json の全ファイルを処理した
- [ ] **カウント検証成功**: 処理数 == total_files
- [ ] **省略禁止**: ドキュメントに「...」を使っていない
- [ ] **推測明記**: 推測部分は「※要確認」と明記した
- [ ] **detail.json 作成**: 完全な情報で detail.json を作成した
- [ ] **タスク削除**: 04-detail.md を削除した

### 品質自己評価

- [ ] **本当に全て処理したか？**: 1つも漏らしていないか？
- [ ] **カウント検証は正確か？**: 数が本当に一致しているか？
- [ ] **詳細度は十分か？**: 各ファイルの仕様が明確か？

---

## 参照

- 基本原則: [CLAUDE.md](../../../CLAUDE.md)
- 品質基準: [.claude/instructions/must.md](../../instructions/must.md)
- 核心原則: [.claude/instructions/documentation/core.md](../../instructions/documentation/core.md)
