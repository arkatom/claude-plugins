#!/usr/bin/env python3
"""
セキュリティポリシー準拠フック

対象ポリシー:
    1. 基本 AI利用ポリシー（共通方針）
    2. 基本 Claude Code セキュリティガイドライン

機能:
    - /bug コマンドのブロック (UserPromptSubmit)
    - 認証情報/秘密鍵パターンの検出 (PreToolUse)
    - 本番設定ファイル・機密ファイルへのアクセスブロック (PreToolUse)
    - 顧客特定可能情報の警告 (PreToolUse)
"""

import json
import re
import sys

# ============================================================
# パターン定義（モジュールレベルでプリコンパイル）
# ============================================================

# --- /bug コマンド ---
BUG_COMMAND_PATTERN = re.compile(r"^\s*/bug\b")

# --- 認証情報パターン (HARD BLOCK) ---
CREDENTIAL_PATTERNS = [
    # AWS Access Key
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key"),
    # API Key 代入
    (re.compile(
        r"(?:api[_-]?key|apikey|api[_-]?token)\s*[=:]\s*[\"']?[A-Za-z0-9_\-]{20,}",
        re.IGNORECASE,
    ), "API Key"),
    # Bearer Token
    (re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]{20,}"), "Bearer Token"),
    # 秘密鍵 (PEM)
    (re.compile(r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----"), "秘密鍵"),
    # DB 接続文字列
    (re.compile(
        r"(?:mongodb|postgres(?:ql)?|mysql|redis|amqp)://[^\s\"']+@[^\s\"']+",
        re.IGNORECASE,
    ), "DB接続文字列"),
    # JDBC 接続文字列
    (re.compile(r"jdbc:[a-z]+://[^\s\"']+", re.IGNORECASE), "JDBC接続文字列"),
    # パスワード代入
    (re.compile(
        r"(?:password|passwd|pwd)\s*[=:]\s*[\"'][^\"']{8,}[\"']",
        re.IGNORECASE,
    ), "パスワード"),
    # シークレットキー代入
    (re.compile(
        r"(?:secret[_-]?key|client[_-]?secret|signing[_-]?key)\s*[=:]\s*[\"']?[A-Za-z0-9_\-]{16,}",
        re.IGNORECASE,
    ), "シークレットキー"),
    # GitHub Token
    (re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}"), "GitHub Token"),
    # GitLab Token
    (re.compile(r"glpat-[A-Za-z0-9_\-]{20,}"), "GitLab Token"),
    # Slack Token
    (re.compile(r"xox[baprs]-[A-Za-z0-9\-]+"), "Slack Token"),
    # 環境変数形式の認証情報
    (re.compile(
        r"(?:TOKEN|SECRET|CREDENTIAL|AUTH_KEY)\s*=\s*[\"']?[A-Za-z0-9_\-/+=]{20,}",
        re.IGNORECASE,
    ), "認証トークン"),
]

# --- 機密ファイルパスパターン (HARD BLOCK) ---
SENSITIVE_FILE_PATTERNS = [
    # .env ファイル
    (re.compile(r"(?:^|/)\.env(?:\.[a-zA-Z]+)?$"), ".envファイル"),
    # 認証情報ディレクトリ
    (re.compile(r"(?:^|/)(?:credentials|secrets|\.aws|\.ssh|\.gnupg)/"), "認証情報ディレクトリ"),
    # SSH 鍵ファイル
    (re.compile(r"(?:^|/)(?:id_rsa|id_ed25519|id_ecdsa)(?:\.pub)?$"), "SSH鍵ファイル"),
    # 認証設定ファイル
    (re.compile(r"(?:^|/)\.(?:netrc|pgpass|my\.cnf)$"), "認証設定ファイル"),
    # 本番設定ファイル
    (re.compile(
        r"(?:^|/)(?:config|settings)/(?:production|prod)\.[a-z]+$",
        re.IGNORECASE,
    ), "本番設定ファイル"),
    # 本番 docker-compose / production 設定
    (re.compile(
        r"(?:^|/)(?:docker-compose\.prod|production)\.(yml|yaml|json|toml)$",
        re.IGNORECASE,
    ), "本番設定ファイル"),
    # 鍵・証明書ファイル
    (re.compile(r"(?:^|/).*\.(?:pem|key|p12|pfx|jks|keystore)$"), "鍵/証明書ファイル"),
    # Terraform ステートファイル
    (re.compile(r"(?:^|/)terraform\.tfstate"), "Terraformステートファイル"),
]

# --- Bash コマンド内のファイルアクセス検出用 ---
BASH_FILE_ACCESS_RE = re.compile(
    r"\b(?:cat|less|more|head|tail|bat|vim|nano|vi|code|open|cp|scp|source)\b"
)

# --- 顧客特定可能情報パターン (SOFT WARNING) ---
CUSTOMER_INFO_PATTERNS = [
    # 顧客名ラベル（日本語）
    (re.compile(r"(?:顧客名?|クライアント|取引先)\s*[:：]\s*\S+"), "顧客名"),
    # 顧客名ラベル（英語）
    (re.compile(
        r"(?:customer|client)\s*(?:name|id)?\s*[:=]\s*[\"']?\w+",
        re.IGNORECASE,
    ), "顧客名(英語)"),
    # 契約番号
    (re.compile(
        r"(?:契約番号|契約ID|contract[_-]?(?:id|number|no))\s*[:=：]\s*[\"']?\w+",
        re.IGNORECASE,
    ), "契約番号"),
    # システムID
    (re.compile(
        r"(?:システムID|system[_-]?id)\s*[:=：]\s*[\"']?\w+",
        re.IGNORECASE,
    ), "システムID"),
    # プロジェクト名
    (re.compile(
        r"(?:project[_-]?(?:name|code|id)|案件名?|PJ名?)\s*[:=：]\s*[\"']?\S+",
        re.IGNORECASE,
    ), "プロジェクト名"),
    # 担当者名（日本語ラベル付き）
    (re.compile(r"(?:担当者?|責任者|連絡先)\s*[:：]\s*[一-龥ぁ-んァ-ヶ]{2,5}"), "個人名"),
]


# ============================================================
# レスポンスビルダー
# ============================================================

def make_deny(reason: str) -> dict:
    """PreToolUse: ツール実行をブロック"""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def make_ask(reason: str) -> dict:
    """PreToolUse: ユーザーに確認を求める"""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }


def make_prompt_block(reason: str) -> dict:
    """UserPromptSubmit: ユーザー入力をブロック"""
    return {
        "decision": "block",
        "reason": reason,
    }


# ============================================================
# チェック関数
# ============================================================

def check_credentials(text: str):
    """テキスト内の認証情報パターンを検出。(マッチ文字列, ラベル) or None"""
    if not text:
        return None
    for pattern, label in CREDENTIAL_PATTERNS:
        match = pattern.search(text)
        if match:
            snippet = match.group()[:20] + "..." if len(match.group()) > 20 else match.group()
            return (snippet, label)
    return None


def check_sensitive_file(file_path: str):
    """ファイルパスが機密ファイルに該当するか。(パス, ラベル) or None"""
    if not file_path:
        return None
    for pattern, label in SENSITIVE_FILE_PATTERNS:
        if pattern.search(file_path):
            return (file_path, label)
    return None


def check_customer_info(text: str):
    """テキスト内の顧客特定可能情報を検出。(マッチ文字列, ラベル) or None"""
    if not text:
        return None
    for pattern, label in CUSTOMER_INFO_PATTERNS:
        match = pattern.search(text)
        if match:
            snippet = match.group()[:30] + "..." if len(match.group()) > 30 else match.group()
            return (snippet, label)
    return None


def check_bash_file_access(command: str):
    """Bashコマンド内の機密ファイルアクセスを検出"""
    if not BASH_FILE_ACCESS_RE.search(command):
        return None
    tokens = command.split()
    for token in tokens:
        result = check_sensitive_file(token)
        if result:
            return result
    return None


# ============================================================
# イベントハンドラー
# ============================================================

def handle_user_prompt_submit(hook_input: dict):
    """/bug コマンドのブロック"""
    prompt = hook_input.get("prompt", "")

    if BUG_COMMAND_PATTERN.match(prompt):
        response = make_prompt_block(
            "[セキュリティガイドライン 2.2] /bug コマンドの使用は禁止されています。\n"
            "理由: /bug 実行時、会話のトランスクリプト全文がAnthropicに送信され、"
            "5年間保管されます。\n"
            "問題報告はAI推進室または社内の課題管理システムをご利用ください。"
        )
        print(json.dumps(response, ensure_ascii=False))
        sys.exit(0)

    sys.exit(0)


def handle_pre_tool_use(hook_input: dict):
    """ツール入力のポリシーチェック"""
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    hard_blocks = []
    soft_warnings = []

    if tool_name == "Bash":
        command = tool_input.get("command", "")

        cred = check_credentials(command)
        if cred:
            hard_blocks.append(
                f"[セキュリティガイドライン 3.1] Bashコマンドに{cred[1]}が検出されました: {cred[0]}\n"
                "認証情報をAIツールに入力しないでください。"
            )

        file_access = check_bash_file_access(command)
        if file_access:
            hard_blocks.append(
                f"[セキュリティガイドライン 3.1] 機密ファイルへのアクセス: {file_access[1]}（{file_access[0]}）\n"
                "本番設定ファイル・認証情報ファイルの内容をAIツールに入力しないでください。"
            )

        cust = check_customer_info(command)
        if cust:
            soft_warnings.append(
                f"[AI利用ポリシー 第8条] 顧客特定可能情報の可能性: {cust[1]}（{cust[0]}）\n"
                "顧客名・プロジェクト名は匿名化/マスキングしてから入力してください。"
            )

    elif tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "")[:10000]  # 性能のため先頭10000文字のみ

        sensitive = check_sensitive_file(file_path)
        if sensitive:
            hard_blocks.append(
                f"[セキュリティガイドライン 3.1] 機密ファイルへの書き込み: {sensitive[1]}（{sensitive[0]}）\n"
                "本番設定ファイルへの書き込みは禁止されています。"
            )

        cred = check_credentials(content)
        if cred:
            hard_blocks.append(
                f"[セキュリティガイドライン 3.1] 書き込み内容に{cred[1]}が検出されました: {cred[0]}\n"
                "認証情報をファイルにハードコードしないでください。"
            )

        cust = check_customer_info(content)
        if cust:
            soft_warnings.append(
                f"[AI利用ポリシー 第8条] 書き込み内容に顧客特定可能情報の可能性: {cust[1]}（{cust[0]}）\n"
                "顧客名・プロジェクト名は匿名化/マスキングしてください。"
            )

    elif tool_name == "Edit":
        file_path = tool_input.get("file_path", "")
        new_string = tool_input.get("new_string", "")

        sensitive = check_sensitive_file(file_path)
        if sensitive:
            hard_blocks.append(
                f"[セキュリティガイドライン 3.1] 機密ファイルの編集: {sensitive[1]}（{sensitive[0]}）\n"
                "本番設定ファイルの編集は禁止されています。"
            )

        cred = check_credentials(new_string)
        if cred:
            hard_blocks.append(
                f"[セキュリティガイドライン 3.1] 編集内容に{cred[1]}が検出されました: {cred[0]}\n"
                "認証情報をファイルにハードコードしないでください。"
            )

        cust = check_customer_info(new_string)
        if cust:
            soft_warnings.append(
                f"[AI利用ポリシー 第8条] 編集内容に顧客特定可能情報の可能性: {cust[1]}（{cust[0]}）\n"
                "顧客名・プロジェクト名は匿名化/マスキングしてください。"
            )

    elif tool_name == "Read":
        file_path = tool_input.get("file_path", "")

        sensitive = check_sensitive_file(file_path)
        if sensitive:
            hard_blocks.append(
                f"[セキュリティガイドライン 3.1] 機密ファイルの読み取り: {sensitive[1]}（{sensitive[0]}）\n"
                "本番設定ファイル・認証情報ファイルの内容をAIツールに入力しないでください。"
            )

    elif tool_name == "WebFetch":
        prompt = tool_input.get("prompt", "")
        url = tool_input.get("url", "")
        combined = f"{url} {prompt}"

        cred = check_credentials(combined)
        if cred:
            hard_blocks.append(
                f"[セキュリティガイドライン 3.1] Web操作に{cred[1]}が検出されました: {cred[0]}\n"
                "認証情報を外部サービスに送信しないでください。"
            )

        cust = check_customer_info(combined)
        if cust:
            soft_warnings.append(
                f"[AI利用ポリシー 第8条] Web操作に顧客特定可能情報の可能性: {cust[1]}（{cust[0]}）\n"
                "顧客名は匿名化してから送信してください。"
            )

    elif tool_name == "WebSearch":
        query = tool_input.get("query", "")

        cred = check_credentials(query)
        if cred:
            hard_blocks.append(
                f"[セキュリティガイドライン 3.1] 検索クエリに{cred[1]}が検出されました: {cred[0]}\n"
                "認証情報を検索エンジンに送信しないでください。"
            )

        cust = check_customer_info(query)
        if cust:
            soft_warnings.append(
                f"[AI利用ポリシー 第8条] 検索クエリに顧客特定可能情報の可能性: {cust[1]}（{cust[0]}）\n"
                "顧客名は匿名化してから検索してください。"
            )

    # --- 判定 ---
    if hard_blocks:
        reason = "\n---\n".join(hard_blocks)
        print(json.dumps(make_deny(reason), ensure_ascii=False))
        sys.exit(0)

    if soft_warnings:
        reason = "\n---\n".join(soft_warnings)
        print(json.dumps(make_ask(reason), ensure_ascii=False))
        sys.exit(0)

    sys.exit(0)


# ============================================================
# メインエントリポイント
# ============================================================

def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        # パースエラー時は fail-open（開発を妨げない）
        sys.exit(0)

    event_name = hook_input.get("hook_event_name", "")

    if event_name == "UserPromptSubmit":
        handle_user_prompt_submit(hook_input)
    elif event_name == "PreToolUse":
        handle_pre_tool_use(hook_input)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
