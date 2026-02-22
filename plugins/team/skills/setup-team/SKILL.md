---
name: setup-team
description: "Agent Teams機能を有効化するための設定セットアップ。~/.claude/settings.jsonにCLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1を追加する。teamスキルを使う前に一度だけ実行する。"
---

# Agent Teams セットアップ

`team` スキルを使うには `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` が必要です。このスキルはその設定を自動追加します。

## 実行手順

1. **現在の設定を確認**:

   ```bash
   cat ~/.claude/settings.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('env', {}).get('CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS', 'not set'))"
   ```

2. **未設定の場合、セットアップスクリプトを実行**:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup-team-env.sh"
   ```

3. **実行後の確認**:

   ```bash
   cat ~/.claude/settings.json | python3 -c "import json,sys; d=json.load(sys.stdin); v=d.get('env',{}).get('CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS'); print('✅ 設定済み:', v) if v=='1' else print('❌ 未設定')"
   ```

4. **Claude Code を再起動** して設定を反映させる。

## 完了後

`/team` コマンドでチームを起動できます。

```
/team
```

## 注意事項

- この設定はグローバル設定（`~/.claude/settings.json`）に追加されます
- すべてのプロジェクトでAgent Teams機能が有効になります
- 無効化したい場合は `~/.claude/settings.json` の `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` を削除してください
