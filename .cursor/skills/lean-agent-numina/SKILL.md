---
name: lean-agent-numina
description: 在 Lean 项目中安装与调用 Numina Lean Agent（run_claude），支持 Gemini+LiteLLM 代理链路与 Anthropic 直连。用户提到 numina、lean agent、run_claude、from-folder、batch proof、mcp、litellm 时使用。
disable-model-invocation: true
---

# Lean Agent Numina

## 适用场景

- 用户要“调用 Lean agent / Numina”。
- 用户提到 `python -m scripts.run_claude`、`from-folder`、`batch`、`MCP`。
- 需要在 WSL + Lean 项目中跑自动证明工作流。

## 执行原则

- 仅在目标 Lean 项目内执行（祖先目录必须有 `lean-toolchain` 与 `lakefile.toml`/`lakefile.lean`）。
- 不在命令中硬编码明文 key；只用环境变量。
- 每一步都输出检查点：`[check] [pass/fail] [next action]`。
- 出现阻塞时优先给“最小可执行修复命令”。

## 标准流程（强制顺序）

1. **项目可构建性检查**
   - 检查目标文件是否在 Lean 项目内。
   - 必要时提示先跑：`lake build`。

2. **运行环境检查**
   - 检查 `wsl`、`uv`、`claude`、`python`、`lake`。
   - 若在 WSL，检查代理连通（如 `curl -I https://github.com`）。

3. **认证模式选择**
   - 模式 A（默认）：Gemini -> LiteLLM -> Anthropic-compatible -> Numina。
   - 模式 B（备选）：Anthropic 直连。
   - 若两者都可用，优先模式 A（与当前项目路线一致）。

4. **MCP 作用域检查**
   - 必须在目标 Lean 项目目录执行 `claude mcp add ...`。
   - 用 `claude mcp list`确认连接状态。

5. **运行 numina 命令**
   - 单文件：`run`
   - 文件夹：`from-folder`
   - 批量配置：`batch`

6. **失败即分流排障**
   - 401 鉴权错误
   - 代理不可达
   - MCP 目录作用域错误
   - `lake=fail`（目标不在可构建 Lean 项目内）

## 模式 A：Gemini + LiteLLM（默认）

### 先决条件

- 已有 `GEMINI_API_KEY`（或团队网关上游 key）。
- LiteLLM 可在本机启动并监听 `localhost:4000`。

### 变量模板

```bash
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="sk-anything"
export ANTHROPIC_MODEL="anthropic-claude"
```

### 关键检查

- `curl -s http://localhost:4000/v1/messages ...` 返回 JSON 正常。
- `run_claude` 启动后不再出现 `AuthenticationError`。

## 模式 B：Anthropic 直连

### 变量模板

```bash
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
export ANTHROPIC_AUTH_TOKEN="<your-anthropic-key>"
export ANTHROPIC_MODEL="claude-opus-4-7"
```

### 关键检查

- `claude` 命令可正常鉴权。
- `run_claude run ...` 可进入 round 循环。

## run_claude 命令模板

### 单文件

```bash
python -m scripts.run_claude run <target_lean_file> \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 5 \
  --cwd <lean_project_root>
```

### 文件夹

```bash
python -m scripts.run_claude from-folder <target_folder> \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 5 \
  --cwd <lean_project_root>
```

### 批量配置

```bash
python -m scripts.run_claude batch <config_yaml> --parallel --max-workers 4
```

## 输出规范（实时汇报）

每个关键步骤都按以下格式汇报：

```text
[check] proxy connectivity | pass
[check] mcp in project scope | fail
[next action] 在目标项目目录执行 `claude mcp add ...`
```

## 常见错误 -> 立即动作

- `AuthenticationError`：检查上游 key 格式、有效性与环境变量是否在当前终端生效。
- `Failed to connect`：检查 WSL 代理地址/端口、`NO_PROXY` 是否包含 `localhost,127.0.0.1`。
- `mcp not connected`：在目标项目目录重新 `claude mcp add`。
- `lake=fail`：目标文件不在可构建 Lean 项目内，先切到含 `lakefile` 的目录。

## 额外资料

- 详细排障命令见 [reference.md](reference.md)
- 常用会话模板见 [examples.md](examples.md)
