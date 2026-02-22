---
name: security-audit
description: コードベースの脆弱性を自律的に発見し、構造化されたマークダウンレポートを生成する
---

## 目的

OWASP Top 10に基づく脆弱性を網羅的に調査し、経営層・開発者・プロジェクトマネージャーが実用的な意思決定をするための詳細レポートを作成する。

## 使用方法

### 基本的な実行

```bash
/security-audit
```

### 除外・含めるディレクトリ・拡張子の設定

**引数で指定**:

```bash
# 特定のディレクトリのみをチェック
/security-audit --include-dirs="actions,models,models_ds,models_mail"

# 特定のディレクトリを除外
/security-audit --exclude-dirs="vendor,node_modules,Classes/PHPExcel,Classes/phpqrcode"

# 特定の拡張子のみをチェック
/security-audit --include-exts="php,js"

# 特定の拡張子を除外
/security-audit --exclude-exts="css,html"

# 組み合わせ
/security-audit --include-dirs="actions,models" --exclude-dirs="vendor" --include-exts="php"
```

**デフォルトの除外リスト**:

引数が指定されない場合、以下のディレクトリは自動的に除外される：

```
除外ディレクトリ:
- vendor/
- node_modules/
- .git/
- .claude/
- test/
- tests/
- spec/
- __tests__/
- Classes/PHPExcel/
- Classes/phpqrcode/

除外ファイルパターン:
- *_test.php
- *_spec.rb
- *.test.js
- *.spec.js
```

**重要**: 上記はデフォルトであり、`--include-dirs`を指定すると、デフォルトの除外は無視され、指定されたディレクトリのみがチェックされる。

## 原則

### 1. 網羅性

- OWASP Top 10をすべてカバー
- 既知のパターンに限定せず、論理的に危険なコードを報告
- 新しい攻撃手法にも対応

### 2. 具体性

- ファイル名と行番号を明記
- 該当コードのスニペットを引用
- 攻撃シナリオを具体的に示す

### 3. 実用性

- 今日から使える修正コードを提供
- Phase別の優先順位（Phase 1: 24h、Phase 2: 1週間、Phase 3: 1ヶ月）
- ROI分析（修正コスト vs リスクコスト）

### 4. 自律性

- 事前の仮定なしでコードベースを調査
- 使用されているすべての技術を特定
- 文脈を理解して危険性を判断

## セキュリティチェックのアプローチ

### 1. 自律的な技術スタック特定

コードベースを**事前の仮定なし**で調査せよ：

**ファイル拡張子から推測**:

- `.php`, `.js`, `.py`, `.java`, `.go`, `.rb`, `.cs`, `.kt`, `.swift`, `.rs`, `.ts`, `.jsx`, `.tsx`, `.vue` など
- 未知の拡張子でも、コードを読んで判断せよ

**インポート文・require文から推測**:

- `from flask import` → Python Flask
- `import express` → Node.js Express
- `using System` → C#
- `require 'rails'` → Ruby on Rails
- `package main` → Go
- `use Illuminate\Support\Facades` → Laravel (PHP)

**設定ファイルから推測**:

- `package.json` → Node.js
- `composer.json` → PHP
- `requirements.txt`, `Pipfile` → Python
- `Gemfile` → Ruby
- `pom.xml`, `build.gradle` → Java
- `go.mod` → Go
- `Cargo.toml` → Rust

**シバン（#!）から推測**:

- `#!/usr/bin/env python3` → Python
- `#!/usr/bin/env ruby` → Ruby
- `#!/usr/bin/env node` → Node.js
- `#!/bin/bash` → Bash

**重要**: 上記は例示であり、限定ではない。使用されているすべての技術を自律的に特定せよ。

### 2. データフローの追跡

単純なパターンマッチングではなく、**データの流れを追跡**せよ：

**ステップ1: ユーザー入力の起点を特定**

- HTTPリクエスト（POST, GET, PUT, DELETE, Cookie, Header）
- ファイルアップロード
- データベースからの取得（信頼できない外部データ）
- 外部API（信頼できないサードパーティ）
- WebSocket、gRPC
- コマンドライン引数

**ステップ2: データの流れを追跡**

- 処理（演算、変換、結合、シリアライゼーション）
- 保存（データベース、ファイル、セッション、キャッシュ）
- 出力（HTML、JSON、XML、ログ、レスポンスヘッダー）
- 外部システムへの送信（API呼び出し、メール送信）

**ステップ3: セキュリティ対策の有効性を評価**

