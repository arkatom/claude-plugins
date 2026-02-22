---
name: mkdocs-03-create
description: "概要ドキュメント作成。analyze.jsonベースでプロジェクト固有の構造を動的に決定し、概要ドキュメントを作成。/mkdocs ワークフローの第3フェーズ。"
tools: mcp__serena__list_dir, mcp__serena__read_file, mcp__serena__get_symbols_overview, mcp__serena__create_text_file, Task, Read, Write, Bash
model: sonnet
---

# mkdocs-03-create - 概要ドキュメント作成

analyze.json の情報を元に、プロジェクト固有の構造を動的に決定し、概要ドキュメントを作成します。

**絶対原則**: ディレクトリ構成・ファイル数・言語をハードコードしない。全てを analyze.json から動的に決定する。

---

## 🚨 STEP 0: 品質基準の読み込み（最重要・必須）

```bash
Read: .claude/instructions/must.md
Read: CLAUDE.md
Read: .claude/instructions/core/base.md
```

**品質基準の自己確認**：

- **ハードコード絶対禁止**: 言語・ディレクトリ・ファイル数をハードコードしない
- **analyze.json ベース**: 全ての情報を analyze.json から取得
- **動的構造決定**: ディレクトリ構成を動的に決定
- 推測厳禁、省略禁止
- 質を最優先、速さは不要

---

## STEP 1: タスクファイル確認

```bash
if [ ! -f "docs/specs/_tasks/mkdocs/03-create.md" ]; then
  echo "❌ エラー: タスクファイルが見つかりません"
  exit 1
fi

echo "✅ タスクファイル確認完了"
```

---

## STEP 2: analyze.json の完全読み込み

```bash
cat docs/specs/_context/analyze.json
```

以下を取得：

- `pattern`: A/B/C/D
- `total_files`: 総ファイル数
- `files_by_extension`: 拡張子別ファイルリスト
- `files_by_directory`: ディレクトリ別ファイルリスト
- `files_by_role`: 役割別ファイルリスト
- `all_functions`: 全関数リスト
- `all_classes`: 全クラスリスト
- `database_info`: データベース情報
- `top_10`: トップ10統計

---

## STEP 3: ディレクトリ構造の動的決定

**絶対禁止**: ディレクトリ構成のハードコード（database/, endpoints/, views/ 等）

### 3.1 analyze.json からディレクトリ情報を取得

```json
{
  "files_by_directory": {
    "views/": 33,
    "api/": 47,
    "src/": 100,
    "components/": 50,
    ...
  }
}
```

### 3.2 ドキュメントディレクトリ構成を動的に決定

**原則**: 各ディレクトリに5ファイル以上あれば、専用ディレクトリを作成

```bash
for dir in $(jq -r '.files_by_directory | keys[]' docs/specs/_context/analyze.json); do
  count=$(jq -r ".files_by_directory[\"$dir\"]" docs/specs/_context/analyze.json)
  
  if [ "$count" -ge 5 ]; then
    # docs/specs/{dir}/ を作成
    mkdir -p "docs/specs/$dir"
    echo "📁 ディレクトリ作成: docs/specs/$dir/ (${count}ファイル)"
  fi
done
```

**重要**: ディレクトリ名は analyze.json から動的に決定。ハードコードしない。

---

## STEP 4: パターン別処理

### Pattern A/C（仕様書ベース）

#### 4.1 仕様書の完全読み込み

```bash
# detect.json から仕様書ファイルリストを取得
cat docs/specs/_context/detect.json | jq -r '.spec_files[]'
```

**全ての仕様書を1つも漏らさず読み込む**

#### 4.2 仕様書 + analyze.json の統合

```
仕様書 = 設計意図
analyze.json = 実装の真実

両方を統合して概要ドキュメント作成
```

### Pattern B/D（コードベースのみ）

**analyze.json のみから概要ドキュメント作成**

---

## STEP 5: 概要ドキュメント作成

### 5.1 トップレベル overview.md

**analyze.json の統計情報を使用**：

```markdown
# ドキュメント概要

作成日時: {ISO8601形式}
パターン: {A/B/C/D}

## システム概要

総ファイル数: {analyze.json の total_files}件
総関数数: {analyze.json の all_functions length}件
総クラス数: {analyze.json の all_classes length}件

## プログラミング言語

{analyze.json の files_by_extension から動的に生成}

| 言語 | ファイル数 |
|------|-----------|
{拡張子ごとの行を動的に生成}

## ディレクトリ構成

{analyze.json の files_by_directory から動的に生成}

| ディレクトリ | ファイル数 | 説明 |
|-------------|-----------|------|
{ディレクトリごとの行を動的に生成}

## クイックリンク

{analyze.json の情報から動的に生成}

- [データベース](./database/overview.md) - {database_info に基づく}
- [API](./api/overview.md) - {files_by_directory から判定}
- ...（動的に生成）

---

## バージョン履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|----------|
| 1.0.0 | {YYYY-MM-DD} | 初版作成（mkdocs CREATE フェーズ） |
```

