# doc-updater スキル: トラブルシューティング

このファイルでは、doc-updaterスキルの使用中に発生する可能性のある問題と解決方法を示します。

## エラー: ai_context.diffが生成されない

### 症状

export_diff.shを実行しても、ai_context.diffファイルが生成されない。

### 原因と解決方法

#### 1. Gitリポジトリではない

**確認方法:**
```bash
git rev-parse --is-inside-work-tree
```

**解決方法:**
Gitリポジトリ内で実行してください。Gitリポジトリではない場合、このスキルは使用できません。

#### 2. export_diff.shが見つからない

**確認方法:**
```bash
ls -la .claude/skills/doc-updater/scripts/export_diff.sh
```

**解決方法:**
スキルが正しくインストールされているか確認してください。パスが正しくない場合、スキルディレクトリから実行してください。

#### 3. 実行権限がない

**確認方法:**
```bash
ls -la .claude/skills/doc-updater/scripts/export_diff.sh
```

実行権限（`-rwxr-xr-x`のようにxが含まれる）がない場合、権限を付与してください。

**解決方法:**
```bash
chmod +x .claude/skills/doc-updater/scripts/export_diff.sh
```

## 警告: 差分が大きすぎる

### 症状

ai_context.diffが生成されるが、ファイルサイズが非常に大きい（数MB以上）。AIが処理しきれない可能性がある。

### 解決方法

#### 1. 対象期間を短くする

```bash
# 1週間前から → 3日前から
bash .claude/skills/doc-updater/scripts/export_diff.sh -day 3

# 1ヶ月前から → 1週間前から
bash .claude/skills/doc-updater/scripts/export_diff.sh -week
```

#### 2. 特定ディレクトリに絞る

```bash
# プロジェクト全体 → src/のみ
bash .claude/skills/doc-updater/scripts/export_diff.sh -week src/

# 複数ディレクトリ → 1つのディレクトリ
bash .claude/skills/doc-updater/scripts/export_diff.sh -week src/auth/
```

#### 3. より多くのファイルを除外

```bash
# テスト、ビルド出力、画像などを除外
bash .claude/skills/doc-updater/scripts/export_diff.sh -week \
  -e "*.test.ts" \
  -e "*.spec.ts" \
  -e "dist/" \
  -e "build/" \
  -e "out/" \
  -e "*.png" \
  -e "*.jpg"
```

## 問題: 関係ない変更が含まれる

### 症状

ai_context.diffに、ドキュメント更新に関係ない変更（テストファイル、ビルド設定など）が大量に含まれている。

### 解決方法

#### 除外パターンを追加

```bash
# テストファイルを除外
bash .claude/skills/doc-updater/scripts/export_diff.sh -week \
  -e "*.test.ts" \
  -e "*.spec.ts"

# 設定ファイルを除外
bash .claude/skills/doc-updater/scripts/export_diff.sh -week \
  -e "*.config.ts" \
  -e "*.config.js" \
  -e ".eslintrc*" \
  -e ".prettierrc*"

# ドキュメント自体の変更を除外（コードの変更のみを対象にする）
bash .claude/skills/doc-updater/scripts/export_diff.sh -week -e "docs/"
```

## 問題: ドキュメント更新が不正確

### 症状

生成されたドキュメント更新が、実際の変更を正確に反映していない。

### 原因と解決方法

#### 1. コミットメッセージが不明瞭

**原因:**
コミットメッセージが「fix」「update」などの簡潔すぎるメッセージで、意図が読み取れない。

**解決方法:**
- コミットメッセージを改善する（今後の対策）
- ai_context.diffのPART 2: CODE DIFFSを重点的に分析する

#### 2. 差分が多すぎて意図が不明確

**原因:**
大量の変更が含まれており、主要な変更点が埋もれている。

**解決方法:**
- 対象期間を短くする（-day 3など）
- 特定ディレクトリに絞る（src/auth/など）
- 複数回に分けてドキュメント更新を行う

#### 3. 破壊的変更の見落とし

**原因:**
BREAKING CHANGEが含まれているのに、通常の変更として処理されている。

**解決方法:**
- コミットメッセージに「BREAKING CHANGE:」を含める（今後の対策）
- 手動でコミットログを確認し、破壊的変更を特定する

## 問題: スクリプトが実行できない（Permission Denied）

### 症状

```
bash: .claude/skills/doc-updater/scripts/export_diff.sh: Permission denied
```

### 解決方法

実行権限を付与してください：

```bash
chmod +x .claude/skills/doc-updater/scripts/export_diff.sh
```

## 問題: 変更がない期間を指定した

### 症状

```
警告: 履歴が見つかりません。最初のコミットから取得します。
```

### 原因

指定した期間にコミットが存在しない（例: 1ヶ月前を指定したが、リポジトリは2週間前に作成された）。

### 解決方法

これは警告であり、エラーではありません。スクリプトは最初のコミットから差分を取得します。問題なければそのまま続行してください。

## その他のヒント

### 差分ファイルのサイズ確認

```bash
ls -lh ai_context.diff
```

一般的な目安：
- 50KB以下: 理想的
- 50KB～200KB: 許容範囲
- 200KB以上: 大きすぎる、絞り込みを推奨

### 対象コミット数の確認

```bash
git log --oneline --since="1 week ago" | wc -l
```

コミット数が多すぎる場合（100件以上など）、期間を短くすることを検討してください。
