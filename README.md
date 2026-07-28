# Stat Inference Lean — Agent 测试床

本仓库是 **Lean 自动证明 Agent 的测试床 / 语料 / Skill 载体**，不是「只教你装环境」的安装页。

核心闭环与 KPI 见 **[`docs/VISION.md`](docs/VISION.md)**。  
调用规则以 Cursor Skill 为单源：[`/.cursor/skills/lean-agent-numina/`](.cursor/skills/lean-agent-numina/)。

## 本仓提供什么

| 资产 | 路径 | 说明 |
|------|------|------|
| Skill（主源） | `.cursor/skills/lean-agent-numina/` | 阶段状态机、认证 Mode A/C、排障 |
| OpenCode Agent（派生） | `.opencode/agents/numina-lean-agent.md` | 由 sync 脚本从 Skill **覆盖生成** |
| Fixture | `StatInferenceLean/Exercises/Fixtures/` | ErrorBank `broken` / `fixed` |
| 冒烟 / Formalize 靶 | `Exercises/InteractiveDemo.lean` | 可进默认 build |
| 回归集说明 | [`docs/REGRESSION.md`](docs/REGRESSION.md) | 含 Bernoulli 单独 lean |
| 评测规格 | [`eval/tasks.yaml`](eval/tasks.yaml) | 6 任务，$5/run 封顶 |
| Success Bank 架构 | [`docs/SUCCESS_BANK.md`](docs/SUCCESS_BANK.md) | 实现在 Phase 2（numina 仓） |

Runner / Error Bank **代码** 在 `~/numina-lean-agent`（本 Phase 不改 Python；见 VISION 仓边界）。

## 快速开始（文档入口）

1. 读愿景：[`docs/VISION.md`](docs/VISION.md)  
2. 读 Skill：[`SKILL.md`](.cursor/skills/lean-agent-numina/SKILL.md) · [`reference.md`](.cursor/skills/lean-agent-numina/reference.md) · [`examples.md`](.cursor/skills/lean-agent-numina/examples.md)  
3. 认证模板：[`.env.example`](.env.example) · [`docs/AUTH.md`](docs/AUTH.md)  
4. 改 Skill 后同步 OpenCode Agent：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\sync_opencode_agent.ps1
```

```bash
bash ./scripts/sync_opencode_agent.sh
```

5. （可选）安装 Skill 到用户目录 — **先 sync**：

```powershell
powershell -ExecutionPolicy Bypass -File ".\.cursor\skills\lean-agent-numina\install.ps1"
```

```bash
bash ./.cursor/skills/lean-agent-numina/install.sh
```

## 认证默认（摘要）

- **Mode A（默认）**：Gemini → LiteLLM（**WSL-only**）→ `ANTHROPIC_MODEL=anthropic-claude`（映射 `gemini/gemini-2.5-pro`）
- **Mode C（回退）**：DeepSeek Anthropic 兼容直连
- 禁止：模型名带 `[1m]`；`BASE_URL=localhost` 却 `MODEL=deepseek*`
- 1211 排障树见 Skill `reference.md`

## 冒烟验证（不依赖 API）

```powershell
# 需 lake 在 PATH（如 d:\Lean\elan\bin）
lake build
lake env lean StatInferenceLean/Exercises/InteractiveDemo.lean
lake env lean StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.fixed.lean
lake env lean StatInferenceLean/Exercises/Bernoulli.lean
# broken 预期失败：
lake env lean StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.broken.lean
```

或：`.\scripts\smoke_verify.ps1` / `bash ./scripts/smoke_verify.sh`

## 仓边界一句话

- **本仓**：语料、Fixture、Skill、评测 YAML、文档  
- **numina-lean-agent**：runner、bank 实现、routing（Phase 2+）