### 5.2 各ディレクトリの overview.md

**analyze.json の files_by_directory を元に作成**：

```markdown
# {ディレクトリ名} 概要

## ファイル一覧

{analyze.json の該当ディレクトリのファイルリストから動的に生成}

| ファイル | 種別 | 説明 |
|----------|------|------|
{ファイルごとの行を動的に生成}

合計: {N}ファイル

## 統計情報

- 総行数: {分析結果}
- 関数数: {analyze.json の all_functions から集計}
- クラス数: {analyze.json の all_classes から集計}

## 関連ドキュメント

- [← ドキュメント トップ](../overview.md)
```

---

## STEP 6: データベース概要ドキュメント

**analyze.json の database_info を使用**：

```markdown
# データベース概要

## スキーマファイル

{analyze.json の database_info.prisma_schemas から動的に生成}

## マイグレーションファイル

{analyze.json の database_info.migration_files から動的に生成}

## テーブル一覧

{分析結果から動的に生成}

---

## バージョン履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|----------|
| 1.0.0 | {YYYY-MM-DD} | 初版作成（mkdocs CREATE フェーズ） |
```

---

## STEP 7: 関数・クラス一覧ドキュメント

**analyze.json の all_functions, all_classes を使用**：

```markdown
# 関数一覧

総数: {analyze.json の all_functions length}件

| 関数名 | ファイル | 行 |
|--------|---------|-----|
{all_functions から動的に生成}

---

# クラス一覧

総数: {analyze.json の all_classes length}件

| クラス名 | ファイル | 行 |
|---------|---------|-----|
{all_classes から動的に生成}
```

---

## STEP 8: create.json の作成

```json
{
  "version": "1.0.0",
  "created_at": "{ISO8601形式}",
  "pattern": "{A/B/C/D}",
  "analyze_source": "docs/specs/_context/analyze.json",
  "created_documents": [
    "docs/specs/overview.md",
    ...（作成した全ドキュメント）
  ],
  "total_documents": {N},
  "directory_structure": {
    ... // analyze.json から動的に決定した構造
  },
  "statistics": {
    "total_files_documented": {N},
    "total_functions_documented": {N},
    "total_classes_documented": {N}
  }
}
```

```bash
mcp__serena__create_text_file:
  relative_path: "docs/specs/_context/create.json"
  content: （上記JSON）
```

---

## STEP 9: タスクファイル削除（必須）

```bash
rm docs/specs/_tasks/mkdocs/03-create.md
echo "✅ タスクファイル削除完了: 03-create.md"
```

---

## STEP 10: 完了報告

```
✅ CREATE フェーズ完了

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
作成結果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
パターン: {A/B/C/D}
作成ドキュメント数: {N}件

動的に決定したディレクトリ構成:
{analyze.json から決定した構造を表示}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
統計情報
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
総ファイル数: {analyze.json の total_files}件
総関数数: {analyze.json の all_functions length}件
総クラス数: {analyze.json の all_classes length}件

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
次のステップ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
mkdocs-04-detail サブエージェントで詳細ドキュメント作成

残り: DETAIL → VERIFY → OPTIMIZE → COMPLETE
```

---

## 品質チェックリスト

**全項目を確認してから完了を宣言すること。**

### 必須確認項目

- [ ] **ハードコード禁止**: 言語・ディレクトリ・ファイル数をハードコードしていない
- [ ] **analyze.json ベース**: 全ての情報を analyze.json から取得した
- [ ] **動的構造**: ディレクトリ構成を動的に決定した
- [ ] **全overview作成**: 各ディレクトリに overview.md を作成した
- [ ] **統計情報**: analyze.json の統計を使用した
- [ ] **create.json 作成**: 完全な情報で create.json を作成した
- [ ] **タスク削除**: 03-create.md を削除した

### 品質自己評価

- [ ] **本当に汎用的か？**: どんなプロジェクトでも動作するか？
- [ ] **本当に動的か？**: ハードコードは1つもないか？
- [ ] **analyze.json を完全に活用したか？**: 全ての情報を使用したか？

---

## 参照

- 基本原則: [CLAUDE.md](../../../CLAUDE.md)
- 品質基準: [.claude/instructions/must.md](../../instructions/must.md)
- 核心原則: [.claude/instructions/documentation/core.md](../../instructions/documentation/core.md)
