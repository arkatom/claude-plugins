---
name: mkdocs-02-analyze
description: "網羅的調査・分類。プロジェクト固有情報を動的に発見し、analyze.jsonに保存。/mkdocs ワークフローの第2フェーズ。"
tools: mcp__serena__list_dir, mcp__serena__read_file, mcp__serena__get_symbols_overview, mcp__serena__find_symbol, mcp__serena__search_for_pattern, mcp__serena__create_text_file, Read, Bash
model: sonnet
---

# mkdocs-02-analyze - 網羅的調査・分類

プロジェクト固有の情報を動的に発見・分類し、analyze.json に保存します。

**絶対原則**: 言語・ディレクトリ・ファイル種別をハードコードしない。全てを動的に発見する。

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

- **言語・ディレクトリのハードコード絶対禁止**
- 全ファイルを動的に発見
- 拡張子・ディレクトリ・役割を動的に分類
- 推測厳禁、省略禁止
- 質を最優先、速さは不要

---

## STEP 1: タスクファイル確認

```bash
if [ ! -f "docs/specs/_tasks/mkdocs/02-analyze.md" ]; then
  echo "❌ エラー: タスクファイルが見つかりません"
  exit 1
fi

echo "✅ タスクファイル確認完了"
```

---

## STEP 2: DETECT コンテキストの読み込み

```bash
cat docs/specs/_context/detect.json
```

以下を取得：

- `pattern`: A/B/C/D
- `source_directories`: ソースディレクトリ候補（参考情報）

**重要**: source_directories は参考情報のみ。これに限定せず、全ファイルを対象とする。

---

## STEP 3: 全ファイルの網羅的列挙

**絶対原則**: 言語・ディレクトリのハードコード禁止。全てを動的に発見する。

### 3.1 全ファイルの取得

```yaml
# Serena MCP で全ファイルを取得（言語非依存）
mcp__serena__list_dir:
  relative_path: "."
  recursive: true
  skip_ignored_files: true
```

**結果を完全に記録する。1つも漏らさない。**

### 3.2 ファイル総数のカウント

```bash
# 総ファイル数を記録
total_files=$(上記結果のファイル数)
echo "総ファイル数: ${total_files}件"
```

---

## STEP 4: 拡張子による動的分類

**絶対禁止**: 拡張子リストのハードコード。発見した拡張子のみを使用。

### 4.1 全拡張子の抽出

```bash
# 全ファイルから拡張子を抽出し、カウント
# 例: {".php": 50, ".js": 12, ".css": 6, ".html": 33, ...}
```

### 4.2 拡張子別ファイルリストの作成

```json
{
  "files_by_extension": {
    ".php": ["file1.php", "file2.php", ...],
    ".js": ["file1.js", "file2.js", ...],
    ".css": ["file1.css", ...],
    ".html": ["file1.html", ...],
    ".ts": ["file1.ts", ...],
    ".py": ["file1.py", ...],
    ".go": ["file1.go", ...],
    ... // 発見した全拡張子
  }
}
```

**重要**: 拡張子リストは固定しない。プロジェクトに存在する全拡張子を対象とする。

---

## STEP 5: ディレクトリによる動的分類

**絶対禁止**: ディレクトリ名のハードコード。発見したディレクトリのみを使用。

### 5.1 全ディレクトリの抽出

```bash
# 全ファイルからディレクトリパスを抽出
# 例: {"views/": 33, "api/": 47, "src/": 100, "components/": 50, ...}
```

### 5.2 ディレクトリ別ファイルリストの作成

```json
{
  "files_by_directory": {
    "views/": ["views/file1.php", "views/file2.php", ...],
    "api/": ["api/endpoint1.php", ...],
    "src/": ["src/file1.ts", ...],
    "components/": ["components/Button.tsx", ...],
    ... // 発見した全ディレクトリ
  }
}
```

**重要**: ディレクトリ名は固定しない。プロジェクトに存在する全ディレクトリを対象とする。

---

## STEP 6: 役割による動的判定

**全ファイルを対象に役割を推測**（ファイル名・パス・内容から）：

### 6.1 役割カテゴリの動的決定

ファイル名・パスから役割を推測：

```json
{
  "files_by_role": {
    "views": [...],  // ファイル名に view, template, html が含まれる
    "api_endpoints": [...],  // ディレクトリ名に api, routes, controllers が含まれる
    "models": [...],  // ファイル名に model, entity, schema が含まれる
    "utilities": [...],  // ファイル名に util, helper, common が含まれる
    "tests": [...],  // ディレクトリ名に test, spec が含まれる
    "config": [...],  // ファイル名に config, settings が含まれる
    "unknown": [...]  // 上記に該当しないファイル
  }
}
```

**重要**: 役割カテゴリも動的に決定。プロジェクトの実態に応じて追加・変更する。

---

## STEP 7: 全シンボルの抽出

**Serena MCP 対応ファイルについて、全シンボルを抽出**

### 7.1 Serena 対応言語の判定

各ファイルに対して `get_symbols_overview` を試行：

```yaml
mcp__serena__get_symbols_overview:
  relative_path: "{ファイルパス}"
  depth: 2
```

- **成功** → シンボル情報を取得
- **エラー** → Serena 非対応言語、スキップ

### 7.2 全関数・全クラスのリスト作成

```json
{
  "all_functions": [
    {
      "name": "function_name",
      "file": "path/to/file.php",
      "line": 10
    },
    ...
  ],
  "all_classes": [
    {
      "name": "ClassName",
      "file": "path/to/file.php",
      "line": 5
    },
    ...
  ]
}
```

**重要**: 全ファイルを試行。Serena 対応ファイルのみシンボル抽出。

---

