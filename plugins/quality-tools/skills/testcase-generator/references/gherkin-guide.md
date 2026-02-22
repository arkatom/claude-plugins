# Gherkin形式ガイド

## Gherkinとは

Gherkin は **BDD（振る舞い駆動開発）** で使用される、人間が読みやすいテスト記述言語です。

## 基本構文

```gherkin
Feature: <機能名>
  <機能の説明>

Scenario: <シナリオ名>
  Given <前提条件>
  When <アクション>
  And <追加アクション>
  Then <期待結果>
  And <追加期待結果>
```

## キーワード

| キーワード | 意味 | 使用例 |
|----------|------|-------|
| **Feature** | テスト対象の機能 | `Feature: ログイン機能` |
| **Scenario** | 具体的なテストシナリオ | `Scenario: 正常系 - 正しいIDとパスワードでログイン` |
| **Given** | 前提条件 | `Given ユーザーがログイン画面にアクセスしている` |
| **When** | ユーザーのアクション | `When メールアドレスに「test@example.com」を入力する` |
| **And** | 追加の前提条件またはアクション | `And パスワードに「password123」を入力する` |
| **Then** | 期待される結果 | `Then ダッシュボードページに遷移する` |
| **But** | 否定的な期待結果 | `But エラーメッセージは表示されない` |

## 良い例

### 正常系テスト

```gherkin
Feature: 問い合わせフォーム送信

Scenario: 正常系 - すべて必須項目を入力して送信
  Given ユーザーが問い合わせ入力画面にアクセスしている
  When 姓に「山田」を入力する
  And 名に「太郎」を入力する
  And メールアドレスに「test@example.com」を入力する
  And 電話番号に「03-1234-5678」を入力する
  And お問い合わせ内容に「資料請求について」を入力する
  And 確認ボタンをクリックする
  Then 確認画面に遷移する
  And 入力内容が正しく表示されている
  When 送信ボタンをクリックする
  Then 完了画面に遷移する
  And 完了メッセージが表示される
  And 確認メールがユーザーに送信される
  And データベースに問い合わせレコードが保存される
```

### 異常系テスト

```gherkin
Feature: ログイン機能

Scenario: 異常系 - 不正なメールアドレスでログイン
  Given ユーザーがログイン画面にアクセスしている
  When メールアドレスに「invalid-email」を入力する
  And パスワードに「password123」を入力する
  And ログインボタンをクリックする
  Then エラーメッセージ「メールアドレスの形式が正しくありません」が表示される
  And ログイン画面にとどまる
  And ダッシュボードページには遷移しない
```

### 境界値テスト

```gherkin
Feature: 問い合わせフォーム送信

Scenario: 境界値 - 名前が最大文字数（50文字）
  Given ユーザーが問い合わせ入力画面にアクセスしている
  When 姓に50文字の文字列を入力する
  And その他の必須項目をすべて入力する
  And 確認ボタンをクリックする
  Then 確認画面に遷移する
  And 姓フィールドに50文字がすべて表示されている

Scenario: 境界値 - 名前が最大文字数+1（51文字）
  Given ユーザーが問い合わせ入力画面にアクセスしている
  When 姓に51文字の文字列を入力する
  And 確認ボタンをクリックする
  Then エラーメッセージ「姓は50文字以内で入力してください」が表示される
  And 確認画面には遷移しない
```

### セキュリティテスト

```gherkin
Feature: 問い合わせフォーム送信

Scenario: セキュリティ - XSS攻撃の防御
  Given ユーザーが問い合わせ入力画面にアクセスしている
  When お問い合わせ内容に「<script>alert('XSS')</script>」を入力する
  And その他の必須項目をすべて入力する
  And 確認ボタンをクリックする
  Then 確認画面に遷移する
  And スクリプトがエスケープされて表示されている
  And スクリプトが実行されない

Scenario: セキュリティ - CSRF攻撃の防御
  Given ユーザーが問い合わせ確認画面にアクセスしている
  And CSRFトークンが無効な状態
  When 送信ボタンをクリックする
  Then エラーメッセージ「無効なリクエストです」が表示される
  And データベースにレコードが保存されない
```

## Background（共通の前提条件）

複数のシナリオで共通の前提条件がある場合、`Background` を使用します：

```gherkin
Feature: ログイン機能

Background:
  Given ユーザーアカウント「test@example.com」が登録済み
  And パスワードは「password123」

Scenario: 正常系 - 正しいIDとパスワード
  Given ユーザーがログイン画面にアクセスしている
  When メールアドレスに「test@example.com」を入力する
  And パスワードに「password123」を入力する
  Then ログインに成功する

Scenario: 異常系 - 間違ったパスワード
  Given ユーザーがログイン画面にアクセスしている
  When メールアドレスに「test@example.com」を入力する
  And パスワードに「wrong-password」を入力する
  Then ログインに失敗する
```

## Scenario Outline（データ駆動テスト）

複数の入力パターンをテストする場合、`Scenario Outline` と `Examples` を使用します：

```gherkin
Feature: バリデーション

Scenario Outline: 異常系 - 不正なメールアドレス
  Given ユーザーが入力画面にアクセスしている
  When メールアドレスに「<email>」を入力する
  And 確認ボタンをクリックする
  Then エラーメッセージ「<error_message>」が表示される

  Examples:
    | email | error_message |
    | invalid | メールアドレスの形式が正しくありません |
    | @example.com | メールアドレスの形式が正しくありません |
    | test@ | メールアドレスの形式が正しくありません |
    | test@.com | メールアドレスの形式が正しくありません |
```

## ベストプラクティス

### 1. 宣言的に書く（How ではなく What）

**良い例**:
```gherkin
When ログインボタンをクリックする
Then ダッシュボードページに遷移する
```

**悪い例**:
```gherkin
When HTTPリクエストをPOSTメソッドで/loginエンドポイントに送信する
Then HTTPステータスコード302が返却され、Location ヘッダーで/dashboardにリダイレクトされる
```

### 2. ビジネス用語を使用する

**良い例**:
```gherkin
Given ユーザーがカートに商品を追加済み
When チェックアウトボタンをクリックする
Then 決済画面に遷移する
```

**悪い例**:
```gherkin
Given session['cart'] に product_id が存在する
When /checkout エンドポイントに POST する
Then view('checkout') が render される
```

### 3. 1つのシナリオで1つのことをテストする

各シナリオは **単一の目的** を持つべきです。

**良い例**（分離）:
```gherkin
Scenario: ログイン成功後、ダッシュボードに遷移
Scenario: ログイン失敗時、エラーメッセージが表示される
```

**悪い例**（複数の目的）:
```gherkin
Scenario: ログイン機能のテスト
  # 正常系と異常系を1つのシナリオに詰め込んでいる
```

### 4. 具体的な値を使用する

**良い例**:
```gherkin
When 姓に「山田」を入力する
And 名に「太郎」を入力する
```

**悪い例**:
```gherkin
When 姓に有効な値を入力する
And 名に有効な値を入力する
```

## 参考文献

- Cucumber Official Documentation: https://cucumber.io/docs/gherkin/
- BDD in Action (John Ferguson Smart)
- The Cucumber Book (Matt Wynne & Aslak Hellesøy)
