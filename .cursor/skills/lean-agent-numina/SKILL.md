---
name: lean-agent-numina
description: 在 Lean 项目中按阶段状态机调用 Numina Lean Agent（run_claude / run_eval）。课题组默认 Gemini+LiteLLM（Mode A）；国内个人开发者实操优先 DeepSeek 直连（Mode C）。用户提到 numina、lean agent、run_claude、run_eval、from-folder、batch proof、mcp、litellm、error bank 时使用。
disable-model-invocation: true
---

# Lean Agent Numina

## 适用场景

- 用户要「调用 Lean agent / Numina」。
- 用户提到 `python -m scripts.run_claude`、`from-folder`、`batch`、`MCP`、Error Bank。
- 需要在 WSL + Lean 项目中跑自动证明 / Formalize 工作流。

## 执行原则

- 仅在目标 Lean 项目内执行（祖先目录有 `lean-toolchain` 与 `lakefile.toml`/`lakefile.lean`）。
- 不在命令中硬编码明文 key；只用环境变量。
- 每一步输出：`[check] <item> | pass/fail` 与 `[next action] <一条命令>`。
- **验证前移**：能 `lake env lean <file>` 的先做单文件验证，再扩大到 `lake build` / 多轮 LLM。
- 主 KPI：端到端成功率；成本次要。
- OpenCode agent 文件由 `scripts/sync_opencode_agent.*` 从本 Skill **生成**；改规则先改本目录再 sync。

## 阶段状态机（强制）

```text
Inspect → Workspace → Formalize → Prove/Fix → Verify → Memory
```

| 阶段 | 做什么 | 成功标准 | 退出条件（进入下一阶段或停） |
|------|--------|----------|------------------------------|
| **Inspect** | 确认目标文件/定理、项目根、是否 broken fixture | 路径在可构建项目内；明确目标类型 | 缺 lakefile / 目标不明 → 停并给出修复命令 |
| **Workspace** | 检查 WSL/venv/lake、选认证模式、MCP 作用域 | Mode A 或 C 可用；`run_claude --help` 过 | 鉴权/代理失败 → 按 Mode C 回退或停 |
| **Formalize** | 自然语言 → `.lean`（如 InteractiveDemo）或确认已有陈述 | 文件含 theorem/example 与 `by` 骨架 | 用户只要检查环境则可跳到 Verify |
| **Prove/Fix** | `run_claude` 迭代；Error Bank tier0 → few-shot → 升 tier | 本轮产出可编译候选或明确错误类 | 达 `max-rounds` / 配额 / 不可修类别 → 停 |
| **Verify** | **优先** `lake env lean <file>`；必要时 `lake build` | 退出码 0；无 sorry（按任务约定） | 失败 → 回 Prove/Fix（计数 +1） |
| **Memory** | verify pass 写 Success/Error（均 `pending_review`）；人工 `review --approve` 后才进检索 | 只注入 `active`；`pending_review` / `fixed_code=null` 不进 Few-Shot | 会话结束 |

类别门控：`--max-model-tier` 默认可到 **3**，但按错误类别封顶（见 [`docs/MODEL_ROUTING.md`](../../../docs/MODEL_ROUTING.md)）；同诊断指纹无效重试 ≤1。

## 认证模式

> **国内个人（仅国内 API）→ 先 Mode C。** 课题组默认叙事 → Mode A；A 失败再回退 C。勿 A/C 混用。

### Mode C（国内实操推荐 / 回退）：DeepSeek 直连

**可跳过 LiteLLM。** 密钥只放 `.env`（gitignore）。

```bash
export DEEPSEEK_API_KEY="..."
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_API_KEY="$DEEPSEEK_API_KEY"
export ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_API_KEY"
export ANTHROPIC_MODEL="deepseek-v4-flash"
```

### Mode A（课题组默认）：Gemini + LiteLLM

- **LiteLLM：WSL-only**。
- 模型别名：`ANTHROPIC_MODEL=anthropic-claude` → LiteLLM 映射 `gemini/gemini-2.5-pro`。

```bash
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="sk-anything"
export ANTHROPIC_MODEL="anthropic-claude"
# 上游：GEMINI_API_KEY 配在 LiteLLM 进程环境
```

### Mode B（可选）：Anthropic 直连

```bash
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
export ANTHROPIC_AUTH_TOKEN="<your-anthropic-key>"
export ANTHROPIC_MODEL="claude-opus-4-7"
```

### 硬性禁止

