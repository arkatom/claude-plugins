#!/bin/bash
#
# docs/specs/routes/ から全エンドポイントを抽出するスクリプト
#
# 使用方法:
#   ./extract_routes.sh [docs/specs]
#
# 出力:
#   エンドポイント一覧（1行1エンドポイント）
#   形式: メソッド|パス|コントローラー|説明
#

set -euo pipefail

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

DOCS_DIR="${1:-$PROJECT_ROOT/docs/specs}"

if [ ! -d "$DOCS_DIR/routes" ]; then
  echo "エラー: $DOCS_DIR/routes/ が見つかりません" >&2
  exit 1
fi

echo "# エンドポイント一覧" >&2
echo "" >&2

# routes/overview.md から表形式のエンドポイントを抽出
if [ -f "$DOCS_DIR/routes/overview.md" ]; then
  grep -E "^\| .* \| .* \|" "$DOCS_DIR/routes/overview.md" | \
    grep -v "^| \-\-" | \
    grep -v "| メソッド |" | \
    sed 's/^| //g' | sed 's/ |$//g' | \
    sed 's/ | /|/g'
fi

# routes/*.md から Route:: 定義を抽出（バックアップ）
find "$DOCS_DIR/routes" -name "*.md" -type f -exec grep -h "Route::" {} \; 2>/dev/null | \
  sed "s/Route:://" | \
  sed "s/[('\"]/ /g" | \
  awk '{print $1"|"$2}' | \
  sort -u

echo "" >&2
echo "✅ エンドポイント抽出完了" >&2
