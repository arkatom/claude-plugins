#!/bin/bash
set -euo pipefail

# Agent Teams環境変数をグローバル設定に追加するスクリプト

SETTINGS_FILE="${HOME}/.claude/settings.json"

# settings.jsonが存在しない場合は作成
if [ ! -f "${SETTINGS_FILE}" ]; then
  echo '{}' > "${SETTINGS_FILE}"
fi

# jqが使用可能かチェック
if ! command -v jq &> /dev/null; then
  echo "❌ jqが見つかりません。インストールしてください: brew install jq"
  exit 1
fi

# 既に設定済みか確認
CURRENT_VALUE=$(jq -r '.env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS // empty' "${SETTINGS_FILE}" 2>/dev/null || echo "")

if [ "${CURRENT_VALUE}" = "1" ]; then
  echo "✅ CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS はすでに設定されています"
  exit 0
fi

# settings.jsonにenv設定を追加
TEMP_FILE=$(mktemp)
jq '.env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"' "${SETTINGS_FILE}" > "${TEMP_FILE}"
mv "${TEMP_FILE}" "${SETTINGS_FILE}"

echo "✅ CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 を ${SETTINGS_FILE} に追加しました"
echo "⚠️  Claude Code を再起動して設定を反映させてください"