## STEP 8: データベース情報の抽出

### 8.1 Prisma スキーマの確認

```bash
# Prisma スキーマファイルの検索
find . -name "schema.prisma" -o -name "*.prisma" 2>/dev/null
```

### 8.2 マイグレーションファイルの確認

```bash
# SQLマイグレーションファイルの検索
find . -path "*/migrations/*" -name "*.sql" 2>/dev/null
```

### 8.3 データベース定義の検索

```yaml
# SQL の CREATE TABLE 文を検索
mcp__serena__search_for_pattern:
  substring_pattern: "CREATE TABLE"
  restrict_search_to_code_files: false
```

結果を記録：

```json
{
  "database_info": {
    "prisma_schemas": [...],
    "migration_files": [...],
    "table_definitions_found": true/false
  }
}
```

---

## STEP 9: 統計情報の集計

### 9.1 全カテゴリの集計

```json
{
  "statistics": {
    "total_files": 実際の数,
    "total_functions": 実際の数,
    "total_classes": 実際の数,
    "extensions_count": 実際の数,
    "directories_count": 実際の数,
    "serena_supported_files": 実際の数,
    "serena_unsupported_files": 実際の数
  }
}
```

### 9.2 トップ10の抽出

```json
{
  "top_10": {
    "most_common_extensions": [
      {".php": 50},
      {".js": 12},
      ...
    ],
    "largest_directories": [
      {"views/": 33},
      {"api/": 47},
      ...
    ],
    "files_with_most_functions": [
      {"inc.php": 53},
      ...
    ]
  }
}
```

---

## STEP 10: analyze.json の作成

**全ての情報を analyze.json に保存**：

```json
{
  "version": "1.0.0",
  "analyzed_at": "{ISO8601形式のタイムスタンプ}",
  "pattern": "{A/B/C/D}",
  
  "statistics": {
    "total_files": {実際の数},
    "total_functions": {実際の数},
    "total_classes": {実際の数},
    "extensions_count": {実際の数},
    "directories_count": {実際の数},
    "serena_supported_files": {実際の数},
    "serena_unsupported_files": {実際の数}
  },
  
  "all_files": [
    "path/to/file1.php",
    "path/to/file2.js",
    ...
  ],
  
  "files_by_extension": {
    ".php": ["file1.php", "file2.php", ...],
    ".js": ["file1.js", ...],
    ...
  },
  
  "files_by_directory": {
    "views/": ["views/file1.php", ...],
    "api/": ["api/endpoint1.php", ...],
    ...
  },
  
  "files_by_role": {
    "views": [...],
    "api_endpoints": [...],
    "models": [...],
    "utilities": [...],
    "tests": [...],
    "config": [...],
    "unknown": [...]
  },
  
  "all_functions": [
    {"name": "...", "file": "...", "line": ...},
    ...
  ],
  
  "all_classes": [
    {"name": "...", "file": "...", "line": ...},
    ...
  ],
  
  "database_info": {
    "prisma_schemas": [...],
    "migration_files": [...],
    "table_definitions_found": true/false
  },
  
  "top_10": {
    "most_common_extensions": [...],
    "largest_directories": [...],
    "files_with_most_functions": [...]
  }
}
```

```bash
mcp__serena__create_text_file:
  relative_path: "docs/specs/_context/analyze.json"
  content: （上記JSON）
```

---

## STEP 11: タスクファイル削除（必須）

```bash
rm docs/specs/_tasks/mkdocs/02-analyze.md
echo "✅ タスクファイル削除完了: 02-analyze.md"
```

---

## STEP 12: 完了報告

```
✅ ANALYZE フェーズ完了

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
調査結果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
総ファイル数: {N}件
総関数数: {N}件
総クラス数: {N}件

検出された拡張子: {N}種類
検出されたディレクトリ: {N}種類

Serena 対応ファイル: {N}件
Serena 非対応ファイル: {N}件

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
トップ10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
最も多い拡張子:
1. {拡張子}: {N}件
2. {拡張子}: {N}件
...

最大のディレクトリ:
1. {ディレクトリ}: {N}件
2. {ディレクトリ}: {N}件
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
保存先
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docs/specs/_context/analyze.json

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
次のステップ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
mkdocs-03-create サブエージェントで概要ドキュメント作成

残り: CREATE → DETAIL → VERIFY → OPTIMIZE → COMPLETE
```

---

## 品質チェックリスト

**全項目を確認してから完了を宣言すること。**

### 必須確認項目

- [ ] **言語ハードコード禁止**: 言語リストをハードコードしていない
- [ ] **ディレクトリハードコード禁止**: ディレクトリ名をハードコードしていない
- [ ] **拡張子ハードコード禁止**: 拡張子リストをハードコードしていない
- [ ] **全ファイル列挙**: 全てのファイルを動的に発見した
- [ ] **全拡張子記録**: 発見した全拡張子を記録した
- [ ] **全ディレクトリ記録**: 発見した全ディレクトリを記録した
- [ ] **シンボル抽出**: Serena 対応ファイルのシンボルを抽出した
- [ ] **analyze.json 作成**: 完全な情報で analyze.json を作成した
- [ ] **タスク削除**: 02-analyze.md を削除した

### 品質自己評価

- [ ] **本当に汎用的か？**: どんなプロジェクトでも動作するか？
- [ ] **本当に網羅的か？**: 全てのファイルを対象としたか？
- [ ] **本当に動的か？**: ハードコードは1つもないか？

---

## 参照

- 基本原則: [CLAUDE.md](../../../CLAUDE.md)
- 品質基準: [.claude/instructions/must.md](../../instructions/must.md)
- 核心原則: [.claude/instructions/documentation/core.md](../../instructions/documentation/core.md)
