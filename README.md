# arkatom/claude-plugins

arkatom の Claude Code プラグイン集。ドキュメント生成・開発ワークフロー・品質管理など、日常的な開発支援スキル・エージェント・フックを提供します。

## インストール

```bash
# マーケットプレイスを追加
/plugin marketplace add arkatom/claude-plugins

# プラグインをインストール（例）
/plugin install mkdocs@arkatom-plugins
/plugin install dev-workflow@arkatom-plugins
```

## プラグイン一覧

| プラグイン | 内容 |
|-----------|------|
| `mkdocs` | 7フェーズドキュメント生成ワークフロー |
| `dev-workflow` | commit/worktree/codex/research スキル + Bash/Grep フック |
| `document-tools` | Markdown ダッシュボード・Excel 生成・日本語太字スペース修正 |
| `quality-tools` | セキュリティ監査・E2E テストケース自動生成 |
| `reflection` | セッション振り返りスキル |
| `team` | 4 メンバーチーム協働（PM/Coder/Reviewer/Devil） |
| `security-guard` | 認証情報・APIキー・PEM 鍵漏洩を自動検出・ブロック |
| `session-hooks` | セッション開始記録・git 状態チェックフック |
| `core-instructions` | コア思考原則と CLAUDE.md へのインストールスキル |

## プラグイン詳細

### mkdocs

7 フェーズのドキュメント生成ワークフロー。`/mkdocs` コマンドでプロジェクトを解析し、高品質なドキュメントを自動生成します。

```
/mkdocs        # 全フェーズ実行
/askdocs       # docs/specs/ を参照して実装質問に回答
```

### dev-workflow

開発ワークフロー支援スキルと Bash/Grep ツール制御フック。

```
/commit        # Conventional Commits 形式のアトミックコミット
/worktree-task # Git Worktree で並行タスク処理
/codex         # コードベース理解・探索
/research      # 公式ドキュメント・ソースコード調査
```

**フック**: Bash では `grep/find/cd` を制限、Grep では `git grep --function-context` を推奨。

### document-tools

```
/markdown-dashboard   # Markdown ファイル群を HTML ダッシュボードに変換
/excel-generation     # ドキュメント・コードから Excel ファイルを生成
/markdown-bold-spacing # 日本語 Markdown の **太字** スペース修正
```

> **スクリプト依存**: これらのスキルはヘルパースクリプト（`scripts/` 配下）を使用します。
> プラグインインストール後、スクリプトは `~/.claude/plugins/cache/arkatom-plugins/document-tools/<version>/` に配置されます。

### quality-tools

```
/security-audit     # コードベースの脆弱性を自律的に発見・レポート生成
/testcase-generator # E2E テストケースを自動生成（Markdown/Excel/JSON）
```

### reflection

```
/reflection    # セッション振り返りを docs/_reflection/ に保存
```

### team

Agent Teams 機能（実験的）を使った 4 メンバー協働チーム。

```
/setup-team    # CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 をセットアップ
/team          # チームを起動（PM/Coder/Reviewer/Devil）
```

> **前提**: `/setup-team` を先に実行し、Claude Code を再起動してください。

### security-guard

PreToolUse と UserPromptSubmit フックで認証情報漏洩を防止します。自動有効化（手動呼び出し不要）。

検出対象:
- AWS アクセスキー・シークレット
- API キー・トークン（汎用パターン）
- PEM 秘密鍵
- データベース URL（パスワード含む）
- 顧客の個人情報

### session-hooks

SessionStart と PreToolUse フックで開発セッションを記録します。自動有効化（手動呼び出し不要）。

### core-instructions

```
/setup-instructions    # 思考原則を ~/.claude/instructions/core/ にインストール
```

インストール後、`~/.claude/CLAUDE.md` に以下が追加されます:

```markdown
## 核心原則
- [絶対厳守](./instructions/core/base2.md)
- [深層思考](./instructions/core/deep-think.md)
- [完了チェックリスト](./instructions/core/completion-checklist.md)
```

## 注意事項

### スクリプト依存スキルについて

`worktree-task`, `doc-updater`, `markdown-dashboard`, `testcase-generator` など、一部のスキルはヘルパー Python/Bash スクリプトを参照します。

プラグインインストール後にこれらのスキルが「スクリプトが見つからない」エラーを出す場合:

1. スクリプトのプラグインキャッシュパスを確認:
   ```bash
   find ~/.claude/plugins/cache/arkatom-plugins -name "*.py" -o -name "*.sh" | sort
   ```

2. または、スクリプトをプロジェクトの `.claude/skills/` にコピー:
   ```bash
   cp -r ~/.claude/plugins/cache/arkatom-plugins/<plugin>/<version>/skills/<skill-name> \
     .claude/skills/
   ```

## ライセンス

MIT
