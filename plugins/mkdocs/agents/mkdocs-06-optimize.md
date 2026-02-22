---
name: mkdocs-06-optimize
description: "ドキュメント構造最適化。巨大ファイル分割、overview.md作成、内部リンク整備。/mkdocs ワークフローの第6フェーズ。"
tools: mcp__serena__read_file, mcp__serena__create_text_file, mcp__serena__replace_content, Read, Edit, Write, Bash
model: sonnet
---

# mkdocs-06-optimize - ドキュメント構造最適化

VERIFY完了後のドキュメント構造を最適化します。

---

## 🚨 STEP 0: 品質基準の読み込み

```bash
Read: .claude/instructions/must.md
Read: CLAUDE.md
```

---

## STEP 1: タスクファイル確認

```bash
if [ ! -f "docs/specs/_tasks/mkdocs/06-optimize.md" ]; then
  echo "❌ エラー: タスクファイルが見つかりません"
  exit 1
fi
```

---

## STEP 2: ファイルサイズ監査

```bash
find docs/specs/ -name "*.md" -not -path "*/_*" -exec wc -l {} \\; | sort -n
```

---

## STEP 3: 巨大ファイルの分割

**1000行超のファイルを分割**：

```bash
# 1000行超のファイルを検出
find docs/specs/ -name "*.md" -not -path "*/_*" -exec wc -l {} \\; | awk '$1 > 1000 {print}'
```

---

## STEP 4: overview.md の作成

**各ディレクトリに overview.md を作成**

---

## STEP 5: 内部リンク検証

```bash
# リンク切れチェック
find docs/specs/ -name "*.md" -not -path "*/_*" | while read file; do
  # リンク検証
done
```

---

## STEP 6: optimize.json の作成

```json
{
  "optimized_at": "{ISO8601}",
  "files_split": [...],
  "overviews_created": [...],
  "links_updated": {N},
  "max_file_lines": {N}
}
```

---

## STEP 7: タスクファイル削除

```bash
rm docs/specs/_tasks/mkdocs/06-optimize.md
```

---

## 完了報告

```
✅ OPTIMIZE フェーズ完了

最大行数: {N}行
1000行超: 0件

次のステップ: mkdocs-07-complete
残り: COMPLETE
```
