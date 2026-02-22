#!/bin/bash
#
# docs/specs/app/requests/ から全バリデーションルールを抽出するスクリプト
#
# 使用方法:
#   ./extract_validations.sh [docs/specs]
#
# 出力:
#   バリデーションルール一覧（1行1ルール）
#   形式: フィールド名|ルール種別|パラメータ
#

set -euo pipefail

DOCS_DIR="${1:-docs/specs}"

if [ ! -d "$DOCS_DIR/app/requests" ]; then
  echo "エラー: $DOCS_DIR/app/requests/ が見つかりません" >&2
  exit 1
fi

echo "# バリデーションルール一覧" >&2
echo "" >&2

# requests/*.md からバリデーションルールを抽出
find "$DOCS_DIR/app/requests" -name "*.md" -type f | while read -r file; do
  echo "## $(basename "$file" .md)" >&2

  # 表形式のバリデーションルールを抽出
  grep -E "^\| .* \| .* \|" "$file" | \
    grep -v "^| \-\-" | \
    grep -v "| フィールド名 |" | \
    grep -E "required|email|max|min|regex|numeric|date|string|integer|boolean|array" | \
    sed 's/^| //g' | sed 's/ |$//g' | \
    sed 's/ | /|/g'

  echo "" >&2
done

# カスタムルールも抽出
if [ -d "$DOCS_DIR/app/rules" ]; then
  echo "## カスタムルール" >&2

  find "$DOCS_DIR/app/rules" -name "*.md" -type f -exec basename {} .md \; | \
    while read -r rule; do
      echo "$rule|custom|"
    done

  echo "" >&2
fi

echo "✅ バリデーションルール抽出完了" >&2
