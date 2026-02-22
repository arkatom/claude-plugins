#!/usr/bin/env python3
import json
import re
import sys

# Define validation rules as a list of (validation function, message) tuples
VALIDATION_RULES = [
    (
        lambda cmd: cmd.strip().startswith("grep "),
        "grep の変わりに git grep --function-context [--and|--or|--not|(|)|-e <pattern>...] -- <pathspec>... を使ってください。--function-context フラグにより出力行が多すぎる場合、 --show-function と -C フラグを利用してください",
    ),
    (
        lambda cmd: cmd.strip().startswith("rg "),
        "rg の変わりに git grep --function-context [--and|--or|--not|(|)|-e <pattern>...] -- <pathspec>... を使ってください。--function-context フラグにより出力行が多すぎる場合、 --show-function と -C フラグを利用してください",
    ),
    (
        lambda cmd: (
            re.match(r"^git\s+grep\s+", cmd) and
            not re.search(r"-W|-p|--function-context|--show-function", cmd)
        ),
        "git grep では --function-context か --show-function フラグを使ってください。まず --function-context フラグを利用し、結果行が多すぎる場合、 --show-function と [ -C | -A | -B ] フラグを利用してください",
    ),
    (
        lambda cmd: re.search(r"\bfind\s+.+\s+-name\b", cmd),
        "find -name の変わりに git ls-files -- <パターン> を使ってください。git ls-files -o --exclude-standard を使うと、未追跡のファイルも確認できます。チェックアウトしていないコミットを確認するときは --with-tree=<tree-ish> でコミットを指定してください",
    ),
    (
        lambda cmd: (
            re.search(r"^git\s+ls-files\b.*\|\s*xargs\s+(git\s+)?grep", cmd)
        ),
        "git ls-files を xargs へパイプして使うのではなく、git grep --show-function [-C|-A|-B] -- <path...> を使ってください。xargs は不要です",
    ),
    (
        lambda cmd: (
            re.match(r"^cd", cmd)
        ),
        "cd コマンドは使わないでください。例えば yarn の場合 --cwd フラグ、make の場合 -C フラグ、docker compose なら --project-directory フラグが利用できます",
    ),
]


def validate_command(command: str) -> list[str]:
    issues = []
    for validation_func, message in VALIDATION_RULES:
        if validation_func(command):
            issues.append(message)
    return issues


try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})
command = tool_input.get("command", "")

if tool_name != "Bash" or not command:
    sys.exit(1)

# Validate the command
issues = validate_command(command)

if issues:
    for message in issues:
        print(f"• {message}", file=sys.stderr)
    sys.exit(2)
