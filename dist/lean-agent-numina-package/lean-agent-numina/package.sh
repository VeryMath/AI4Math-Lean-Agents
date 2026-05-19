#!/usr/bin/env bash
set -euo pipefail

output_dir="${1:-./dist}"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/../../.." && pwd)"

source_skill_dir="$script_dir"
source_agent_file="$project_root/.opencode/agents/numina-lean-agent.md"

mkdir -p "$output_dir"
stage_dir="$output_dir/lean-agent-numina-package"
rm -rf "$stage_dir"
mkdir -p "$stage_dir/lean-agent-numina"

cp -R "$source_skill_dir/"* "$stage_dir/lean-agent-numina/"

if [[ -f "$source_agent_file" ]]; then
  mkdir -p "$stage_dir/.opencode/agents"
  cp "$source_agent_file" "$stage_dir/.opencode/agents/numina-lean-agent.md"
fi

cat > "$stage_dir/README_INSTALL.md" <<'EOF'
# Lean Agent Numina 分发包

## 内容

- `lean-agent-numina/`：Cursor Skill 全部文件
- `.opencode/agents/numina-lean-agent.md`：OpenCode 子 Agent 定义（若包含）

## 安装（Windows）

1. 解压 zip
2. 在解压目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File ".\lean-agent-numina\install.ps1"
```

## 安装（WSL/Linux/macOS）

1. 解压 zip
2. 在解压目录执行：

```bash
bash ./lean-agent-numina/install.sh
```
EOF

python3 - <<'PY' "$output_dir"
import pathlib
import sys
import zipfile

out_dir = pathlib.Path(sys.argv[1]).resolve()
src_dir = out_dir / "lean-agent-numina-package"
zip_path = out_dir / "lean-agent-numina-package.zip"
if zip_path.exists():
    zip_path.unlink()
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in src_dir.rglob("*"):
        if path.is_file():
            zf.write(path, path.relative_to(out_dir))
PY

echo "[lean-agent-numina] Package created: $output_dir/lean-agent-numina-package.zip"
echo "[lean-agent-numina] You can send this zip directly."
