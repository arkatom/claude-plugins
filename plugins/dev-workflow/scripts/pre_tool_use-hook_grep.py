#!/usr/bin/env python3
import json
import re
import sys

# Define validation rules as a list of (validation function, message) tuples
VALIDATION_RULES = [
    (
        lambda cmd: True,
        "git grep --function-context [--and|--or|--not|(|)|-e <pattern>...] -- <pathspec>... を使ってください。--function-context フラグにより出力行が多すぎる場合、 --show-function と -C フラグを利用してください",
    ),
]


def validate_command(pattern: str) -> list[str]:
    issues = []
    for validation_func, message in VALIDATION_RULES:
        if validation_func(pattern):
            issues.append(message)
    return issues


try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})
pattern = tool_input.get("pattern", "")

if tool_name != "Grep" or not pattern:
    sys.exit(1)

# Validate the pattern
issues = validate_command(pattern)

if issues:
    for message in issues:
        print(f"• {message}", file=sys.stderr)
    sys.exit(2)
