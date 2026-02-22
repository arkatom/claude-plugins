#!/bin/bash
#
# テストケースのカバレッジを検証するスクリプト
#
# 使用方法:
#   ./count_coverage.sh
#
# 出力:
#   カバレッジレポート（エンドポイント、バリデーション、UIパーツ）
#

set -euo pipefail

echo "# テストケースカバレッジレポート"
echo ""
echo "生成日時: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# docs/specs/ が存在するか確認
if [ ! -d "docs/specs" ]; then
  echo "❌ docs/specs/ が見つかりません"
  exit 1
fi

# tests/qa/ が存在するか確認
if [ ! -d "tests/qa" ]; then
  echo "❌ tests/qa/ が見つかりません"
  exit 1
fi

echo "## エンドポイントカバレッジ"
echo ""

# エンドポイント総数
total_endpoints=$(grep -rh "Route::" docs/specs/routes/*.md 2>/dev/null | wc -l | tr -d ' ')

# テストケースでカバーされているエンドポイント数
covered_endpoints=0
if ls tests/qa/exports/*.json 1> /dev/null 2>&1; then
  # 全JSONファイルからエンドポイントを抽出してユニーク化
  covered_endpoints=$(jq -s 'map(.testcases[].related.endpoint) | unique | length' tests/qa/exports/*.json 2>/dev/null || echo 0)
fi

echo "- 総エンドポイント数: $total_endpoints"
echo "- カバーされたエンドポイント: $covered_endpoints"

if [ "$total_endpoints" -gt 0 ]; then
  coverage=$((covered_endpoints * 100 / total_endpoints))
  echo "- **カバレッジ率: ${coverage}%**"

  if [ "$coverage" -ge 80 ]; then
    echo "- ✅ カバレッジ目標達成（80%以上）"
  else
    echo "- ⚠️  カバレッジ目標未達（80%未満）"
  fi
fi

echo ""
echo "## バリデーションルールカバレッジ"
echo ""

# バリデーションルール総数
total_validations=$(find docs/specs/app/requests -name "*.md" -exec grep -h "required\|email\|max\|min" {} \; 2>/dev/null | wc -l | tr -d ' ')

# カバーされたバリデーションルール数
if [ -f tests/qa/exports/*.json ]; then
  covered_validations=$(jq '[.testcases[] | select(.category=="異常系")] | length' tests/qa/exports/*.json 2>/dev/null || echo 0)
else
  covered_validations=0
fi

echo "- 総バリデーションルール数: $total_validations"
echo "- カバーされたルール: $covered_validations"

echo ""
echo "## テストケース統計"
echo ""

# テストケース総数
total_testcases=$(find tests/qa/testcases -name "TC_*.md" 2>/dev/null | wc -l | tr -d ' ')

echo "- 総テストケース数: $total_testcases"

if [ -f tests/qa/exports/*.json ]; then
  critical=$(jq '[.testcases[] | select(.priority=="Critical")] | length' tests/qa/exports/*.json 2>/dev/null || echo 0)
  high=$(jq '[.testcases[] | select(.priority=="High")] | length' tests/qa/exports/*.json 2>/dev/null || echo 0)
  medium=$(jq '[.testcases[] | select(.priority=="Medium")] | length' tests/qa/exports/*.json 2>/dev/null || echo 0)
  low=$(jq '[.testcases[] | select(.priority=="Low")] | length' tests/qa/exports/*.json 2>/dev/null || echo 0)

  echo "- 優先度別:"
  echo "  - Critical: $critical件"
  echo "  - High: $high件"
  echo "  - Medium: $medium件"
  echo "  - Low: $low件"
fi

echo ""
echo "---"
echo ""
echo "✅ カバレッジ検証完了"
