#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
スタイル変換関数モジュール

A型（ビジネス文書）、B型（技術仕様書）、H型（ハイブリッド）の
3つのスタイル間で文書を変換する。
"""

import re


def format_business_style(text):
    """
    A型（ビジネス文書スタイル）に変換

    - 敬語表現に変換
    - 物語的な記述

    Args:
        text: 変換対象のテキスト

    Returns:
        str: A型に変換されたテキスト
    """
    if not text:
        return text

    # 敬語変換
    conversions = [
        (r'します(?![ょう])', 'いたします'),  # 「します」→「いたします」（「しますよう」は除外）
        (r'する(?![\u3040-\u309F])', 'いたす'),  # 「する」→「いたす」（ひらがなが続く場合は除外）
        (r'([^お])社員', r'\1社員様'),  # 「社員」→「社員様」
        (r'担当者', '担当者様'),  # 「担当者」→「担当者様」
        (r'指導者', '指導者様'),  # 「指導者」→「指導者様」
        (r'ユーザー', 'ユーザー様'),  # 「ユーザー」→「ユーザー様」
        (r'行います', '実施いたします'),  # 「行います」→「実施いたします」
        (r'送信します', '送信いたします'),  # 「送信します」→「送信いたします」
        (r'取得します', '取得いたします'),  # 「取得します」→「取得いたします」
        (r'更新します', '更新いたします'),  # 「更新します」→「更新いたします」
        (r'登録します', '登録いたします'),  # 「登録します」→「登録いたします」
        (r'削除します', '削除いたします'),  # 「削除します」→「削除いたします」
        (r'作成します', '作成いたします'),  # 「作成します」→「作成いたします」
        (r'実行します', '実行いたします'),  # 「実行します」→「実行いたします」
        (r'処理します', '処理いたします'),  # 「処理します」→「処理いたします」
        (r'変更します', '変更いたします'),  # 「変更します」→「変更いたします」
        (r'確認します', '確認いたします'),  # 「確認します」→「確認いたします」
    ]

    result = text
    for pattern, replacement in conversions:
        result = re.sub(pattern, replacement, result)

    return result


def format_technical_style(text):
    """
    B型（技術仕様書スタイル）に変換

    - 簡潔な表現
    - 構造化された記述
    - 敬語を削除

    Args:
        text: 変換対象のテキスト

    Returns:
        str: B型に変換されたテキスト
    """
    if not text:
        return text

    # 敬語を簡潔な表現に変換
    conversions = [
        (r'いたします', 'します'),  # 「いたします」→「します」
        (r'実施いたします', '行います'),  # 「実施いたします」→「行います」
        (r'送信いたします', '送信します'),  # 「送信いたします」→「送信します」
        (r'取得いたします', '取得します'),  # 「取得いたします」→「取得します」
        (r'更新いたします', '更新します'),  # 「更新いたします」→「更新します」
        (r'登録いたします', '登録します'),  # 「登録いたします」→「登録します」
        (r'削除いたします', '削除します'),  # 「削除いたします」→「削除します」
        (r'作成いたします', '作成します'),  # 「作成いたします」→「作成します」
        (r'実行いたします', '実行します'),  # 「実行いたします」→「実行します」
        (r'処理いたします', '処理します'),  # 「処理いたします」→「処理します」
        (r'変更いたします', '変更します'),  # 「変更いたします」→「変更します」
        (r'確認いたします', '確認します'),  # 「確認いたします」→「確認します」
        (r'ございます', 'です'),  # 「ございます」→「です」
        (r'様', ''),  # 「様」を削除
    ]

    result = text
    for pattern, replacement in conversions:
        result = re.sub(pattern, replacement, result)

    return result


def format_hybrid_style(text):
    """
    H型（ハイブリッドスタイル）に変換

    - A型の敬語表現 + B型の構造化
    - 空行削除、段落内改行は保持
    - テーブル名を（括弧）内に記載

    Args:
        text: 変換対象のテキスト

    Returns:
        str: H型に変換されたテキスト
    """
    if not text:
        return text

    # まずA型の敬語変換を適用
    result = format_business_style(text)

    # 空行（連続する改行）を削除
    # 2つ以上の連続する改行を1つの改行に置き換え
    result = re.sub(r'\n\n+', '\n', result)

    # 行頭・行末の空白を削除
    result = result.strip()

    return result


def convert_to_structured_format(text, style='B'):
    """
    テキストを構造化フォーマットに変換

    Args:
        text: 変換対象のテキスト
        style: スタイル ('A', 'B', 'H')

    Returns:
        str: 構造化されたテキスト
    """
    if not text:
        return text

    if style == 'A':
        return format_business_style(text)
    elif style == 'B':
        return format_technical_style(text)
    elif style == 'H':
        return format_hybrid_style(text)
    else:
        # デフォルトはB型
        return format_technical_style(text)


# テスト用のサンプル
if __name__ == '__main__':
    sample_text = """LIL社員が作成した指導者宛てのメールを一斉配信します。
配信対象メール取得：mail_detail テーブルから配信予約済みメールを取得
配信先リスト取得：mail_history テーブルから配信先を取得
メール送信処理：各教室の指導者にメール送信
ステータス更新：送信成功(3)、送信失敗(4)、配信完了(2)
送信報告メール：送信結果を事務局にメール送信"""

    print("=== 元のテキスト ===")
    print(sample_text)
    print()

    print("=== A型（ビジネス文書スタイル） ===")
    print(format_business_style(sample_text))
    print()

    print("=== B型（技術仕様書スタイル） ===")
    print(format_technical_style(sample_text))
    print()

    print("=== H型（ハイブリッドスタイル） ===")
    print(format_hybrid_style(sample_text))
    print()
