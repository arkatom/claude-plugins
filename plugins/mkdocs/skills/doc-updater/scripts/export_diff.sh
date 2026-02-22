#!/bin/bash
# ==========================================
# 使い方
# ==========================================
# 1. 特定のディレクトリだけを対象にする
# # srcディレクトリのみ
# ./export_diff.sh src/
# # src と public の2つ
# ./export_diff.sh src/ public/

# 2. 特定の拡張子だけを対象にする
# # TypeScriptファイル (*.ts) だけ
# ./export_diff.sh "*.ts"
# # srcディレクトリの中の *.tsx だけ
# ./export_diff.sh "src/*.tsx"

# 3. 除外ファイルを指定する (-e または --exclude)
# # testディレクトリを除外したい
# ./export_diff.sh -e "test/"
# # markdownファイルとスペックファイルを除外
# ./export_diff.sh -e "*.md" -e "*.spec.ts"

# 4. 複合技（よくあるパターン）
# # 1週間前からの変更で、src ディレクトリ以下を見たいが、*.test.ts はノイズだから消したい
# ./export_diff.sh -week src/ -e "*.test.ts"


# ==========================================
# デフォルト設定
# ==========================================
OUTPUT_FILE="ai_context.diff"
CONTEXT_LINES=1   # 上下のコンテキスト行数
TIME_UNIT="day"
TIME_VALUE="1"

# ベースとなる除外リスト（常に除外したいゴミファイル）
# 配列で管理して可読性を確保
DEFAULT_EXCLUDES=(
    ':(exclude)package-lock.json'
    ':(exclude)yarn.lock'
    ':(exclude)pnpm-lock.yaml'
    ':(exclude)composer.lock'
    ':(exclude)Gemfile.lock'
    ':(exclude)vendor/'
    ':(exclude)node_modules/'
    ':(exclude)dist/'
    ':(exclude)build/'
    ':(exclude).next/'
    ':(exclude).nuxt/'
    ':(exclude).output/'
    ':(exclude).DS_Store'
    ':(exclude)*.min.js'
    ':(exclude)*.min.css'
    ':(exclude)*.map'
    ':(exclude)*.svg'
    ':(exclude)*.png'
    ':(exclude)*.jpg'
    ':(exclude)*.jpeg'
    ':(exclude)*.gif'
    ':(exclude)*.webp'
    ':(exclude)*.ico'
    ':(exclude)*.woff'
    ':(exclude)*.woff2'
    ':(exclude)*.ttf'
)

# ユーザー指定用の配列初期化
USER_EXCLUDES=()
TARGET_PATHS=()

# ==========================================
# 引数解析ロジック
# ==========================================

while [[ $# -gt 0 ]]; do
    case "$1" in
        # --- 時間指定 ---
        -d|-day|-days)
            TIME_UNIT="day"
            if [[ "$2" =~ ^[0-9]+$ ]]; then TIME_VALUE="$2"; shift; else TIME_VALUE="1"; fi
            ;;
        -w|-week|-weeks)
            TIME_UNIT="week"
            if [[ "$2" =~ ^[0-9]+$ ]]; then TIME_VALUE="$2"; shift; else TIME_VALUE="1"; fi
            ;;
        -m|-month|-months)
            TIME_UNIT="month"
            if [[ "$2" =~ ^[0-9]+$ ]]; then TIME_VALUE="$2"; shift; else TIME_VALUE="1"; fi
            ;;

        # --- 除外指定 (-e "test/" や -e "*.log") ---
        -e|-exclude|--exclude)
            if [ -n "$2" ]; then
                # Gitのpathspec形式に変換して追加
                USER_EXCLUDES+=(":(exclude)$2")
                shift
            fi
            ;;

        # --- 対象指定 (-t "src/" や -t "*.ts") ---
        # ※ フラグなしで末尾に書いても認識されるように後述の *) で処理するが、
        #    明示的に指定したい場合用
        -t|-target|--target|-i|-include)
            if [ -n "$2" ]; then
                TARGET_PATHS+=("$2")
                shift
            fi
            ;;

        # --- その他のオプション ---
        -o|--output) # 出力ファイル名変更
            if [ -n "$2" ]; then OUTPUT_FILE="$2"; shift; fi
            ;;

        *)
            # ハイフンで始まらない引数は「対象パス」として扱う
            # 例: ./script.sh src/ components/
            TARGET_PATHS+=("$1")
            ;;
    esac
    shift
done

# 対象パスが指定されていなければ、デフォルトはカレントディレクトリ (.)
if [ ${#TARGET_PATHS[@]} -eq 0 ]; then
    TARGET_PATHS=(".")
fi

# SINCE_WHEN の組み立て
SINCE_WHEN="$TIME_VALUE $TIME_UNIT ago"

# ==========================================
# 前準備
# ==========================================
set -e

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "エラー: Gitリポジトリ内ではありません。"
    exit 1
fi

START_COMMIT=$(git rev-list -n 1 --before="$SINCE_WHEN" HEAD)
if [ -z "$START_COMMIT" ]; then
    echo "警告: 履歴が見つかりません。最初のコミットから取得します。"
    START_COMMIT=$(git rev-list --max-parents=0 HEAD)
fi

echo "--------------------------------------------------"
echo " 対象期間: $SINCE_WHEN ($TIME_VALUE $TIME_UNIT)"
echo " 対象パス: ${TARGET_PATHS[*]}"
if [ ${#USER_EXCLUDES[@]} -gt 0 ]; then
    echo " 追加除外: ${USER_EXCLUDES[*]}"
fi
echo " 出力先: $OUTPUT_FILE"
echo "--------------------------------------------------"

# ==========================================
# 出力実行
# ==========================================

(
  echo "CONTEXT: PROMPT FOR AI"
  echo "Target Period: Since $SINCE_WHEN"
  echo "Target Paths: ${TARGET_PATHS[*]}"
  echo "Generated: $(date)"
  echo ""

  echo "=== PART 1: COMMIT LOGS (INTENT) ==="
  echo "What changed & WHY:"
  # ログも対象パスに絞ることで、関係ないログを出さないようにする
  git log --no-merges --since="$SINCE_WHEN" --format="- [%h] %s (%cd)" --date=short -- "${TARGET_PATHS[@]}"

  echo ""
  echo "=== PART 2: CODE DIFFS (DETAILS) ==="
  echo "Context: $CONTEXT_LINES lines | Whitespace ignored"

  # Diffコマンド組み立て
  # 1. 期間 ($START_COMMIT HEAD)
  # 2. パス区切り (--)
  # 3. 対象パス (${TARGET_PATHS[@]})
  # 4. デフォルト除外 (${DEFAULT_EXCLUDES[@]})
  # 5. ユーザー除外 (${USER_EXCLUDES[@]})

  git diff -w -U"$CONTEXT_LINES" "$START_COMMIT" HEAD -- \
    "${TARGET_PATHS[@]}" \
    "${DEFAULT_EXCLUDES[@]}" \
    "${USER_EXCLUDES[@]}"

) > "$OUTPUT_FILE"

echo "完了! '$OUTPUT_FILE' が生成されました。"
