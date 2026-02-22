---
name: mkdocs-01-detect
description: "ドキュメント作成パターン（A/B/C/D）を検出。仕様書と既存ドキュメントの有無を確認。/mkdocs ワークフローの第1フェーズ。"
tools: mcp__serena__list_dir, mcp__serena__read_file, mcp__serena__find_file, mcp__serena__search_for_pattern, Read, Glob, Grep, Bash
model: sonnet
---

# mkdocs2-detect - パターン検出

ドキュメント作成のパターンを検出し、次のステップを決定します。

---

## 🚨 STEP 0: 品質基準の読み込み（最重要・必須）

**このステップを絶対にスキップしないこと。**

### 0.1 must.md を読み込む

```bash
Read: .claude/instructions/must.md
```

**内容を完全に理解し、以降の全作業で厳守すること。**

### 0.2 CLAUDE.md を読み込む

```bash
Read: CLAUDE.md
```

基本原則を理解する。

### 0.3 品質基準の確認

以下を自分自身に言い聞かせる：

- **深層思考で進める** - 質を最優先、速さは不要
- **網羅的・徹底的な調査を実施** - 手抜き厳禁
- **適当な出力は信頼と価値を地に落とす**
- **推測厳禁** - 必ず実際のファイル・ディレクトリを確認
- **省略禁止** - 全てのファイルを確認し、全て記録

---

## STEP 1: タスクファイル確認

```bash
if [ ! -f "docs/specs/_tasks/mkdocs/01-detect.md" ]; then
  echo "❌ エラー: タスクファイルが見つかりません"
  echo "実行: /mkdocs コマンドで初期化してください"
  exit 1
fi

echo "✅ タスクファイル確認完了"
```

---

## STEP 2: 仕様書の網羅的確認

**「ある」「ない」の判定だけでなく、何があるかを全て記録すること。**

### 2.1 仕様書ディレクトリの存在確認

```bash
# ディレクトリ自体の存在
ls -la docs/specs/_original_specs/ 2>/dev/null || echo "ディレクトリなし"
```

### 2.2 全ファイルの網羅的リスト取得

```bash
# Serena MCP で確認（推奨）
mcp__serena__list_dir:
  relative_path: "docs/specs/_original_specs"
  recursive: true
  skip_ignored_files: true
```

**重要**: recursive: true で全サブディレクトリも確認すること。

### 2.3 仕様書ファイルの詳細検出

以下の全形式を探す（1つも漏らさない）：

| 拡張子 | 形式 | 検出コマンド |
|--------|------|-------------|
| `.xlsx`, `.xls` | Excel | `find ... -name "*.xlsx" -o -name "*.xls"` |
| `.pdf` | PDF | `find ... -name "*.pdf"` |
| `.docx`, `.doc` | Word | `find ... -name "*.docx" -o -name "*.doc"` |
| `.md` | Markdown | `find ... -name "*.md"` |
| `.txt` | Text | `find ... -name "*.txt"` |
| `.csv` | CSV | `find ... -name "*.csv"` |

```bash
# 全形式を一度に検索
find docs/specs/_original_specs/ -type f \( \
  -name "*.xlsx" -o -name "*.xls" -o \
  -name "*.pdf" -o \
  -name "*.docx" -o -name "*.doc" -o \
  -name "*.md" -o -name "*.txt" -o -name "*.csv" \
\) 2>/dev/null
```

**Excel全シート処理**: 総シート数カウント → 全シート処理 → カウント検証（処理数 == 総シート数）

### 2.4 検出結果の記録

**省略禁止**: 検出した全ファイルをリストアップする。

```
仕様書ファイル一覧:
1. docs/specs/_original_specs/xxx.xlsx
2. docs/specs/_original_specs/yyy.pdf
3. ...（全て記載）

合計: N 件
```

**結果判定**:

- 1件以上 → `HAS_SPEC_FILES=true`
- 0件 → `HAS_SPEC_FILES=false`

---

## STEP 3: 既存ドキュメントの網羅的確認

**タスクファイル・コンテキストファイル以外の全 .md を確認。**

### 3.1 docs/specs/ ディレクトリ構造の確認

```bash
# 全体構造を把握
mcp__serena__list_dir:
  relative_path: "docs/specs"
  recursive: true
  skip_ignored_files: true
```

### 3.2 既存ドキュメントのカウント

```bash
# タスク・コンテキスト・差分ディレクトリを除外
find docs/specs/ -name "*.md" \
  -not -path "*/_tasks/*" \
  -not -path "*/_context/*" \
  -not -path "*/_differences/*" \
  -not -path "*/_original_specs/*" \
  2>/dev/null
```

### 3.3 検出結果の記録

**省略禁止**: 検出した全ファイルをリストアップする。

```
既存ドキュメント一覧:
1. docs/specs/overview.md
2. docs/specs/database/schema.md
3. ...（全て記載）

合計: N 件
```

**結果判定**:

- 1件以上 → `HAS_EXISTING_DOCS=true`
- 0件 → `HAS_EXISTING_DOCS=false`

---

## STEP 4: パターン判定

