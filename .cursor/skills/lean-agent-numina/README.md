# Lean Agent Numina Skill 使用说明

本说明用于当前项目内的 `lean-agent-numina` 技能，目标是让你稳定调用 `project-numina/numina-lean-agent` 完成 Lean 自动证明任务。

## 0. 一键安装给别人（新电脑）

这套 Skill 已支持一键安装。把整个项目目录发给对方（或让对方 `git clone` 后进入项目根目录），执行以下命令即可：

### Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File ".\.cursor\skills\lean-agent-numina\install.ps1"
```

### WSL / Linux / macOS

```bash
bash ./.cursor/skills/lean-agent-numina/install.sh
```

执行后会自动完成：

- 安装 Skill 到 `~/.cursor/skills/lean-agent-numina`
- 安装 OpenCode 子 Agent 到 `~/.opencode/agents/numina-lean-agent.md`（若项目内存在）

可选参数（仅安装 Skill，不安装 OpenCode 子 Agent）：

- PowerShell: `-SkipOpenCode`
- Bash: `--skip-opencode`

## 0.5 自动打包分发（导出 zip）

如果你要把 Skill 发给同学，推荐先导出标准分发包 zip。

### Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File ".\.cursor\skills\lean-agent-numina\package.ps1"
```

生成文件：`.\dist\lean-agent-numina-package.zip`

### WSL / Linux / macOS

```bash
bash ./.cursor/skills/lean-agent-numina/package.sh
```

生成文件：`./dist/lean-agent-numina-package.zip`

### 分发包内容

- `lean-agent-numina/`（包含 `SKILL.md`、`reference.md`、`examples.md`、安装脚本）
- `.opencode/agents/numina-lean-agent.md`（如果项目中存在）
- `README_INSTALL.md`（给接收方的安装说明）

## 1. 组件关系（先看这个）

- `SKILL.md`：给 Cursor Skill 的主规则（何时触发、标准流程、检查点格式）。
- `reference.md`：详细排障和补充说明。
- `examples.md`：可直接复制的命令示例。
- `.opencode/agents/numina-lean-agent.md`：OpenCode 子 Agent 定义（用于 `opencode` 场景）。

结论：你已经同时具备「Cursor Skill」和「OpenCode 子 Agent」两条调用路径。

## 2. 前置条件

在 WSL 中确认以下项目存在：

- Numina 仓库：`~/numina-lean-agent`
- 虚拟环境：`~/numina-lean-agent/.venv`
- Lean 项目：`/mnt/d/Lean/projects/stat-inference-lean`

建议先执行：

```bash
cd ~/numina-lean-agent
source .venv/bin/activate
python --version
uv --version
```

## 3. LiteLLM 配置（DeepSeek 上游）

确保 `~/litellm_config.yaml` 内容如下：

```yaml
model_list:
  - model_name: anthropic-claude
    litellm_params:
      model: deepseek/deepseek-chat
      api_key: os.environ/DEEPSEEK_API_KEY
```

设置 key（不要写进仓库文件）：

```bash
export DEEPSEEK_API_KEY='sk-你的key'
```

## 4. 标准运行步骤（推荐双终端）

### 终端 A：启动 LiteLLM（常驻）

```bash
cd ~/numina-lean-agent
source .venv/bin/activate
export DEEPSEEK_API_KEY='sk-你的key'
~/numina-lean-agent/.venv/bin/litellm --config ~/litellm_config.yaml --port 4000
```

看到 `Uvicorn running on http://0.0.0.0:4000` 后，保持该终端不关闭。

### 终端 B：运行 Numina

```bash
cd ~/numina-lean-agent
source .venv/bin/activate
export PYTHONPATH="$PWD"
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="dummy"
export ANTHROPIC_MODEL="anthropic-claude"
```

先做基础可用性检查：

```bash
python -m scripts.run_claude --help
```

## 5. 三种任务执行方式

### 单文件（run）

```bash
python -m scripts.run_claude run \
  /mnt/d/Lean/projects/stat-inference-lean/StatInferenceLean/Exercises/Week01.lean \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 3 \
  --cwd /mnt/d/Lean/projects/stat-inference-lean
```

### 文件夹批量（from-folder）

```bash
python -m scripts.run_claude from-folder \
  /mnt/d/Lean/projects/stat-inference-lean/StatInferenceLean/Exercises \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 3 \
  --cwd /mnt/d/Lean/projects/stat-inference-lean
```

### 配置批量并行（batch）

```bash
python -m scripts.run_claude batch config/config_minif2f.yaml --parallel --max-workers 4
```

## 6. 如何通过 OpenCode 子 Agent 调用

在 WSL 进入 Lean 项目后执行：

```bash
cd /mnt/d/Lean/projects/stat-inference-lean
opencode
```

在会话里明确指令（示例）：

```text
调用 numina-lean-agent，目标文件是 StatInferenceLean/Exercises/Week01.lean。
请按 run_claude run 执行，max-rounds=1，并输出 [check]/[next action]。
```

## 7. 如何判定“真的跑通了”

至少同时满足以下 4 条：

- `run_claude --help` 成功（命令入口可用）。
- LiteLLM 正在监听 `:4000`。
- 子 Agent 输出出现 `run_claude run` 实际执行结果（不只是环境检查）。
- 无 `AuthenticationError`、无 `模型不存在`、无 `Connection refused`。

## 8. 常见问题与修复

- 现象：`Command 'wsl' not found`
  - 原因：你已经在 WSL 里了，还在 WSL 内再执行 `wsl`。
  - 修复：直接 `cd /mnt/d/Lean/projects/stat-inference-lean`。

- 现象：`模型不存在 (code 1211)`
  - 原因：`ANTHROPIC_MODEL=anthropic-claude` 未映射到真实上游模型。
  - 修复：检查 `~/litellm_config.yaml` 中 `model_name: anthropic-claude` 的映射。

- 现象：`401 Unauthorized`
  - 原因：上游 key 无效、过期或未导出到当前 shell。
  - 修复：重新 `export DEEPSEEK_API_KEY='sk-...'`，重启 LiteLLM。

- 现象：`Connection refused`（localhost:4000）
  - 原因：LiteLLM 没启动或被中断。
  - 修复：在终端 A 重启 LiteLLM 并保持常驻。

## 9. 安全建议

- 不要在仓库文件中写明文 API key。
- 如果 key 曾在终端历史中明文出现，建议立刻在提供商后台旋转并更换。
- 日志和截图中避免暴露完整 key。

## 10. 推荐最小验证命令（复制即用）

```bash
cd ~/numina-lean-agent && source .venv/bin/activate && export PYTHONPATH="$PWD" && export ANTHROPIC_BASE_URL="http://localhost:4000" && export ANTHROPIC_AUTH_TOKEN="dummy" && export ANTHROPIC_MODEL="anthropic-claude" && python -m scripts.run_claude run /mnt/d/Lean/projects/stat-inference-lean/StatInferenceLean/Exercises/Week01.lean --prompt-file prompts/prompt_complete_file.txt --max-rounds 1 --cwd /mnt/d/Lean/projects/stat-inference-lean
```

