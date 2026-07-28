# BASELINE — 端到端基线模板

> 主 KPI：端到端成功率。数字可先空着，跑完评测再填。  
> 评测配额见 `eval/tasks.yaml`（`max_usd_per_run: 5`）。

## 记录元数据

| 字段 | 值 |
|------|-----|
| 日期 | 2026-07-24 |
| Mode | （真 API 未跑；下列为离线冒烟） |
| 模型 | n/a（offline） |
| max-rounds | n/a |
| max-model-tier | 3（代码默认；类别门控见 MODEL_ROUTING） |
| 备注 | Phase 2 落地后离线基线；真 API 6 任务属 Phase 3 |

## 套件结果

| 套件 | 任务数 | 成功 | 失败 | 成功率 | 轮次均值 | 成本 USD | 笔记 |
|------|--------|------|------|--------|----------|----------|------|
| InteractiveDemo（Formalize/冒烟） | 1 | （见下表） | | | | 0 | offline env lean |
| Week01 子集 | 1 | | | | | 0 | 真 API 未跑 |
| ErrorBank **broken→fixed** | 1 | offline：broken 失败 + fixed 通过 | | | | 0 | 无 agent 修复轮 |
| Bernoulli（单独 lean） | 1 | （见下表） | | | | 0 | |
| Week02 子集（可选） | 1 | | | | | 0 | 真 API 未跑 |
| **合计（对齐 6 任务评测）** | 6 | | | | | ≤5 | 填 Phase 3 |

## 编译冒烟（无 API）

| 目标 | 命令 | 期望 | 实测 |
|------|------|------|------|
| 全仓 | `lake build` | 通过 | **通过**（2026-07-24，`smoke_verify.ps1`） |
| InteractiveDemo | `lake env lean …/InteractiveDemo.lean` | 通过 | **通过** |
| ErrorBank fixed | `lake env lean …/ErrorBankDemo.fixed.lean` | 通过 | **通过** |
| Bernoulli | `lake env lean …/Bernoulli.lean` | 通过 | **通过** |
| ErrorBank broken | `lake env lean …/ErrorBankDemo.broken.lean` | **失败** | **按预期失败** |

## Phase 2 代码冒烟（numina）

```bash
cd ~/numina-lean-agent && PYTHONPATH=$PWD \
  python -m unittest scripts.error_bank.tests.test_error_bank scripts.error_bank.tests.test_integration -v
# 实测 2026-07-24：20 tests OK（门控 / Success Bank / 路由 / auto_fix）
```

```bash
python -m scripts.run_eval --dry-run --config …/eval/tasks.yaml
# 解析 6 任务 + max_usd_per_run=5
```

## 变更相对上次

- 上次基线日期：Phase 0–1 文档模板
- 成功率 Δ：n/a（尚无真 API）
- 主要回归 / 修复：Success Bank + 类别门控 + pending_review 检索门控
