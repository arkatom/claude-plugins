---
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, mcp__serena__*
description: "最高品質のドキュメントを生成する7フェーズワークフロー。プロジェクト固有情報を動的に発見し、汎用的なドキュメント生成を実現。"
---

# /mkdocs - 最高品質ドキュメント作成ワークフロー v4.0

プロジェクト固有の情報を動的に発見し、完全に汎用的なドキュメント生成を実現する7フェーズワークフロー。

**絶対原則**: 言語・ディレクトリ・ファイル数をハードコードしない。全てを動的に発見する。

---

## 7フェーズワークフロー

```
DETECT → ANALYZE → CREATE → DETAIL → VERIFY → OPTIMIZE → COMPLETE
  ↓        ↓         ↓         ↓        ↓         ↓          ↓
パターン  全体調査   概要作成   詳細化   検証済み   最適化    完成
```

1. **DETECT**: 仕様書・既存ドキュメントからパターン（A/B/C/D）を判定
2. **ANALYZE**: プロジェクト固有の情報を動的に発見・分類 → analyze.json
3. **CREATE**: analyze.json ベースで概要ドキュメント作成
4. **DETAIL**: analyze.json の全ファイルを詳細化
5. **VERIFY**: コードベースと照合し差分を発見・修正
6. **OPTIMIZE**: ファイル分割、リンク整備、構造最適化
7. **COMPLETE**: 最終チェックと完了処理

---

## 初期化処理

```bash
# ディレクトリ作成
mkdir -p docs/specs/_tasks/mkdocs
mkdir -p docs/specs/_context
mkdir -p docs/specs/_differences

# タスクファイル作成（01-07）
for i in {1..7}; do
  phase_name=$(case $i in
    1) echo "DETECT" ;;
    2) echo "ANALYZE" ;;
    3) echo "CREATE" ;;
    4) echo "DETAIL" ;;
    5) echo "VERIFY" ;;
    6) echo "OPTIMIZE" ;;
    7) echo "COMPLETE" ;;
  esac)

  cat > "docs/specs/_tasks/mkdocs/0${i}-$(echo $phase_name | tr 'A-Z' 'a-z').md" << EOF
# $phase_name フェーズ

実行: mkdocs-0${i}-$(echo $phase_name | tr 'A-Z' 'a-z') サブエージェントを使用
EOF
done

echo "✅ タスクファイル作成完了 (01-07)"
```

---

## 実行方法

### フェーズ1: DETECT

```
Task tool:
- subagent_type: "mkdocs-01-detect"
- prompt: "DETECT フェーズを実行してください。"
```

### フェーズ2: ANALYZE

```
Task tool:
- subagent_type: "mkdocs-02-analyze"
- prompt: "ANALYZE フェーズを実行してください。プロジェクト固有の情報を動的に発見し、analyze.json に保存してください。"
```

### フェーズ3-7: 同様に順次実行

各フェーズは前フェーズの完了が必須。タスクファイルで制御。

---

## 品質基準（Definition of Done）

以下を**全て**満たして初めて「完了」：

### 網羅性

- [ ] analyze.json の全ファイルを処理した
- [ ] detail.json で全ファイルを詳細化した
- [ ] verify.json で全ファイルを検証した

### 汎用性

- [ ] 言語・ディレクトリ・ファイル数のハードコードゼロ
- [ ] analyze.json ベースの完全に動的な設計

### 構造

- [ ] 全ファイルが1000行以下
- [ ] 内部リンク切れゼロ
- [ ] 各ディレクトリに overview.md がある

---

## 参照

- 核心原則: [.claude/instructions/documentation/core.md](../instructions/documentation/core.md)
- 各サブエージェント: `.claude/agents/mkdocs-0X-*.md`
