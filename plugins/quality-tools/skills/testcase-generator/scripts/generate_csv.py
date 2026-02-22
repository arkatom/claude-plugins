#!/usr/bin/env python3
"""
review.json から CSV 形式のテストケースを生成するスクリプト
1ステップ = 1行の実務的なフォーマット

使用方法:
  cat review.json | python3 generate_csv.py > testcases.csv

出力形式:
  - 1テストケース × Nステップ = N行
  - UTF-8 BOM付き（Excelで開ける）
  - QAツールにインポート可能

列構成:
  テストケースID | ステップ番号 | 優先度 | リスクスコア | カテゴリ | サブカテゴリ |
  タイトル | 前提 | 操作 | 期待挙動 | 結果 | 実施日 | 実施者 | 備考
"""

import json
import csv
import sys
from io import StringIO


def extract_preconditions(testcase):
    """
    前提条件を抽出（具体的な条件のみ）

    原則: 「システムが正常に稼働している」のような一般的すぎる条件は記載しない。
    テスト固有の前提条件のみを記載する。
    """
    preconditions = []

    # 明示的な前提条件があればそれを使用
    if 'preconditions' in testcase and testcase['preconditions']:
        if isinstance(testcase['preconditions'], list):
            return '\n'.join(testcase['preconditions'])
        else:
            return testcase['preconditions']

    # テストケースの内容から具体的な前提条件を推定
    title = testcase.get('title', '')
    description = testcase.get('description', '')
    category = testcase.get('category', '')
    subcategory = testcase.get('subcategory', '')

    # セミナー申込・お問い合わせフォーム関連
    if '送信' in description or '完了' in description or 'メール' in title:
        preconditions.append('説明会日程CSVファイルに有効な日程が登録されている')

    # reCAPTCHA関連
    if 'recaptcha' in title.lower() or 'captcha' in description.lower():
        preconditions.append('reCAPTCHAが有効である（NOCAPTCHA_SECRET設定済み）')

    # 認証関連
    if 'ログイン' in title or '認証' in description:
        preconditions.append('ユーザーがログアウト状態である')
    elif 'ログアウト' in title:
        preconditions.append('ユーザーがログイン済みである')

    # 管理画面関連
    if 'admin' in title.lower() or '管理画面' in description:
        preconditions.append('管理者としてログイン済みである')

    # CSVファイル関連
    if 'CSV' in title or 'csv' in description:
        if '空' in title or '存在しない' in title:
            pass  # 意図的に空または削除するテストなので前提不要
        else:
            preconditions.append('説明会日程CSVファイルが存在する')

    # 日程フィルタリング関連
    if '4日前' in description or '日程' in title and 'フィルタ' in subcategory:
        preconditions.append('説明会日程CSVファイルに過去・現在・未来の日程が含まれている')

    # 前提条件がない場合は空文字（一般的な条件は書かない）
    return '\n'.join(preconditions) if preconditions else ''


def main():
    """メイン処理"""
    try:
        # stdin から review.json を読み込み
        data = json.load(sys.stdin)

        # testcases キーまたは test_perspectives キーを探す（互換性のため）
        testcases_key = 'testcases' if 'testcases' in data else 'test_perspectives'
        testcases = data.get(testcases_key, [])

        # CSV出力用のバッファ
        output = StringIO()
        writer = csv.writer(output)

        # ヘッダー行
        headers = [
            'テストケースID', 'ステップ番号', '優先度', 'リスクスコア',
            'カテゴリ', 'サブカテゴリ', 'タイトル', '前提', '操作', '期待挙動',
            '結果', '実施日', '実施者', '備考'
        ]

        writer.writerow(headers)

        # 各テストケース（1ステップ=1行）
        for tc in testcases:
            tc_id = tc.get('id', '')
            priority = tc.get('priority', '')
            risk_score = tc.get('risk_score', 0)
            category = tc.get('category', '')
            subcategory = tc.get('subcategory', '')
            title = tc.get('title', '')

            # 前提条件（最初のステップのみ）
            preconditions = extract_preconditions(tc)

            # ステップと期待結果を取得
            steps = tc.get('steps', [])
            expected_results = tc.get('expected_results', [])

            # ステップがない場合は1行だけ出力（サマリー行）
            if not steps:
                steps = ['（テストステップ未定義）']
                expected_results = ['（期待結果未定義）']

            # 各ステップを1行ずつ出力
            for step_num, (step, expected) in enumerate(zip(steps, expected_results), 1):
                row = [
                    tc_id,                                    # テストケースID
                    step_num,                                 # ステップ番号
                    priority,                                 # 優先度
                    risk_score,                               # リスクスコア
                    category,                                 # カテゴリ
                    subcategory,                              # サブカテゴリ
                    title,                                    # タイトル
                    preconditions if step_num == 1 else '-',  # 前提（最初のステップのみ）
                    step,                                     # 操作
                    expected,                                 # 期待挙動
                    '',                                       # 結果（空欄）
                    '',                                       # 実施日
                    '',                                       # 実施者
                    ''                                        # 備考
                ]

                writer.writerow(row)

        # UTF-8 BOM付きで出力（Excelでの文字化け防止）
        print('\ufeff' + output.getvalue(), end='')

        # 統計情報を出力（stderr）
        total_steps = sum(len(tc.get('steps', [])) for tc in testcases)
        print(f"✅ CSVファイルを生成しました", file=sys.stderr)
        print(f"   - 総テストケース数: {len(testcases)}件", file=sys.stderr)
        print(f"   - 総ステップ数: {total_steps}行", file=sys.stderr)
        print(f"   - フォーマット: 1ステップ=1行（実務標準）", file=sys.stderr)
        print(f"   - エンコーディング: UTF-8 BOM付き（Excel対応）", file=sys.stderr)

    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
