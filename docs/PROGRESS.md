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

基线数字：[`BASELINE.md`](BASELINE.md)。认证：[`AUTH.md`](AUTH.md)。

## 当前最大准确度 / 自动化缺口（来自事故）

1. Agent 可 `rm -rf .lake/packages/mathlib` — **必须加工具护栏**（Phase 4 A）
2. Claude 全局 `~/.claude/settings.json` 曾指向智谱导致 **1211** — 认证探测 / 覆盖必须文档化并在 runner 拦截（Phase 4 A）
3. 记忆飞轮未走通：`pending_review` → 人工审核 → `active` 检索命中（Phase 4 B）
4. Few-Shot / Success Bank 尚未在真任务上证明「命中后下一轮更准」（Phase 4 用离线测试锁门控；真 API 证明留给护栏确认后的短跑）

## Phase 4 必须服务该目标

不是再写教材。交付：

- **护栏**：禁止碰 `.lake` / mathlib / toolchain / lakefile；round 内不用全仓 `lake build`；禁止 Mode A/C 与智谱混用
- **记忆闭环**：verify pass → `pending_review` → `review --approve` → 检索只注入 `active`
- 剧本：[`MEMORY_LOOP.md`](MEMORY_LOOP.md)

## Phase 5（尚未做）

稳态运维：冒烟脚本进习惯、Skill↔OpenCode 同步纪律、护栏确认后的基线对比（短 `--max-rounds 1`，禁止再毁 mathlib）。
