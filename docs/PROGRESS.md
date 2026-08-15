# PROGRESS — 目标 vs 现状（短、可执行）

> 主 KPI：**端到端成功率**（coding agent 闭环）。本文件不是教材进度看板。

## 真实目标（用户最初）

完整闭环 Skill，让 coding agent **结构化**完成 Lean 工程任务：

```text
Inspect → Workspace → Formalize → Prove/Fix → Verify → Memory
```

- 检查工程 / 配 workspace / 形式化 / 修证明 / 补 sorry / 本地验证
- 错题集 + 成功案例飞轮提高**自动化准确率**
- KPI = 任务从启动到 `lake env lean` / 证明通过的比例

## 已完成

| Phase | 内容 |
|-------|------|
| **0–2** | 愿景、Fixture（broken+fixed）、Skill 阶段机、Success/Error Bank 代码、类别门控 routing、eval 规格 |
| **3** | harness `--dry-run` / `--offline` 绿；Mode C DeepSeek 连通；单任务 T3 `run_claude` **SUCCESS**（~$0.54）；offline **6/6**；全量 `--real-api` 因 agent 误删 mathlib 中止并已恢复 |
| **4** | 工具护栏（禁 `.lake`/mathlib、`probe_auth`、disallowed rm/clone）+ 记忆闭环离线证明（pending→approve→active） |
| **5** | 冒烟习惯化（`ops_daily` / `smoke_verify.ps1`）、Skill↔OpenCode `--check`+CI、离线「命中后 prompt 含 minimal_diff」；真 API 短跑标为可选需批准 |

基线数字：[`BASELINE.md`](BASELINE.md)。认证：[`AUTH.md`](AUTH.md)。

## 当前最大准确度 / 自动化缺口

1. Agent 可 `rm -rf .lake/packages/mathlib` — Phase 4 护栏已上（prompt 禁 `.lake`/mathlib、`Bash(rm *)`/`git clone`、round 后完整性检查）
2. `~/.claude/settings.json` 曾指向智谱导致 **1211** — `probe_auth` abort；本机 settings 已是 DeepSeek
3. 记忆飞轮 pending→approve→active — 离线 unittest 已锁
4. 真任务上「命中后下一轮更准」— **离线**已证明命中后 prompt 含 `minimal_diff`；真 API 冷/热短跑仍需用户批准（[`OPS.md`](OPS.md)）

## Phase 4 必须服务该目标

不是再写教材。交付：

- **护栏**：禁止碰 `.lake` / mathlib / toolchain / lakefile；round 内不用全仓 `lake build`；禁止 Mode A/C 与智谱混用
- **记忆闭环**：verify pass → `pending_review` → `review --approve` → 检索只注入 `active`
- 剧本：[`MEMORY_LOOP.md`](MEMORY_LOOP.md)

## Phase 5（已落地：运维清单 + 对比协议）

交付见 [`OPS.md`](OPS.md)：

- 日常：`.\scripts\ops_daily.ps1` = sync `--check` + `smoke_verify.ps1`（elan PATH=`d:\Lean\elan\bin`）
- 改 Skill **必须** `scripts/sync_opencode_agent.ps1`；CI 跑 `--check`
- 准确度最小证明：**离线** retrieve-after-approve → prompt 含该条 `minimal_diff`（冷 prompt 不含）
- 真 API：settings 已是 DeepSeek 且护栏仍在，但上次短跑曾 ~22 分钟并 `rm` mathlib → **本 Phase 不烧 API**；冷/热 `--max-rounds 1` 仅在用户批准且 abort 门全绿时做

闭环（Inspect→Memory + Bank 门控）**可用**；「命中后真任务下一轮更准」仍欠一次经批准的短跑，不阻塞日常运维。
