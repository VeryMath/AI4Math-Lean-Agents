#!/usr/bin/env bash
set -euo pipefail

SKIP_OPENCODE="${1:-}"

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/../../.." && pwd)"

skill_source_dir="$script_dir"
skill_target_dir="$HOME/.cursor/skills/lean-agent-numina"

sync_script="$project_root/scripts/sync_opencode_agent.sh"
agent_source_file="$project_root/.opencode/agents/numina-lean-agent.md"
agent_target_dir="$HOME/.opencode/agents"
agent_target_file="$agent_target_dir/numina-lean-agent.md"

echo "[lean-agent-numina] Source skill: $skill_source_dir"
echo "[lean-agent-numina] Target skill: $skill_target_dir"

if [[ "$SKIP_OPENCODE" != "--skip-opencode" ]]; then
  if [[ -f "$sync_script" ]]; then
    echo "[lean-agent-numina] Running sync_opencode_agent.sh ..."
    bash "$sync_script"
  else
    echo "[lean-agent-numina] WARN: sync script missing ($sync_script). Run sync before install."
  fi
fi

mkdir -p "$skill_target_dir"
cp -R "$skill_source_dir/"* "$skill_target_dir/"
echo "[lean-agent-numina] Copied skill files."

if [[ "$SKIP_OPENCODE" == "--skip-opencode" ]]; then
  echo "[lean-agent-numina] --skip-opencode enabled. OpenCode agent copy skipped."
else
  if [[ -f "$agent_source_file" ]]; then
    mkdir -p "$agent_target_dir"
    cp "$agent_source_file" "$agent_target_file"
    echo "[lean-agent-numina] Copied OpenCode agent file."
  else
    echo "[lean-agent-numina] OpenCode agent file not found: $agent_source_file"
    echo "[lean-agent-numina] Skill is installed. Run scripts/sync_opencode_agent.sh first."
  fi
fi

echo "[lean-agent-numina] Install complete."
echo "Next:"
echo "1) Restart Cursor (or run: Developer: Reload Window)"
echo "2) Verify skill files in: $skill_target_dir"
if [[ "$SKIP_OPENCODE" != "--skip-opencode" ]]; then
  echo "3) Verify OpenCode agent in: $agent_target_file"
fi