- 模型名带 `[1m]` 或其它 ANSI/脏字符。
- `BASE_URL=http://localhost:4000` 却设置 `MODEL=deepseek*`（Mode A/C 混用）。
- `~/.claude/settings.json` 指向智谱 / GLM / `bigmodel.cn` 却跑 DeepSeek（1211）。
- **禁止操作（准确度护栏）**：修改/删除 `.lake/`、`mathlib`、`lean-toolchain`、lakefile（除非 Workspace 阶段且用户明确要求）；round 内用全仓 `lake build` 当验证；`rm -rf` / `git clone mathlib` 当「修复」。

`run_claude` 会：`--disallowed-tools Bash(rm *)` 等、`--append-system-prompt` 硬约束、启动 `probe_auth`、round 后检查 mathlib 是否还在。

### 启动检查清单

见 [reference.md](reference.md)「启动检查清单」与「1211 排障树」；摘要见仓库 [`docs/AUTH.md`](../../../docs/AUTH.md)。

## Phase 3 评测（$5 硬顶）

```bash
cd ~/numina-lean-agent && source .venv/bin/activate && export PYTHONPATH=$PWD
python -m scripts.run_eval --dry-run --config <lean>/eval/tasks.yaml
python -m scripts.run_eval --offline --config <lean>/eval/tasks.yaml --project-root <lean>
# 有 key 后（国内推荐 C）：
python -m scripts.run_eval --real-api --auth-mode C \
  --config <lean>/eval/tasks.yaml --project-root <lean>
```

基线填数：[`docs/BASELINE.md`](../../../docs/BASELINE.md)。

## run_claude 命令模板

在 `~/numina-lean-agent`（`source .venv`，`PYTHONPATH=$PWD`）：

```bash
python -m scripts.run_claude run <target_lean_file> \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 5 \
  --cwd <lean_project_root> \
  --max-model-tier 3 \
  --success-bank true
# 关闭记忆飞轮：--no-error-bank  或  --success-bank false
```

```bash
python -m scripts.run_claude from-folder <target_folder> \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 5 \
  --cwd <lean_project_root>
```

```bash
python -m scripts.run_claude batch <config_yaml> --parallel --max-workers 4
```

验证前移示例：

```bash
lake env lean <target_lean_file>
```

## Error Bank / Success Bank（默认启用）

- Error：`<lean_project_root>/.lean-error-bank/`；Success：`.lean-success-bank/`（均 gitignore）
- 默认开 Error Bank + Success Bank；关闭：`--no-error-bank` / `--success-bank false`
- 入库默认 `pending_review`；检索 **只取 `active`**；`fixed_code=null` 禁止进 Few-Shot
- Few-Shot：优先 Success **最小 diff**；Error 只给短策略
- 闭环剧本：[`docs/MEMORY_LOOP.md`](../../../docs/MEMORY_LOOP.md)；进度：[`docs/PROGRESS.md`](../../../docs/PROGRESS.md)
- Fixture：`Exercises/Fixtures/ErrorBankDemo.broken.lean` + `.fixed.lean`（broken 勿 import 进根模块）
- 路由：[`docs/MODEL_ROUTING.md`](../../../docs/MODEL_ROUTING.md)；Success：[`docs/SUCCESS_BANK.md`](../../../docs/SUCCESS_BANK.md)

```bash
python -m scripts.error_bank --bank_dir .lean-error-bank list
python -m scripts.error_bank --bank_dir .lean-error-bank review <id> --approve
python -m scripts.error_bank success --bank_dir .lean-success-bank list
python -m scripts.error_bank success --bank_dir .lean-success-bank review <id> --approve
python -m scripts.error_bank --bank_dir .lean-error-bank stats
```

## 输出规范

```text
[check] stage=Inspect | pass
[check] auth Mode A litellm | fail
[next action] 切换 Mode C：export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic ...
```

## 额外资料

- [reference.md](reference.md) — 排障、1211、LiteLLM、flags
- [examples.md](examples.md) — 可复制会话与命令
- 愿景：[docs/VISION.md](../../../docs/VISION.md)
- 进度复盘：[docs/PROGRESS.md](../../../docs/PROGRESS.md)
- 记忆闭环：[docs/MEMORY_LOOP.md](../../../docs/MEMORY_LOOP.md)
- 路由：[docs/MODEL_ROUTING.md](../../../docs/MODEL_ROUTING.md)
- Success Bank：[docs/SUCCESS_BANK.md](../../../docs/SUCCESS_BANK.md)
