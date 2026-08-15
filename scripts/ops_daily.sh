#!/usr/bin/env bash
# Phase 5 daily ops: Skill↔OpenCode sync check, then smoke_verify.
# Does NOT call the LLM. Live short-run is opt-in (see docs/OPS.md).
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/.." && pwd)"
cd "$project_root"

echo "==> Skill <-> OpenCode sync check"
bash "$script_dir/sync_opencode_agent.sh" --check

echo
echo "==> smoke_verify"
bash "$script_dir/smoke_verify.sh"

echo
echo "ops_daily: sync check + smoke passed."
echo "Live API short-run is NOT included. Abort unless docs/OPS.md gate is green AND the user approved."
