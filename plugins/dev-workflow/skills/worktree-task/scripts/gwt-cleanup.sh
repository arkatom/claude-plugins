#!/bin/bash

# Git Worktree 自動クリーンアップスクリプト
# マージ済みのworktreeを自動的に削除する

set -euo pipefail

# worktreesディレクトリが存在しない場合は終了
if [ ! -d ".worktrees" ]; then
    exit 0
fi

# mainブランチの最新状態を取得
git fetch origin main --quiet 2>/dev/null || true

# 削除したworktreeをカウント
CLEANED=0

# 全てのworktreeをチェック
git worktree list --porcelain 2>/dev/null | while IFS= read -r line; do
    if [[ $line == worktree* ]]; then
        WORKTREE_PATH="${line#worktree }"

        # .worktrees配下のみ対象
        if [[ ! "$WORKTREE_PATH" =~ \.worktrees/ ]]; then
            continue
        fi

        # 次の行でブランチ情報を取得
        read -r branch_line
        if [[ $branch_line == branch* ]]; then
            BRANCH="${branch_line#branch refs/heads/}"

            # mainブランチにマージ済みかチェック
            if git branch --merged origin/main 2>/dev/null | grep -q "^\s*${BRANCH}$"; then
                echo "🧹 マージ済みのworktreeを削除: $WORKTREE_PATH (branch: $BRANCH)"

                # worktreeを削除
                git worktree remove "$WORKTREE_PATH" --force 2>/dev/null || true

                # ブランチを削除
                git branch -d "$BRANCH" 2>/dev/null || true

                CLEANED=$((CLEANED + 1))
            fi
        fi
    fi
done

# 結果を表示（削除があった場合のみ）
if [ $CLEANED -gt 0 ]; then
    echo ""
    echo "✅ ${CLEANED}個のworktreeをクリーンアップしました"
fi

exit 0
