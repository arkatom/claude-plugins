---
name: mkdocs-07-complete
description: "最終チェックと完了処理。7フェーズ全体の品質検証、チェックリスト確認、サマリー作成。/mkdocs ワークフローの最終フェーズ。"
tools: mcp__serena__search_for_pattern, mcp__serena__read_file, Read, Bash
model: haiku
---

# mkdocs-07-complete - 最終チェックと完了

7フェーズ全体の最終検証と完了処理を実行します。

---

## 🚨 STEP 0: 品質基準の読み込み

```bash
Read: .claude/instructions/must.md
Read: CLAUDE.md
Read: .claude/instructions/core/completion-checklist.md
```

---

## STEP 1: タスクファイル確認

```bash
if [ ! -f "docs/specs/_tasks/mkdocs/07-complete.md" ]; then
  echo "❌ エラー: タスクファイルが見つかりません"
  exit 1
fi
```

---

## STEP 2: 7フェーズ完了確認

### 2.1 各フェーズのコンテキスト確認

```bash
for phase in detect analyze create detail verify optimize; do
  if [ ! -f "docs/specs/_context/${phase}.json" ]; then
    echo "❌ ${phase}.json 不足"
  fi
done
```

---

## STEP 3: ハードコード検出

**禁止ワードの検出**：

```bash
# ハードコードされた数字を検索
grep -r "全33\\|全47\\|全12\\|全31" .claude/agents/mkdocs-*.md

# 結果が0件なら成功
```

**結果が1件でもあれば失敗**

---

## STEP 4: Definition of Done 検証

### 4.1 網羅性チェック

- [ ] analyze.json の全ファイルを処理した
- [ ] detail.json で全ファイルを詳細化した
- [ ] verify.json で全ファイルを検証した

### 4.2 構造チェック

```bash
# 全ファイルが1000行以下
max_lines=$(find docs/specs/ -name "*.md" -not -path "*/_*" -exec wc -l {} \\; | awk '{print $1}' | sort -n | tail -1)

if [ "$max_lines" -gt 1000 ]; then
  echo "❌ 失敗: 1000行超ファイルが存在"
fi
```

### 4.3 リンク検証

```bash
# 内部リンク切れゼロ
find docs/specs/ -name "*.md" -not -path "*/_*" | while read file; do
  # リンク検証
done
```

---

## STEP 5: 完了サマリー作成

### 5.1 ディレクトリ作成

```bash
mkdir -p docs/specs/_summary
```

### 5.2 サマリーファイル作成

**出力先**: `docs/specs/_summary/$(date +%Y%m%d)_completion-summary.md`

```markdown
# /mkdocs 完了サマリー

## 7フェーズ実行履歴

| フェーズ | 日時 | 結果 |
|---------|------|------|
| DETECT | {...} | パターン {X} 検出 |
| ANALYZE | {...} | {N}ファイル分析 |
| CREATE | {...} | 概要ドキュメント作成 |
| DETAIL | {...} | {N}ファイル詳細化 |
| VERIFY | {...} | {N}差分検出・修正 |
| OPTIMIZE | {...} | 構造最適化 |
| COMPLETE | {...} | 品質検証完了 |

## 成果物

総ドキュメント数: {N}件
総ファイル数: {analyze.json の total_files}件
```

---

## STEP 6: クリーンアップ

### 6.1 タスクファイル削除

```bash
rm docs/specs/_tasks/mkdocs/07-complete.md
rmdir docs/specs/_tasks/mkdocs
```

---

## 完了報告

```
🎉 /mkdocs ワークフロー完了

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7フェーズ実行完了
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ DETECT   - パターン検出
✅ ANALYZE  - 網羅的調査・分類
✅ CREATE   - 概要ドキュメント作成
✅ DETAIL   - 詳細化
✅ VERIFY   - コードベース検証
✅ OPTIMIZE - 構造最適化
✅ COMPLETE - 最終検証

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
品質検証結果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- ファイルサイズ: ✅ 全ファイル1000行以下
- リンク整合性:   ✅ リンク切れ 0件
- ハードコード:   ✅ 検出 0件
- 汎用性:         ✅ 完全に動的な設計
```
