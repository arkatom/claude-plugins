---
name: worktree-task
description: "Git Worktreeで並行タスク処理を行う標準化されたワークフロー。planファイルを指定するだけでworktreeを作成し、並行処理を開始できる。コンテキスト汚染を防ぎながら複数タスクを並行処理したい場合に使用。"
---

# Git Worktree Task

planファイルから自動的にGit Worktreeを作成し、並行タスク処理を可能にする。

## 実行方法

ユーザーが planfile のパスを指定したら、以下のスクリプトを実行：

```bash
.claude/skills/worktree-task/scripts/gwt.sh <planfile>
```

**重要**: スクリプトの出力を**そのまま全て**表示すること。追加の説明は不要。

## スクリプトの動作

`gwt.sh` が自動的に以下を実行：

1. planfile 名から task-name を抽出（例: `dark-mode.plan.md` → `dark-mode`）
2. `.worktrees/<task-name>` ディレクトリとブランチ `feature/<task-name>` を作成
3. **rsync で Git 管理外のファイル（node_modules, .env, venv など）を同期** ⭐
4. 次のステップをユーザーに案内

## 使用例

```bash
# ユーザー入力
/worktree-task @docs/courses/05/dark-mode.plan.md

# 実行するコマンド
.claude/skills/worktree-task/scripts/gwt.sh docs/courses/05/dark-mode.plan.md
```

## 並行処理パターン

複数タスクを並行処理する場合：

1. **メインターミナル**: 軽いタスク（ドキュメント更新など）
2. **新しいターミナル**: 重いタスク（実装作業）を Worktree で実行

```bash
# ターミナル1（メイン）
/worktree-task @plans/heavy-feature.plan.md
# → 別ターミナルでの作業を案内後、軽いタスクを続行

# ターミナル2（新規）
cd .worktrees/heavy-feature && claude
# → @plans/heavy-feature.plan.md を実装
```

## 自動クリーンアップ

**SessionEnd時に自動実行** されるクリーンアップ機能：

- `gwt-cleanup.sh` が全worktreeをチェック
- mainブランチにマージ済みのブランチを自動削除
- PRマージ後、次回セッション終了時に自動的にクリーンアップされる

### 手動クリーンアップ（必要な場合のみ）

```bash
git worktree remove .worktrees/<task-name>
git branch -d feature/<task-name>
```

## エラーハンドリング

スクリプトがエラーを返した場合のみ、追加の説明を提供。
