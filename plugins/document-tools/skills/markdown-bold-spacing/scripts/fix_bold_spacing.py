#!/usr/bin/env python3
import re
import sys


def fix_bold_spacing(text):
    """
    Markdownの**強調**の前後に適切なスペースを追加する。

    修正するケース：
    - 文中で前後に日本語文字がある場合

    修正しないケース：
    - 行頭の **
    - # の直後の **
    - * の直後の ** (リスト項目)
    - - の直後の ** (リスト項目)
    - 数字+ピリオドの直後の ** (番号付きリスト)
    - ( の直後の **
    - **の直後に : がある場合 (**キー:** の形式)
    - **の後ろが ← などの特殊記号の場合
    """

    lines = text.split('\n')
    result_lines = []

    for line in lines:
        original_line = line

        # 行の先頭部分を確認
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]

        # 行頭の **、#の後の **、リスト項目の ** は処理しない
        if stripped.startswith('**') or \
           stripped.startswith('#') or \
           re.match(r'^\d+\.\s+\*\*', stripped) or \
           re.match(r'^\*\s+\*\*', stripped) or \
           re.match(r'^-\s+\*\*', stripped):
            # この行は処理しない
            result_lines.append(line)
            continue

        # パターン1: 日本語文字 + ** の間にスペースを追加
        # ただし、**の直後に:がある場合は除外（**キー:** の形式）
        line = re.sub(
            r'([ぁ-んァ-ヶー一-龥])\*\*(?!:)',
            r'\1 **',
            line
        )

        # パターン2: ** + 日本語文字 の間にスペースを追加
        # ただし、直前が:の場合は除外
        # また、後ろが特殊記号（←など）の場合も除外
        line = re.sub(
            r'(?<!:)\*\*([ぁ-んァ-ヶー一-龥])(?!←)',
            r'** \1',
            line
        )

        result_lines.append(line)

    return '\n'.join(result_lines)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            content = f.read()
        result = fix_bold_spacing(content)
        print(result, end='')
    else:
        content = sys.stdin.read()
        result = fix_bold_spacing(content)
        print(result, end='')
