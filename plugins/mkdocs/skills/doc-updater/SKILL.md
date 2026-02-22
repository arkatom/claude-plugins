---
name: doc-updater
description: Git変更差分を分析してドキュメントを自動更新。README、仕様書、ガイドなどを最新状態に保つ。scripts/export_diff.shで差分を抽出し、変更内容に基づいて適切にドキュメントを更新する。ユーザーがドキュメントの更新、変更の反映、ドキュメントの同期などを要求した場合に使用。
---

# ドキュメント自動更新スキル

Gitの変更履歴を分析し、ドキュメント（README、仕様書、ガイドなど）を自動的に更新します。

## タスク

### フェーズ1: パラメータ確認と差分抽出

#### 1. ユーザーに質問

AskUserQuestionで以下を質問してください：

**対象ドキュメント（必須）:**

- README.md
- docs/specs/
- docs/guides/
- すべて

**対象期間（オプション）:**

- デフォルト: 1週間前から
- ユーザーが指定した場合はそれを使用

**除外パターン（オプション）:**

- デフォルト: テストファイル (`*.test.ts`, `*.spec.ts`)
- ユーザーが追加指定した場合は追加

#### 2. export_diff.shスクリプトの実行

```bash
bash .claude/skills/doc-updater/scripts/export_diff.sh -week [対象ディレクトリ] -e [除外パターン]
```

**基本例:**

```bash
# README更新: ドキュメント自体の変更を除外
bash .claude/skills/doc-updater/scripts/export_diff.sh -week -e "docs/"

# 仕様書更新: src/のみを対象
bash .claude/skills/doc-updater/scripts/export_diff.sh -week src/ -e "*.test.ts"
```

スクリプトが `ai_context.diff` を生成します。

#### 3. 差分ファイルの読み込み

```
Read tool で ai_context.diff を読み込む
```

### フェーズ2: 差分の分析

`ai_context.diff` を分析：

**PART 1: COMMIT LOGS（変更の意図）**

- 新機能: "feat:", "add:" で始まるコミット
- バグ修正: "fix:" で始まるコミット
- リファクタリング: "refactor:"
- 削除: "remove:", "delete:"
- 破壊的変更: "BREAKING CHANGE:"

**PART 2: CODE DIFFS（変更の詳細）**

- 新規/削除ファイル
- 主要な変更（関数追加、API変更、設定変更）
- 技術スタックの変更（新しい依存関係）

### フェーズ3: ドキュメント更新

分析結果に基づいて、対象ドキュメントを更新：

**README.md:**

- 機能一覧の更新
- セットアップ手順の更新
- 使用例の最新化
- 技術スタックの更新

**仕様書（docs/specs/）:**

- API仕様の更新
- データモデルの更新
- 設計方針の記載

**ガイド（docs/guides/）:**

- セットアップガイドの更新
- チュートリアルの最新化

### フェーズ4: 報告

以下の形式で報告：

```markdown
## ドキュメント更新完了

### 更新されたドキュメント
- README.md

### 主な変更内容
1. 新機能「〇〇」を追加（feat: xxx のコミットに基づく）
2. セットアップ手順に新しい環境変数を追記
3. 技術スタックにライブラリXXXを追加
```

## 注意事項

### やるべきこと

✅ **変更意図の尊重**: コミットメッセージから意図を読み取り、文脈に合わせた説明を記述

✅ **一貫性の維持**: 既存のドキュメントスタイルに合わせる

✅ **ユーザー視点**: 開発者だけでなく、初心者にも分かりやすく記述

### やってはいけないこと

❌ **機械的なコピペ**: コミットメッセージやコードをそのまま貼り付けない

❌ **過度な詳細**: 内部実装の詳細をREADMEに記載しない

❌ **重要な変更の見落とし**: 破壊的変更（BREAKING CHANGE）は必ず記載

## 詳細ガイド

詳細な使用例やトラブルシューティングについては、以下のreferencesファイルを参照してください：

- **使用例**: [references/examples.md](references/examples.md) - 週次更新、特定機能のドキュメント追加、リリース前の総合更新など
- **トラブルシューティング**: [references/troubleshooting.md](references/troubleshooting.md) - エラー対処法、差分が大きすぎる場合の対応など
