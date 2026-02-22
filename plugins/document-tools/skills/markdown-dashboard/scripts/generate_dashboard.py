#!/usr/bin/env python3
"""
Markdown Dashboard Generator

指定ディレクトリ内の全マークダウンファイルを収集し、
HTMLテンプレートに埋め込んで単一HTMLダッシュボードを生成する。

複数ディレクトリ指定時は、タブ型ナビゲーションで切り替え可能な統合ダッシュボードを生成する。
"""

import json
import sys
from pathlib import Path

def get_repository_name(path):
    """パスから2階層上のディレクトリ名を取得してリポジトリ名とする"""
    parts = Path(path).resolve().parts
    if len(parts) >= 3:
        return parts[-3]  # 2階層上
    elif len(parts) >= 2:
        return parts[-2]  # 1階層上
    else:
        return parts[-1]  # ディレクトリ名そのまま

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_dashboard.py <target_directory> [<dir2> <dir3> ...]", file=sys.stderr)
        sys.exit(1)

    # 対象ディレクトリ（複数可）
    target_dirs = [Path(arg) for arg in sys.argv[1:]]

    # 存在確認
    for dir_path in target_dirs:
        if not dir_path.exists():
            print(f"Error: Directory {dir_path} does not exist", file=sys.stderr)
            sys.exit(1)

    # Step 1: 全マークダウンファイルを収集（複数ディレクトリ対応）
    documents = []
    all_repositories = []

    for base_dir in target_dirs:
        repo_name = get_repository_name(base_dir)
        all_repositories.append(repo_name)

        for md_file in sorted(base_dir.rglob('*.md')):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    documents.append({
                        'filename': md_file.name,
                        'path': str(md_file.relative_to(base_dir)),
                        'content': f.read(),
                        'repository': repo_name  # リポジトリ情報を追加
                    })
            except Exception as e:
                print(f"Warning: Failed to read {md_file}: {e}", file=sys.stderr)

    # Step 2: vulnerabilities.jsonを読み込み（複数ディレクトリ対応）
    all_vulnerabilities = []
    total_stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    for base_dir in target_dirs:
        repo_name = get_repository_name(base_dir)
        vuln_json_path = base_dir / 'data' / 'vulnerabilities.json'

        if vuln_json_path.exists():
            with open(vuln_json_path, 'r', encoding='utf-8') as f:
                vuln_data = json.load(f)
                # 各脆弱性にリポジトリ情報を追加
                for vuln in vuln_data.get('vulnerabilities', []):
                    vuln['repository'] = repo_name
                    all_vulnerabilities.append(vuln)
                # 統計を集計
                for severity, count in vuln_data.get('metadata', {}).get('by_severity', {}).items():
                    total_stats[severity] = total_stats.get(severity, 0) + count
        else:
            print(f"Warning: {vuln_json_path} not found", file=sys.stderr)

    # 統合されたvulnerabilities.jsonデータ
    vuln_data = {
        "metadata": {
            "total_vulnerabilities": len(all_vulnerabilities),
            "by_severity": total_stats,
            "repositories": all_repositories
        },
        "vulnerabilities": all_vulnerabilities
    }

    # Step 3: テンプレートファイルを読み込み
    template_path = Path(__file__).parent.parent / 'templates' / 'dashboard_template.html'

    if not template_path.exists():
        print(f"Error: Template {template_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(template_path, 'r', encoding='utf-8') as f:
        template_html = f.read()

    # Step 3.5: テンプレートの破損をチェックして修正
    # const MARKDOWN_DOCUMENTS の行が既にデータを含んでいる場合、初期値にリセット
    import re
    # 568行目を探して、正しい初期値に置き換える
    lines = template_html.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('const MARKDOWN_DOCUMENTS = ') and len(line) > 100:
            lines[i] = 'const MARKDOWN_DOCUMENTS = [];'
            print(f"Warning: Fixed corrupted template at line {i+1}", file=sys.stderr)
            break
    template_html = '\n'.join(lines)

    # Step 4: データをJSON形式に変換
    # ensure_ascii=False を使用（<script type="application/json"> 内なのでエスケープ不要）
    md_json = json.dumps(documents, ensure_ascii=False, separators=(',', ':'), indent=None)
    vuln_json = json.dumps(vuln_data, ensure_ascii=False, separators=(',', ':'), indent=None)

    # Step 4.5: HTML内のJSON用に </script> タグをエスケープ
    md_json = md_json.replace('</script>', '<\\/script>')
    vuln_json = vuln_json.replace('</script>', '<\\/script>')

    # Step 5: テンプレートにデータを埋め込み
    final_html = template_html.replace(
        '<script type="application/json" id="markdown-data">[]</script>',
        f'<script type="application/json" id="markdown-data">{md_json}</script>'
    ).replace(
        '<script type="application/json" id="vuln-data">{"metadata":{"total_vulnerabilities":0,"by_severity":{"critical":0,"high":0,"medium":0,"low":0}},"vulnerabilities":[]}</script>',
        f'<script type="application/json" id="vuln-data">{vuln_json}</script>'
    )

    # Step 6: 結果を標準出力
    print(final_html)

if __name__ == '__main__':
    main()
