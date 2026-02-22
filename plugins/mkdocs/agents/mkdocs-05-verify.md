---
name: mkdocs-05-verify
description: "コードベース検証。analyze.jsonとdetail.jsonベースで全ドキュメントとコードを照合し、差分を発見・修正。/mkdocs ワークフローの第5フェーズ。"
tools: mcp__serena__get_symbols_overview, mcp__serena__find_symbol, mcp__serena__search_for_pattern, mcp__serena__read_file, mcp__serena__create_text_file, Task, Read, Edit, Bash
model: sonnet
---

# mkdocs-05-verify - コードベース検証

analyze.json と detail.json ベースで全ドキュメントとコードを照合し、差分を発見・修正します。

**絶対原則**: analyze.json の全ファイルを検証。ハードコード禁止。

---

## 🚨 STEP 0: 品質基準の読み込み

```bash
Read: .claude/instructions/must.md
Read: CLAUDE.md
```

**品質基準**: ハードコード禁止、analyze.json ベース、全ファイル検証

---

## STEP 1: タスクファイル確認

```bash
if [ ! -f "docs/specs/_tasks/mkdocs/05-verify.md" ]; then
  echo "❌ エラー: タスクファイルが見つかりません"
  exit 1
fi
```

---

## STEP 2: analyze.json と detail.json の読み込み

```bash
cat docs/specs/_context/analyze.json
cat docs/specs/_context/detail.json
```

以下を取得：
- `total_files`: 総ファイル数
- `all_files`: 全ファイルリスト
- `files_by_extension`: 拡張子別ファイルリスト
- `documented_files`: ドキュメント化されたファイル

---

## STEP 3: 検証対象の動的決定

**analyze.json から全ファイルリストを取得**：

```bash
total_files=$(jq -r '.total_files' docs/specs/_context/analyze.json)
echo "検証対象: ${total_files}ファイル"
```

**絶対禁止**: 特定の言語・ディレクトリのみ検証

---

## STEP 4: 全ファイルの検証

### 4.1 Serena 対応ファイルの検証

```yaml
# analyze.json の all_files から順次処理
for file in $(jq -r '.all_files[]' analyze.json); do
  mcp__serena__get_symbols_overview:
    relative_path: "$file"
    depth: 2
done
```

### 4.2 検証カウント

```bash
# 検証したファイル数 == analyze.json の total_files
verified_count=$(実際に検証したファイル数)
total=$(jq -r '.total_files' docs/specs/_context/analyze.json)

if [ "$verified_count" -ne "$total" ]; then
  echo "❌ 失敗: 検証数不一致"
  exit 1
fi
```

---

## STEP 5: 差分レポート作成

**動的に差分を記録**：

```markdown
# コードベース検証レポート

## 検証概要

| 項目 | 値 |
|------|-----|
| 検証対象ファイル数 | {analyze.json の total_files}件 |
| 検証完了ファイル数 | {実際の数}件 |
| 発見された差分数 | {N}件 |

## 詳細な差分一覧

{動的に生成}
```

---

## STEP 6: verify.json の作成

```json
{
  "verified_at": "{ISO8601}",
  "total_files_in_analyze": {analyze.json の total_files},
  "total_files_verified": {実際の数},
  "verification_passed": true,
  "differences_found": {N},
  "difference_report": "docs/specs/_differences/{YYYYMMDD}_verification_report.md"
}
```

---

## STEP 7: タスクファイル削除

```bash
rm docs/specs/_tasks/mkdocs/05-verify.md
```

---

## 完了報告

```
✅ VERIFY フェーズ完了

検証ファイル数: {analyze.json の total_files}件
発見した差分: {N}件

次のステップ: mkdocs-06-optimize
残り: OPTIMIZE → COMPLETE
```

---

## 参照

- [CLAUDE.md](../../../CLAUDE.md)
- [must.md](../../instructions/must.md)