| 仕様書 | 既存ドキュメント | パターン | 説明 |
|--------|------------------|----------|------|
| ✅ あり | ❌ なし | **A** | 仕様書から新規作成 |
| ❌ なし | ❌ なし | **B** | コードベースから新規作成 |
| ✅ あり | ✅ あり | **C** | 仕様書で既存ドキュメント検証・更新 |
| ❌ なし | ✅ あり | **D** | コードベースで既存ドキュメント検証・更新 |

### 4.1 パターン B/D の場合の警告

**Pattern B または D** の場合、必ずユーザーに確認：

```
⚠️ 警告: 仕様書が見つかりません

検出パターン: {B または D}

このパターンでは：
- コードベースのみから情報を抽出します
- 設計意図や要件は推測できない可能性があります
- DB設計の詳細度が下がる可能性があります

仕様書を配置し忘れていませんか？
- 配置する場合 → docs/specs/_original_specs/ に配置後、再度 /mkdocs を実行
- このまま続行 → Y を入力

続行しますか？ [y/N]
```

**ユーザーの明示的な承認なしに続行しないこと。**

---

## STEP 5: プロジェクト構造の事前調査

**CREATE フェーズに有用な情報を収集。**

### 5.1 ソースコードの存在確認

**絶対禁止**: 言語・ディレクトリをハードコードしない。

```yaml
# .gitignore を考慮した全ファイル取得（言語非依存）
mcp__serena__list_dir:
  relative_path: "."
  recursive: true
  skip_ignored_files: true
```

結果からソースコードディレクトリを動的に特定する。

### 5.2 設定ファイルの確認

```bash
# 設定ファイルの存在確認（技術スタック把握のため、対象限定のためではない）
ls -la package.json composer.json Cargo.toml go.mod Gemfile requirements.txt pyproject.toml pom.xml build.gradle *.csproj Makefile CMakeLists.txt tsconfig.json .env* 2>/dev/null
```

### 5.3 データベース関連の確認

```bash
# Prisma スキーマ
find . -name "schema.prisma" -o -name "*.prisma" 2>/dev/null

# マイグレーションファイル
find . -path "*/migrations/*" -name "*.sql" 2>/dev/null | head -5
```

---

## STEP 6: コンテキスト情報の保存

**次のステップで使用するため、検出結果を JSON 形式で保存。**

```bash
mkdir -p docs/specs/_context

cat > docs/specs/_context/detect.json << 'EOF'
{
  "pattern": "{A/B/C/D}",
  "has_spec_files": {true/false},
  "has_existing_docs": {true/false},
  "spec_files": [
    "docs/specs/_original_specs/file1.xlsx",
    "docs/specs/_original_specs/file2.pdf"
  ],
  "existing_docs": [
    "docs/specs/overview.md",
    "docs/specs/database/schema.md"
  ],
  "source_directories": [
    "src/",
    "functions/"
  ],
  "config_files": [
    "package.json",
    "tsconfig.json"
  ],
  "database_schema_found": {true/false},
  "detected_at": "{ISO8601形式のタイムスタンプ}"
}
EOF
```

**重要**: 全てのフィールドを実際の値で埋めること。推測値は入れない。

---

## STEP 7: タスクファイル削除（必須）

```bash
rm docs/specs/_tasks/mkdocs2/01-detect.md
echo "✅ タスクファイル削除完了: 01-detect.md"
```

---

## STEP 8: 完了報告

ユーザーに詳細な結果を報告：

```
✅ DETECT フェーズ完了

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
検出結果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
パターン: {A/B/C/D}
仕様書: {あり (N件) / なし}
既存ドキュメント: {あり (N件) / なし}

仕様書ファイル:
{ファイル一覧または「なし」}

既存ドキュメント:
{ファイル一覧または「なし」}

ソースディレクトリ:
{検出されたディレクトリ}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
次のステップ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
mkdocs-02-analyze サブエージェントで網羅的調査・分類を実行

残り: ANALYZE → CREATE → DETAIL → VERIFY → OPTIMIZE → COMPLETE
```

---

## 品質チェックリスト

**全項目を確認してから完了を宣言すること。**

### 必須確認項目

- [ ] **STEP 0 完了**: must.md と CLAUDE.md を読んで理解した
- [ ] **網羅的調査**: 仕様書ディレクトリを再帰的に全て確認した
- [ ] **網羅的調査**: 既存ドキュメントを全て確認した
- [ ] **省略なし**: 検出した全ファイルをリストアップした
- [ ] **パターン判定**: 正確に判定し、根拠を示した
- [ ] **B/D 確認**: Pattern B/D の場合、ユーザー確認を得た
- [ ] **コンテキスト保存**: detect.json を正確な値で作成した
- [ ] **タスク削除**: 01-detect.md を削除した

### 品質確認

- [ ] **推測なし**: 全ての情報は実際のファイル確認に基づいている
- [ ] **深層思考**: 表面的な確認でなく、徹底的に調査した
- [ ] **丁寧な報告**: ユーザーに十分な情報を提供した

---

## 参照

- 品質基準: [.claude/instructions/must.md](../../instructions/must.md)
- 核心原則: [.claude/instructions/documentation/core.md](../../instructions/documentation/core.md)
- 基本原則: [CLAUDE.md](../../../CLAUDE.md)
