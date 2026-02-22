---
name: setup-instructions
description: "コア思考原則（絶対厳守・深層思考・完了チェックリスト）を~/.claude/instructions/core/にインストールし、~/.claude/CLAUDE.mdに読み込みセクションを追加する。"
---

# コア思考原則インストール

このスキルは以下の思考原則ファイルをグローバル設定にインストールします。

## 利用可能な原則ファイル

| ファイル | 内容 |
|---------|------|
| `base.md` | 基本動作原則 |
| `base2.md` | 絶対厳守事項（最重要） |
| `deep-think.md` | 深層思考プロセス |
| `completion-checklist.md` | 完了前チェックリスト |

## 実行手順

### 1. インストールするファイルを選択

AskUserQuestion でどの原則をインストールするか確認してください:

- すべてインストール（推奨）
- `base2.md` + `deep-think.md` + `completion-checklist.md`（コア3点セット）
- 個別選択

### 2. ディレクトリを作成

```bash
mkdir -p ~/.claude/instructions/core
```

### 3. 原則ファイルをコピー

選択されたファイルを `${CLAUDE_PLUGIN_ROOT}/instructions/core/` から `~/.claude/instructions/core/` へコピー:

```bash
# 例: すべてコピー
cp "${CLAUDE_PLUGIN_ROOT}/instructions/core/"*.md ~/.claude/instructions/core/

# 例: 個別コピー
cp "${CLAUDE_PLUGIN_ROOT}/instructions/core/base2.md" ~/.claude/instructions/core/
cp "${CLAUDE_PLUGIN_ROOT}/instructions/core/deep-think.md" ~/.claude/instructions/core/
cp "${CLAUDE_PLUGIN_ROOT}/instructions/core/completion-checklist.md" ~/.claude/instructions/core/
```

### 4. CLAUDE.md に読み込みセクションを追加

`~/.claude/CLAUDE.md` を Read して、以下のセクションが存在しない場合のみ追加:

```markdown
## 核心原則

- [絶対厳守](./instructions/core/base2.md)
- [深層思考](./instructions/core/deep-think.md)
- [完了チェックリスト](./instructions/core/completion-checklist.md)
```

**重要**: 既にセクションが存在する場合は追加しない（重複防止）。

### 5. 完了報告

インストールしたファイルと追加した CLAUDE.md セクションを報告してください。

## 注意事項

- `${CLAUDE_PLUGIN_ROOT}` は Claude Code プラグインシステムがフック実行時に設定する環境変数
- スキル（SKILL.md）実行時はこの変数が利用できない場合があります
- その場合は `find ~/.claude/plugins/cache/arkatom-plugins -name 'base2.md'` でパスを特定してください
