# VISION — Lean Agent 测试床闭环

> 本仓库是 **测试床 / 语料 / Skill 载体**，不是教材进度看板。  
> 主 KPI：**端到端成功率**（成本次要）。

## 1. 闭环六阶段

| 阶段 | 名称 | 目标 | 本仓角色 |
|------|------|------|----------|
| 0 | 愿景与单源文档 | 锁定 KPI、认证、仓边界 | `docs/` + Skill |
| 1 | Fixture / 语料 | broken+fixed、回归集、评测规格 | Exercises / eval / docs |
| 2 | Runner / Bank 实现 | Error Bank 强化、Success Bank 代码、routing | 主改 `~/numina-lean-agent` |
| 3 | 评测跑通 | 6 任务真 API（$5/run 封顶） | `eval/` + runner |
| 4 | 记忆闭环 | pending_review → 审核入库 → 检索命中 | success/error bank |
| 5 | 稳态运维 | 冒烟、同步 Skill↔OpenCode、基线对比 | scripts + CI 可选 |

状态机（Agent 单次任务，见 Skill）：

```text
Inspect → Workspace → Formalize → Prove/Fix → Verify → Memory
```

## 2. KPI（锁定）

| KPI | 定义 | 备注 |
|-----|------|------|
| **主 KPI** | 端到端成功率 | 任务从启动到 `lake env lean` / 证明通过的比例 |
| 次要 | 轮次、耗时、美元成本 | 不牺牲成功率去压成本 |
| **暂停** | 教材进度 KPI | Phase 0–1 全力 Fixture/语料 |

基线填数见 [`BASELINE.md`](BASELINE.md)。回归清单见 [`REGRESSION.md`](REGRESSION.md)。

## 3. 仓边界

| 仓 | 职责 |
|----|------|
| **本仓** `stat-inference-lean` | Lean 语料、Fixture、Cursor Skill、OpenCode 同步、评测规格与文档 |
| **`~/numina-lean-agent`** | `run_claude` runner、error_bank / success_bank **代码实现**、routing |

> Phase 0–1：**只改本仓**文档 / Skill / Fixture。若本机无 numina 仓或不可写，Python 改动标为 **Phase 2**。

## 4. 认证（锁定）

| 模式 | 用途 | 要点 |
|------|------|------|
| **Mode A（课题组默认叙事）** | Gemini + LiteLLM | `ANTHROPIC_MODEL=anthropic-claude` → LiteLLM 映射 `gemini/gemini-2.5-pro`；**LiteLLM 仅 WSL** |
| **Mode C（国内实操推荐 / 回退）** | DeepSeek 直连 | `ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic`，`MODEL=deepseek-v4-flash`（或 pro）；**可跳过 LiteLLM** |
| Mode B（可选） | Anthropic 直连 | 非默认 |

> 国内个人开发者（仅国内 API 可买）**先配 Mode C**；课题组文档默认仍写 Mode A。详见 [`AUTH.md`](AUTH.md)。

硬性禁止：

- 模型名带 ANSI/`[1m]` 等脏字符
- `BASE_URL=localhost`（LiteLLM）却设 `MODEL=deepseek*`（混用 Mode A/C）

排障见 Skill [`reference.md`](../.cursor/skills/lean-agent-numina/reference.md)（含 **1211** 树）与 [`AUTH.md`](AUTH.md)。

## 5. Fixture 与 Bank

- **ErrorBankDemo**：`broken` + `fixed` 双文件；broken **不**进根模块 import（避免 `lake build` 失败）。
- **Bernoulli**：不写入 `StatInferenceLean.lean` 默认 import；回归集单独 `lake env lean`。
- **Success Bank**：架构独立（[`SUCCESS_BANK.md`](SUCCESS_BANK.md)）；物理可复用 fixed 语料；入库默认 `pending_review`。实现：`~/numina-lean-agent`（Phase 2 已落地）。

## 6. 评测配额

- 任务数：**恰好 6**（[`eval/tasks.yaml`](../eval/tasks.yaml)）
- **`max_usd_per_run: 5`**（harness 硬顶；另封顶 rounds / tier）
- Phase 3 入口：`python -m scripts.run_eval --dry-run` / `--offline` / `--real-api [--auth-mode C]`
- 基线填数：[`BASELINE.md`](BASELINE.md)

## 7. 文档单源

- **主源**：`.cursor/skills/lean-agent-numina/`（Cursor Skill）
- **派生**：`.opencode/agents/numina-lean-agent.md` 由 `scripts/sync_opencode_agent.*` 覆盖生成（文件头 **DO NOT EDIT**）
- 改 Skill 后必须先 sync，再 install / 使用 OpenCode

## 8. 里程碑

| 里程碑 | 完成标准 |
|--------|----------|
| M0 | VISION / README / Skill 认证与阶段机 / `.env.example` |
| M1 | broken+fixed、REGRESSION、sync 脚本、tasks.yaml、SUCCESS_BANK 文档 |
| M2 | numina 仓：Success Bank 代码、类别门控 routing、eval runner |
| M3 | harness `--dry-run` 绿 + `--real-api` 入口与 $5 硬顶；有 key 则 6 任务填 BASELINE，无 key 则记录阻塞与复跑命令 |

## 9. 决策摘要（已拍板）

1. 主 KPI = 端到端成功率  
2. 认证：课题组默认 Mode A，失败回退 Mode C；国内个人实操推荐先 C；LiteLLM WSL-only  
3. Phase 0–1 只动 Lean 仓文档/Skill/Fixture  
4. ErrorBankDemo → broken + fixed  
5. Bernoulli 不进默认 import  
6. Success Bank 本 Phase 仅文档  
7. 评测 6 任务 + $5/run  
8. 暂停教材进度 KPI  
9. Skill 单源 + sync 生成 OpenCode agent  
10. 方案 A+C：阶段化 Skill；验证前移 `lake env lean`；`max-model-tier` 可达 3，仍类别门控  
