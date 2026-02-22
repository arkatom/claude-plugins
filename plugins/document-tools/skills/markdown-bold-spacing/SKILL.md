---
name: markdown-bold-spacing
description: "Fix Markdown bold (**text**) spacing by adding half-width spaces before and after bold text when surrounded by Japanese characters. Use when working with Markdown files that need proper bold formatting, especially mixed Japanese/English documents where **強調** patterns need spaces for correct rendering."
---

# Markdown Bold Spacing

Automatically add half-width spaces around Markdown bold syntax (`**text**`) for proper rendering in Japanese documents.

## Problem

Markdown bold syntax requires spaces around `**` for correct rendering when adjacent to text:

- `これは**重要**です` → renders incorrectly
- `これは **重要** です` → renders correctly

## Usage

Run the included Python script on target Markdown files:

```bash
python3 <script_dir>/fix_bold_spacing.py <file.md> > output.md
```

Or process multiple files:

```bash
find . -name "*.md" | while read f; do
    python3 <script_dir>/fix_bold_spacing.py "$f" > "$f.tmp" && mv "$f.tmp" "$f"
done
```

> **Note**: `<script_dir>` refers to the `scripts/` directory within this skill. When installed as a plugin, it is located at `~/.claude/plugins/cache/arkatom-plugins/document-tools/<version>/skills/markdown-bold-spacing/scripts/`. When using project-local installation, use `.claude/skills/markdown-bold-spacing/scripts/`.

## What It Does

**Adds spaces:**

- Before `**` when preceded by Japanese characters (hiragana, katakana, kanji)
- After `**` when followed by Japanese characters

**Preserves (no changes):**

- Line-start patterns: `**講師:**`, `## **見出し:**`
- List items: `- **項目:**`, `* **項目:**`, `1. **項目:**`
- Key-value format: `**キー:** 値`

## Script Reference

The `scripts/fix_bold_spacing.py` script handles:

- Line-by-line processing to preserve structure
- Regex-based pattern matching for Japanese characters
- Special case handling for lists, headers, and key-value pairs
