#!/bin/bash
set -euo pipefail

# SessionStart フックでセッション開始時刻を記録するスクリプト
# CLAUDE_PROJECT_DIR はClaudeが設定する環境変数

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"

if [ -z "${PROJECT_DIR}" ]; then
  # プロジェクトディレクトリが不明な場合は何もしない
  exit 0
fi

# 一時ディレクトリを作成（存在しない場合）
TMP_DIR="${PROJECT_DIR}/.claude/tmp"
mkdir -p "${TMP_DIR}"

# 開始時刻を記録（ISO 8601 UTC形式）
START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S")

# ファイルに保存
echo "${START_TIME}" > "${TMP_DIR}/session-start-time"

# 何も出力しない（フックは静かに実行）
exit 0
