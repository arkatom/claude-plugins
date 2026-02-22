#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel生成Skill - メインエントリーポイント

SKILL.mdの手順に従って、Markdownドキュメントまたはコードベースから
Excel形式のドキュメントを生成する。

使用方法:
    python main.py --source cron-jobs.md --output output.xlsx --style B [--sample sample.xlsx]
"""

import argparse
import sys
import os

# 同じディレクトリのモジュールをインポート
from analyze_sample import analyze_sample_excel
from style_converter import convert_to_structured_format
from excel_generator import create_excel_with_template, create_excel_default


def parse_markdown_table(md_content):
    """
    Markdownのテーブルをパースしてデータ行のリストを返す

    Args:
        md_content: Markdownファイルの内容

    Returns:
        list: データ行のリスト
    """
    lines = md_content.split('\n')
    data_rows = []
    headers = []
    in_table = False
    separator_found = False

    for line in lines:
        stripped_line = line.strip()

        # 空行はスキップ
        if not stripped_line:
            if in_table:
                in_table = False
                separator_found = False
            continue

        # テーブル行（|を含む）を検出
        if '|' in stripped_line:
            # パイプで分割
            parts = [p.strip() for p in stripped_line.split('|')]
            # 最初と最後の空要素を除去
            parts = [p for p in parts if p or parts.index(p) not in [0, len(parts)-1]]

            if not in_table:
                # テーブルの開始 - ヘッダー行
                headers = parts
                in_table = True
                separator_found = False
            elif not separator_found:
                # 区切り行（-----|-----）を検出
                if all('-' in p for p in parts):
                    separator_found = True
                else:
                    # 区切り行でない場合はデータ行として扱う
                    if len(parts) == len(headers):
                        row_dict = {headers[i]: parts[i] for i in range(len(headers))}
                        data_rows.append(row_dict)
            else:
                # データ行
                if len(parts) == len(headers):
                    row_dict = {headers[i]: parts[i] for i in range(len(headers))}
                    data_rows.append(row_dict)
        elif in_table:
            # テーブルの終了
            in_table = False
            separator_found = False

    return data_rows


def extract_cron_data_from_markdown(md_path):
    """
    cron-jobs.mdからCron処理データを抽出

    Args:
        md_path: Markdownファイルのパス

    Returns:
        list: Cron処理データのリスト
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Markdownのテーブルをパース
    data_rows = parse_markdown_table(content)

    return data_rows


def apply_style_conversion(data_rows, style):
    """
    データ行にスタイル変換を適用

    Args:
        data_rows: データ行のリスト
        style: スタイル ('A', 'B', 'H')

    Returns:
        list: スタイル変換されたデータ行
    """
    converted_rows = []

    for row in data_rows:
        converted_row = {}
        for key, value in row.items():
            # テキストフィールドにスタイル変換を適用
            if isinstance(value, str) and len(value) > 20:  # 長いテキストのみ
                converted_row[key] = convert_to_structured_format(value, style)
            else:
                converted_row[key] = value
        converted_rows.append(converted_row)

    return converted_rows


def generate_excel(source_path, output_path, style='B', sample_path=None):
    """
    Excelファイルを生成（メイン関数）

    Args:
        source_path: ソースMarkdownファイルのパス
        output_path: 出力Excelファイルのパス
        style: スタイル ('A', 'B', 'H')
        sample_path: サンプルExcelファイルのパス（オプション）

    Returns:
        bool: 成功した場合True
    """
    try:
        # Step 1: ソースデータを抽出
        print(f"ソースMarkdownを読み込み中: {source_path}")
        data_rows = extract_cron_data_from_markdown(source_path)
        print(f"  データ行数: {len(data_rows)}")

        if not data_rows:
            print("エラー: データが見つかりませんでした")
            return False

        # Step 2: スタイル変換を適用
        print(f"スタイル変換を適用中: {style}型")
        converted_data = apply_style_conversion(data_rows, style)

        # Step 3: Excelを生成
        if sample_path and os.path.exists(sample_path):
            print(f"サンプルExcelを解析中: {sample_path}")
            template_info = analyze_sample_excel(sample_path)
            print("  サンプルの体裁を使用してExcelを生成中...")

            # シート名を取得（テンプレートの最初のシート名を使用）
            sheet_name = template_info['sheets'][0]['name'] if template_info['sheets'] else 'Sheet1'

            wb = create_excel_with_template(converted_data, template_info, sheet_name)
        else:
            print("デフォルト体裁でExcelを生成中...")
            # ソースファイル名からシート名を推測
            base_name = os.path.splitext(os.path.basename(source_path))[0]
            sheet_name = base_name if base_name else 'Sheet1'

            wb = create_excel_default(converted_data, sheet_name, style)

        # Step 4: ファイルを保存
        print(f"Excelファイルを保存中: {output_path}")
        wb.save(output_path)
        print(f"✅ 完了: {output_path}")

        return True

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """コマンドライン実行のエントリーポイント"""
    parser = argparse.ArgumentParser(
        description='Excel生成Skill - Markdownから高品質なExcelドキュメントを生成'
    )

    parser.add_argument(
        '--source',
        required=True,
        help='ソースMarkdownファイルのパス'
    )

    parser.add_argument(
        '--output',
        required=True,
        help='出力Excelファイルのパス'
    )

    parser.add_argument(
        '--style',
        choices=['A', 'B', 'H'],
        default='B',
        help='スタイル: A=ビジネス文書, B=技術仕様書, H=ハイブリッド (デフォルト: B)'
    )

    parser.add_argument(
        '--sample',
        default=None,
        help='サンプルExcelファイルのパス（オプション）'
    )

    args = parser.parse_args()

    # 引数の検証
    if not os.path.exists(args.source):
        print(f"エラー: ソースファイルが見つかりません: {args.source}")
        sys.exit(1)

    if args.sample and not os.path.exists(args.sample):
        print(f"警告: サンプルファイルが見つかりません: {args.sample}")
        print("デフォルト体裁を使用します")
        args.sample = None

    # Excel生成を実行
    success = generate_excel(
        source_path=args.source,
        output_path=args.output,
        style=args.style,
        sample_path=args.sample
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
