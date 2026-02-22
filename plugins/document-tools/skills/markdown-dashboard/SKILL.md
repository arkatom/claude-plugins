---
name: markdown-dashboard
description: "複数のMarkdownファイルを美しく安全な単一HTMLダッシュボードに変換する。検索・ナビゲーション・フィルタリング機能付き。"
---

## 目的

技術ドキュメント、プロジェクトマニュアル、レポートなど、Markdownファイル群をプロフェッショナルなWebダッシュボードとして統合し、検索・ナビゲーション・フィルタリング機能付きで提供する。

## 使用方法

### 単一ディレクトリ

```bash
/markdown-dashboard <target_directory>

# 例
/markdown-dashboard docs/reports
/markdown-dashboard docs/specs
```

### 複数ディレクトリ統合（タブ型ナビゲーション）

```bash
/markdown-dashboard <dir1> <dir2> [<dir3> ...]

# 例
/markdown-dashboard docs/api docs/guides docs/changelog
```

**ディレクトリ名の自動判別**: パスから2階層上のディレクトリ名を使用

- 例: `project-a/docs/reports` → タブ名: `project-a`

## 出力

- **単一ディレクトリ**: `<target_directory>/index.html`
- **複数ディレクトリ**: 最初の引数ディレクトリに `index.html`

完全に自己完結した単一HTMLファイル（外部依存ゼロ、オフライン動作）

### 機能

- タブ型ナビゲーション（複数ディレクトリ時）
- サイドバーナビゲーション（階層的）
- ダークモード切替（LocalStorage保存）
- メタデータテーブル自動生成（YAMLフロントマターから）
- Markdownテーブルの自動HTML変換
- シンタックスハイライト（PHP, JavaScript, Python, SQL, Bash等）
- スムーズスクロール
- レスポンシブ（モバイル対応）
- XSS対策（完全サニタイズ）

### デザイン

- ビジネスプロフェッショナル（青系基調 `#2563eb`）
- WCAG AA準拠
- レスポンシブ（モバイル対応）

## Claude（エージェント）への実装手順

以下のコマンドを**1回実行するだけ**：

**単一ディレクトリ**：

```bash
python3 <plugin_root>/scripts/generate_dashboard.py <target_directory> > <target_directory>/index.html
```

**複数ディレクトリ統合**：

```bash
python3 <plugin_root>/scripts/generate_dashboard.py <dir1> <dir2> <dir3> > <dir1>/index.html
```

> **注意**: `<plugin_root>` はこのスキルのスクリプトディレクトリを指す。プラグインインストール後は `~/.claude/plugins/cache/arkatom-plugins/document-tools/` 配下にある。プロジェクトローカルインストール時は `.claude/skills/markdown-dashboard/` となる。

### 内部動作

1. `scripts/generate_dashboard.py` が：
   - 全ディレクトリから全.mdファイルを読み込み
   - 各ファイルにディレクトリ情報を付与（パスから2階層上のディレクトリ名）
   - データをJSON化（ensure_ascii=False で自然な形式）
   - `templates/dashboard_template.html` にデータを埋め込み
   - 完成したHTMLを標準出力

2. 出力を `> <first_directory>/index.html` にリダイレクト

3. ブラウザ上でHTMLを開く

## セキュリティ対策

- `<script>` タグを `&lt;script&gt;` にエスケープ
- `javascript:` プロトコルを無効化
- すべてのHTML要素を適切にサニタイズ
- CSP準拠

## 制約

- ファイルサイズ: 500KB以下推奨
- ブラウザ: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- アクセシビリティ: WCAG AA準拠