- **サニタイゼーション**: 危険な文字の除去は適切か？
- **バリデーション**: 形式・範囲・長さのチェックは十分か？
- **エスケープ**: 出力時の無害化は正しく行われているか？
- **プリペアドステートメント**: SQLインジェクション対策は万全か？
- **暗号化**: 機密データは適切に暗号化されているか？

### 3. 文脈的な分析

単純なパターンマッチングではなく、**コードの意図を理解**せよ。

**重要な観点**:

- 不十分な対策を検出
- 文脈依存の脆弱性を検出
- 安全なコードを誤検出しない

### 3.5. 網羅性を保証する原則（重要）

**すべての技術スタックを調査**:

- プロジェクト内に存在するすべてのプログラミング言語を特定
- 各言語に対応する脆弱性パターンを調査
- **見落としやすい箇所**: サブディレクトリ内の別言語、設定ファイル、スクリプト

**直接経路と間接経路の両方を追跡**:

- データが直接出力される箇所
- 中間関数・ヘルパー関数を経由して出力される箇所
- テンプレートエンジン経由の出力
- すべての経路でセキュリティ対策の有効性を確認

**各OWASP Top 10カテゴリで徹底調査**:

- **認証**: メイン処理だけでなく、外部連携、middleware、設定ファイルも
- **暗号化**: すべての暗号化・ハッシュ化箇所（弱いアルゴリズムを網羅的に検索）
- **Injection**: すべての外部入力が使われる箇所（直接・間接問わず）
- **XSS**: 直接出力だけでなく、中間関数経由の出力も
- **アクセス制御**: 認可チェックが必要なすべての操作

**重複脆弱性の防止**:

- 既に報告した脆弱性と同じパターンを見逃さない
- 同じ脆弱性が複数箇所にあれば、すべて報告

### 4. OWASP Top 10の網羅

以下のカテゴリを**すべて**チェック：

- **A01**: Broken Access Control（認可チェック欠如、IDOR、パストラバーサル）
- **A02**: Cryptographic Failures（平文パスワード、弱い暗号化、HTTPSの未使用）
- **A03**: Injection（SQL、OS Command、LDAP、NoSQL、XML、テンプレート）
- **A04**: Insecure Design（脅威モデリング欠如、ビジネスロジック脆弱性）
- **A05**: Security Misconfiguration（デバッグモード有効、セキュリティヘッダー欠如）
- **A06**: Vulnerable Components（古いライブラリ、既知の脆弱性）
- **A07**: Authentication Failures（弱いパスワードポリシー、セッション管理不備）
- **A08**: Data Integrity Failures（安全でないデシリアライゼーション、署名検証欠如）
- **A09**: Logging Failures（ログ記録欠如、センシティブデータのログ記録）
- **A10**: SSRF（ユーザー入力によるURL生成、内部システムアクセス）

### 5. 誤検出の最小化

以下は除外せよ：

- テストコード（`test/`, `spec/`, `__tests__/`, `*_test.php`, `*_spec.rb`）
- コメント内の例示コード
- セキュリティ対策済みのコード

ただし、**対策が不十分**な場合は報告せよ：

- 例: `htmlspecialchars()`は良いが、`htmlspecialchars($input, ENT_NOQUOTES)`は不十分
- 例: `mysqli_real_escape_string()`はあるが、プリペアドステートメントの方が推奨

## 出力構造

`docs/security_review/` に以下を出力せよ：

```
docs/security_review/
├── index.md                              # ダッシュボード（統計、ナビゲーション）
├── summaries/
│   ├── 00_EXECUTIVE_SUMMARY.md          # 経営層向け（5分で読める）
│   ├── 01_CRITICAL_OVERVIEW.md          # Critical脆弱性の一覧と優先度
│   ├── 02_HIGH_MEDIUM_OVERVIEW.md       # High/Medium脆弱性の一覧
│   ├── 03_REMEDIATION_ROADMAP.md        # Phase別修正ロードマップ
│   └── 04_ROI_ANALYSIS.md               # 投資対効果分析
├── vulnerabilities/
│   └── VULN-*.md                         # 個別の脆弱性詳細
└── data/
    └── vulnerabilities.json              # メタデータ（プログラム処理用）
```

## 個別脆弱性ファイルのテンプレート

各脆弱性ファイルは[templates/vulnerability_template.md](templates/vulnerability_template.md)の構造に従うこと。

## マークダウン標準化ルール

すべてのマークダウンファイルは以下のルールに従うこと：

### 1. YAMLフロントマター

