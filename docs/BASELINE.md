# BASELINE — 端到端基线

> 主 KPI：端到端成功率。评测配额见 `eval/tasks.yaml`（`max_usd_per_run: 5`）。

## 记录元数据

| 字段 | 值 |
|------|-----|
| 日期 | 2026-08-14 |
| Mode | **C（DeepSeek 直连）** |
| 模型 | `deepseek-v4-flash` |
| max-rounds | 1（单任务冒烟）/ 5（套件配额） |
| max-model-tier | 1（单任务）/ 3（套件） |
| 备注 | 1211 已排除（原因为 `~/.claude/settings.json` 曾指向智谱）；单任务真 API 已通 |

## 套件结果

### A. 离线对照（`run_eval --offline`，无 API）

| 套件 | 任务数 | 成功 | 失败 | 成功率 | 成本 USD | 笔记 |
|------|--------|------|------|--------|----------|------|
| **合计（6 任务）** | 6 | 6 | 0 | **100%** | 0 | 2026-08-14 `run_eval --offline` |

### B. 真 API（Mode C）

| 任务 | 结果 | 轮次 | 成本 USD | 笔记 |
|------|------|------|----------|------|
| T1 InteractiveDemo | **pass** | 0 | 0 | 已编译，跳过 agent（自动评测） |
| T2 Week01 | **pass** | 0 | 0 | 已编译，跳过 agent（自动评测） |
| T3 ErrorBank broken→fix | **SUCCESS / COMPLETE** | 1 | **0.5351** | 人工确认的 `run_claude` 单任务；statement 曾改动后已 restore |
| T4 ErrorBank fixed | **pass**（冒烟） | 0 | 0 | `lake env lean` OK |
| T5 Bernoulli | **pass**（冒烟） | 0 | 0 | `lake env lean` OK |
| T6 Week02 | **pass**（冒烟） | 0 | 0 | 随 `lake build` OK |
| **合计（有效真 API 证明）** | — | — | **≈0.54**（仅 T3 烧额度） | 远低于 $5 硬顶 |

### C. 自动全量 `--real-api` 中断说明（2026-08-14）

自动跑到 T3 时，agent **偏离任务**，尝试：

```text
rm -rf .lake/packages/mathlib && git clone mathlib4
```

导致 mathlib 包损坏；已中止进程，并用镜像重新 clone + `lake exe cache get` 恢复；`smoke_verify.ps1` 再次全绿。  
**结论**：API/认证正常；全自动 fix 任务仍需 Phase 4 加固（禁止改 `.lake/`、限制工具范围）。

### 复跑命令

```bash
cd ~/numina-lean-agent && source .venv/bin/activate && export PYTHONPATH=$PWD
set -a && source .env && set +a

# 离线
python -m scripts.run_eval --offline \
  --config /mnt/d/Lean/projects/stat-inference-lean/eval/tasks.yaml \
  --project-root /mnt/d/Lean/projects/stat-inference-lean

# 真 API（$5 硬顶）— 建议先确认 ~/.claude/settings.json 的 BASE_URL 是 deepseek
python -m scripts.run_eval --real-api --auth-mode C \
  --config /mnt/d/Lean/projects/stat-inference-lean/eval/tasks.yaml \
  --project-root /mnt/d/Lean/projects/stat-inference-lean
```

## 编译冒烟（无 API，2026-08-14 恢复后）

| 目标 | 期望 | 实测 |
|------|------|------|
| `lake build` | 通过 | **通过**（8033 jobs） |
| InteractiveDemo | 通过 | **通过** |
| ErrorBank fixed | 通过 | **通过** |
| Bernoulli | 通过 | **通过** |
| ErrorBank broken | **失败** | **按预期失败** |

## 变更相对上次

- 上次：真 API 阻塞（无 key）
- 本次：Mode C 连通；单任务 T3 **SUCCESS**；全量自动评测因 agent 误伤 mathlib 中止并已恢复环境
- 下一优先（Phase 4）：工具护栏 + pending_review→active 闭环演示，避免再改 `.lake/packages`
