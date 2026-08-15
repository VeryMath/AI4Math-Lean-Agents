# Lean Agent Numina Skill

本目录是 **Cursor Skill 单源**。OpenCode 子 Agent 由仓库根 `scripts/sync_opencode_agent.*` 覆盖生成，勿手改 `.opencode/agents/numina-lean-agent.md`。

完整愿景与仓边界：仓库 [`docs/VISION.md`](../../../docs/VISION.md)。

## 组件

| 文件 | 用途 |
|------|------|
| `SKILL.md` | 阶段状态机、Mode A/C、命令模板 |
| `reference.md` | 启动清单、1211 树、LiteLLM/DeepSeek |
| `examples.md` | 可复制命令与汇报模板 |
| `install.ps1` / `install.sh` | 安装到 `~/.cursor/skills`；会先提示/调用 sync |

## 一键安装（先 sync）

改 `SKILL.md` 后必须先 sync。CI 跑 `bash ./scripts/sync_opencode_agent.sh --check`。日常：`.\scripts\ops_daily.ps1`（见 [`docs/OPS.md`](../../../docs/OPS.md)）。

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\sync_opencode_agent.ps1
powershell -ExecutionPolicy Bypass -File ".\.cursor\skills\lean-agent-numina\install.ps1"
```

```bash
bash ./scripts/sync_opencode_agent.sh
bash ./.cursor/skills/lean-agent-numina/install.sh
```

可选：`-SkipOpenCode` / `--skip-opencode` 只装 Skill。

## 认证（默认 Mode A，回退 Mode C）

| 模式 | 说明 |
|------|------|
| **A** | Gemini → LiteLLM（**WSL-only**）→ `ANTHROPIC_MODEL=anthropic-claude` → 映射 `gemini/gemini-2.5-pro` |
| **C** | DeepSeek Anthropic 兼容直连（`deepseek-v4-flash`） |
| B | Anthropic 直连（可选） |

禁止：模型名含 `[1m]`；localhost LiteLLM + deepseek 模型混用。详见 `reference.md` 与 [`docs/AUTH.md`](../../../docs/AUTH.md)。

环境变量模板：仓库 [`.env.example`](../../../.env.example)。

## 阶段状态机（摘要）

`Inspect → Workspace → Formalize → Prove/Fix → Verify → Memory`  
Verify **前移**使用 `lake env lean`；`max-model-tier` 可达 3，仍类别门控。

## 前置（WSL）

- Numina：`~/numina-lean-agent` + `.venv`
- Lean 项目：如 `/mnt/d/Lean/projects/stat-inference-lean`
- Mode A：本机 WSL 可跑 LiteLLM `:4000` + `GEMINI_API_KEY`

```bash
cd ~/numina-lean-agent && source .venv/bin/activate
python -m scripts.run_claude --help
```

## 最小跑通（Mode C 回退示例）

```bash
cd ~/numina-lean-agent
source .venv/bin/activate
export PYTHONPATH="$PWD"
export DEEPSEEK_API_KEY='你的key'
export ANTHROPIC_BASE_URL='https://api.deepseek.com/anthropic'
export ANTHROPIC_API_KEY="$DEEPSEEK_API_KEY"
export ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_API_KEY"
export ANTHROPIC_MODEL='deepseek-v4-flash'
python -m scripts.run_claude run \
  /mnt/d/Lean/projects/stat-inference-lean/StatInferenceLean/Exercises/InteractiveDemo.lean \
  --prompt-file "$HOME/numina-lean-agent/prompts/prompt_complete_file.txt" \
  --max-rounds 1 \
  --cwd /mnt/d/Lean/projects/stat-inference-lean
```

Mode A 示例见 `examples.md`。

## 安全

- 禁止把 API key 写入仓库文件。
- 终端历史若曾泄露 key，立即在提供商后台旋转。
