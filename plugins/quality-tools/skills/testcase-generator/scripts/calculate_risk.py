#!/usr/bin/env python3
"""
テスト観点にリスクスコアを付与し、優先度を決定するスクリプト

使用方法:
  cat extract.json | python3 calculate_risk.py > review.json

リスクスコア計算式:
  risk_score = business_impact (1-5) × user_visibility (1-3) × technical_complexity (1-3)

優先度ラベル:
  - Critical: 20以上
  - High: 10-19
  - Medium: 5-9
  - Low: 4以下

重要: 元のテストケースデータ（steps, expected_results等）を保持したまま、
リスク評価情報を追加します。
"""

import json
import sys


def calculate_risk_score(business, visibility, complexity):
    """リスクスコア = ビジネス影響度 × ユーザー可視性 × 技術複雑性"""
    return business * visibility * complexity


def assign_priority(score):
    """スコアから優先度ラベルを付与"""
    if score >= 20:
        return "Critical"
    elif score >= 10:
        return "High"
    elif score >= 5:
        return "Medium"
    else:
        return "Low"


def estimate_risk_factors(testcase):
    """
    テストケースからリスク要因を推定（汎用的なヒューリスティック）

    既に business_impact, user_visibility, technical_complexity が
    設定されている場合はそれを使用。未設定の場合のみ推定する。
    """
    category = testcase.get('category', '')
    subcategory = testcase.get('subcategory', '')
    title = testcase.get('title', '').lower()
    description = testcase.get('description', '').lower()

    # ビジネス影響度（1-5）
    business_impact = 3  # デフォルト

    if '基本フロー' in subcategory or '送信' in description or 'submit' in title:
        business_impact = 5  # フォーム送信は最重要
    elif '認証' in description or 'login' in title or 'auth' in title:
        business_impact = 5  # 認証も最重要
    elif 'メール' in description or 'mail' in title:
        business_impact = 5  # メール送信は重要
    elif '削除' in description or 'delete' in title:
        business_impact = 4  # 削除は重要
    elif category == 'セキュリティ':
        business_impact = 4  # セキュリティは重要
    elif '表示' in description or 'display' in title:
        business_impact = 2  # 表示は低め

    # ユーザー可視性（1-3）
    user_visibility = 2  # デフォルト

    if 'admin' in title or '管理' in description:
        user_visibility = 1  # 管理画面は内部のみ
    elif category == 'セキュリティ':
        user_visibility = 1  # セキュリティテストは内部処理
    elif category == '正常系':
        user_visibility = 3  # 正常系はすべてのユーザーに影響
    elif '必須' in description:
        user_visibility = 2  # バリデーションは一部のユーザーに影響
    else:
        user_visibility = 2  # その他

    # 技術複雑性（1-3）
    technical_complexity = 2  # デフォルト

    if 'メール' in description or 'mail' in title:
        technical_complexity = 3  # 外部API依存
    elif 'recaptcha' in title or 'captcha' in description:
        technical_complexity = 3  # 外部API依存
    elif 'csv' in title or 'ファイル' in description:
        technical_complexity = 2  # 中程度
    elif category == 'セキュリティ':
        technical_complexity = 3  # セキュリティテストは複雑
    elif '未入力' in title or '未選択' in title:
        technical_complexity = 1  # 単純なバリデーション
    else:
        technical_complexity = 2  # その他

    return business_impact, user_visibility, technical_complexity


def main():
    """メイン処理"""
    try:
        # stdin から extract.json を読み込み
        data = json.load(sys.stdin)

        # testcases キーまたは test_perspectives キーを探す（互換性のため）
        testcases_key = 'testcases' if 'testcases' in data else 'test_perspectives'
        testcases = data.get(testcases_key, [])

        # 各テストケースにリスクスコアと優先度を付与
        # 重要: 元のデータ（steps, expected_results等）は保持する
        for tc in testcases:
            # リスク要因を推定（または既存の値を使用）
            if 'business_impact' not in tc:
                business, visibility, complexity = estimate_risk_factors(tc)
                tc['business_impact'] = business
                tc['user_visibility'] = visibility
                tc['technical_complexity'] = complexity
            else:
                business = tc['business_impact']
                visibility = tc['user_visibility']
                complexity = tc['technical_complexity']

            # リスクスコア計算
            score = calculate_risk_score(business, visibility, complexity)
            tc['risk_score'] = score
            tc['priority'] = assign_priority(score)

        # 優先度でソート
        testcases = sorted(
            testcases,
            key=lambda x: x.get('risk_score', 0),
            reverse=True
        )
        data[testcases_key] = testcases

        # メタデータ更新
        if 'meta' not in data:
            data['meta'] = {}

        data['meta']['total_testcases'] = len(testcases)
        data['meta']['by_priority'] = {}

        for priority in ['Critical', 'High', 'Medium', 'Low']:
            count = len([tc for tc in testcases if tc.get('priority') == priority])
            data['meta']['by_priority'][priority] = count

        # 結果を出力
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
