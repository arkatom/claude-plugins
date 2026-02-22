#!/bin/bash

# Git Worktree Task スクリプト
# planファイルから自動的にtask-nameを抽出し、worktreeを作成する

set -euo pipefail

# 引数チェック
if [ $# -lt 1 ]; then
    echo "使い方: $0 <planファイル>"
    echo ""
    echo "例:"
    echo "  $0 docs/courses/05/dark-mode.plan.md"
    echo "  $0 @docs/courses/05/dark-mode.plan.md"
    exit 1
fi

PLANFILE="$1"

# @ 記法を除去
PLANFILE="${PLANFILE#@}"

# planファイルの存在確認
if [ ! -f "$PLANFILE" ]; then
    echo "❌ エラー: planファイルが見つかりません: $PLANFILE"
    exit 1
fi

# task-name を抽出
# 例: docs/courses/05/dark-mode.plan.md → dark-mode
PLANFILE_BASE=$(basename "$PLANFILE")
TASK_NAME="${PLANFILE_BASE%.plan.md}"
TASK_NAME="${TASK_NAME%.md}"  # .plan.md がない場合のフォールバック
TARGET_DIR=".worktrees/$TASK_NAME"

echo "🔨 タスク用worktreeを作成中: $TASK_NAME..."
echo ""

# Worktree ディレクトリの存在確認
if [ -d "$TARGET_DIR" ]; then
    echo "⚠️  警告: Worktreeディレクトリが既に存在します: $TARGET_DIR"
    echo "   先に 'git worktree remove $TARGET_DIR' で削除してください。"
    exit 1
fi

# Worktree とブランチを作成
# 新しいブランチを作成するか、既存のブランチを使用
if git show-ref --verify --quiet "refs/heads/feature/$TASK_NAME"; then
    echo "📌 既存のbranchを使用: feature/$TASK_NAME"
    git worktree add "$TARGET_DIR" "feature/$TASK_NAME"
else
    echo "🌿 新しいbranchを作成: feature/$TASK_NAME"
    git worktree add "$TARGET_DIR" -b "feature/$TASK_NAME"
fi

if [ $? -ne 0 ]; then
    echo "❌ worktreeの作成に失敗しました。"
    exit 1
fi

# Git管理外のファイルを同期
# これにより node_modules/, .env, venv/ などがコピーされる
echo ""
echo "📦 Git管理外のファイルを同期中 (node_modules, .env, venv など)..."
rsync -a --ignore-existing \
    --exclude='.git' \
    --exclude='.worktrees' \
    ./ "$TARGET_DIR/"

# 完了案内
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Worktreeの作成が完了しました！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 場所: $TARGET_DIR"
echo "🌿 Branch: feature/$TASK_NAME"
echo "📄 Plan: $PLANFILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 次のステップ (新しいターミナルで実行):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  cd $TARGET_DIR && claude"
echo ""
echo "Claude起動後に実行:"
echo "  @$PLANFILE を実装してください"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
