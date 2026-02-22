---
name: commit
description: Atomic commit with conventional format
---

## Commit Workflow
1. Run `git status` and `git diff --staged` to understand all changes
2. Group changes by logical unit (never mix refactors with features)
3. For each group, create a separate commit with format: `<type>(<scope>): <description in Japanese>`
4. Types: feat, fix, refactor, docs, chore, style
5. Never use interactive git commands
6. Verify remote exists before pushing
7. Show summary of all commits made