- すべての脆弱性ファイルの冒頭に配置
- 必須フィールド: `id`, `title`, `severity`, `cvss`, `category`, `phase`, `location`
- オプションフィールド: `cwe`, `owasp`, `effort_hours`, `cost_to_fix`, `risk_cost`, `discovered`, `status`, `related`

### 2. 見出しレベル

- **h1** (`#`): ファイルのタイトル（VULN-ID + 脆弱性名）
- **h2** (`##`): メインセクション（脆弱性の詳細、該当コード、攻撃シナリオ、修正方法など）
- **h3** (`###`): サブセクション（概念実証、技術的影響、推奨対策など）

### 3. コードブロック

- **言語指定必須**: \```php、\```javascript、\```sql、\```bash など
- 長いコードは要点のみ（20行以内を推奨）

### 4. テーブル

- GitHub Flavored Markdown形式を使用

### 5. リンク|### 4. テーブル

- GitHub Flavored Markdown形式を使用

### 5. リンク

- **相対パス**を使用
- GitHub形式の行番号: `file.php#L42-L56`
- 他の脆弱性へのリンク: `[VULN-005](VULN-005-sql-injection.md)`

### 6. VULN-ID

- 連番で一意に採番（VULN-001, VULN-002, VULN-003, ...）
- 3桁のゼロパディング（VULN-001 ○、VULN-1 ×）
- ファイル名: `VULN-001-sql-injection-login.md`（小文字、ハイフン区切り）

### 7. CVSS v3.1スコアの分類

- **Critical**: 9.0 - 10.0
- **High**: 7.0 - 8.9
- **Medium**: 4.0 - 6.9
- **Low**: 0.1 - 3.9

### 8. Phase分類

- **Phase 1（24時間以内）**: Critical脆弱性、容易に悪用可能
- **Phase 2（1週間以内）**: High脆弱性、または重要な機能に影響
- **Phase 3（1ヶ月以内）**: Medium/Low脆弱性、影響範囲が限定的

## vulnerabilities.jsonの構造

`data/vulnerabilities.json` は[templates/vulnerabilities_json_template.json](templates/vulnerabilities_json_template.json)の構造に従うこと。

## Claude（エージェント）への実行プロセス（厳守）

### 必須プロセス

**1. Todoツールで各OWASP項目をタスク化**（必須）

- OWASP Top 10の各カテゴリ（A01〜A10）を個別タスクとして登録
- 1つのカテゴリを完了したら、必ず次のタスクに進む
- タスクを飛ばすな、省略するな

**2. 脆弱性発見→即座にファイル生成**（必須）

- 脆弱性を1つ発見したら、その場で`VULN-XXX.md`を生成
- 「後でまとめて書く」は禁止
- TodoツールでVULN-XXXファイル生成タスクを完了としてマーク

**3. 深層思考の徹底**（必須）

- 各OWASP項目の調査開始前に、sequential-thinkingで調査戦略を立案
- 表面的なgrep数回で満足するな
- すべての技術スタック、すべての間接経路を調査

**4. 進捗の可視化**（必須）

- 現在どのOWASP項目を調査中か明示
- 発見した脆弱性数をリアルタイムで報告
- 調査完了したカテゴリと未調査カテゴリを明確に区別

## 制約

### ファイルサイズ

- 個別脆弱性ファイルは50KB以下を推奨
- コードスニペットは20行以内（長い場合は要点のみ）
- サマリーファイルは100KB以下

### リンク

- すべてのリンクは相対パス
- 外部リンク（OWASP, CWE）は絶対URL

### ファイル名

- 小文字、ハイフン区切り
- 例: `VULN-001-sql-injection-login.md`、`00_EXECUTIVE_SUMMARY.md`

### 文体

- 技術者も経営層も理解できる言葉
- 専門用語には簡単な説明を追加
- 箇条書きと表を活用（長文は避ける）

### ROI計算

- ROI = リスクコスト / 修正コスト
- 例: 5000万円 / 3万円 = 1666.67x

## レポート生成の流れ

1. **コードベースのスキャン**
   - すべてのファイルを調査
   - 技術スタックを特定

2. **脆弱性の発見**
   - データフロー追跡
   - 文脈的な分析
   - OWASP Top 10の網羅

3. **脆弱性の分析**
   - CVSS スコア計算
   - Phase 分類
   - 工数・コスト見積もり

4. **マークダウン生成**
   - 個別脆弱性ファイル（vulnerabilities/）
   - サマリーファイル（summaries/）
   - データファイル（data/vulnerabilities.json）
   - インデックス（index.md）

5. **品質チェック**
   - すべてのファイルがテンプレートに従っているか
   - リンク切れがないか
   - マークダウン標準化ルールに準拠しているか
