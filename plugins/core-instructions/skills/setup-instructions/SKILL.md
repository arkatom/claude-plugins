---
name: setup-instructions
description: "コア指示ファイル（鉄則・実行プロセス・サブエージェントポリシー）を~/.claude/instructions/core/にインストールし、~/.claude/CLAUDE.mdに読み込みセクションを追加する。"
---

# コア指示ファイルインストール

このスキルは以下の指示ファイルをグローバル設定にインストールします。

## 利用可能なファイル

| ファイル | 内容 |
|---------|------|
| `rules.md` | 鉄則・必須作業 |
| `process.md` | 提案基準・完了チェックリスト |
| `subagent-policy.md` | サブエージェント利用ポリシー |

## 実行手順

### 1. インストールするファイルを選択

AskUserQuestion でどのファイルをインストールするか確認してください:

- すべてインストール（推奨）
- 個別選択

### 2. ディレクトリを作成

```bash
mkdir -p ~/.claude/instructions/core
```

### 3. ファイルをコピー

選択されたファイルを `${CLAUDE_PLUGIN_ROOT}/instructions/core/` から `~/.claude/instructions/core/` へコピー:

```bash
# 例: すべてコピー
cp "${CLAUDE_PLUGIN_ROOT}/instructions/core/"*.md ~/.claude/instructions/core/

# 例: 個別コピー
cp "${CLAUDE_PLUGIN_ROOT}/instructions/core/rules.md" ~/.claude/instructions/core/
cp "${CLAUDE_PLUGIN_ROOT}/instructions/core/process.md" ~/.claude/instructions/core/
cp "${CLAUDE_PLUGIN_ROOT}/instructions/core/subagent-policy.md" ~/.claude/instructions/core/
```

### 4. CLAUDE.md に読み込みセクションを追加

`~/.claude/CLAUDE.md` を Read して、以下のセクションが存在しない場合のみ追加:

```markdown
## 核心原則（必須）

- [鉄則](./instructions/core/rules.md)
- [実行プロセス](./instructions/core/process.md)
- [サブエージェントポリシー](./instructions/core/subagent-policy.md)
```

**重要**: 既にセクションが存在する場合は追加しない（重複防止）。既存のセクションがある場合は新しいファイル名に置き換える。

### 5. 完了報告

インストールしたファイルと追加した CLAUDE.md セクションを報告してください。

## 注意事項

- `${CLAUDE_PLUGIN_ROOT}` は Claude Code プラグインシステムがフック実行時に設定する環境変数
- スキル（SKILL.md）実行時はこの変数が利用できない場合があります
- その場合は `find ~/.claude/plugins/cache/arkatom-plugins -name 'rules.md'` でパスを特定してください
