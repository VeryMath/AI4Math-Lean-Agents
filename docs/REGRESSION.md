# REGRESSION — 回归与冒烟清单

不依赖 API 的编译回归。`broken` **不**加入 `StatInferenceLean.lean`，也不应被 `lake build` 拉取。

## 默认 build（应通过）

```text
lake build
```

根模块当前 import：Basic、Probability、Estimator、Week01、Week02、InteractiveDemo。  
**不含** Bernoulli、**不含** ErrorBank broken/fixed（fixed 亦建议单独 lean，避免与 Exercises 命名空间策略混淆时可按需调整；当前 fixed 为独立文件、未挂根模块）。

## 单文件 `lake env lean`（应通过）

| ID | 文件 | 角色 |
|----|------|------|
| R1 | `StatInferenceLean/Exercises/InteractiveDemo.lean` | 冒烟 / Formalize 靶 |
| R2 | `StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.fixed.lean` | Error Bank 正确对照 |
| R3 | `StatInferenceLean/Exercises/Bernoulli.lean` | 统计语料；**单独 lean，不进默认 import** |
| R4 | `StatInferenceLean/Exercises/Week01.lean` | 教材周次子集 |
| R5 | `StatInferenceLean/Exercises/Week02.lean` | 教材周次子集 |
| R6 | `StatInferenceLean/Exercises/Fixtures/InfinitelyManyPrimes.lean` | 素数无穷评测 Fixture；**不进根 import**；2026-08-16 已补全 |
| R7 | `StatInferenceLean/Exercises/Fixtures/StrictMonoComp.lean` | 严格单调复合；`exact hg.comp hf`；不进根 import |
| R8 | `StatInferenceLean/Exercises/Fixtures/DvdTrans.lean` | 整除传递；`exact dvd_trans`；不进根 import |
| R9 | `StatInferenceLean/Exercises/Fixtures/OddSquareMod8.lean` | 奇平方减 1 整除 8；`exact Int.eight_dvd_sq_sub_one_of_odd`；不进根 import |

`EvenSquare.lean` 为评测 Fixture，**当前仍 `sorry`**（2026-08-16 真 API 未闭环），**不要**当正例冒烟。详见 [`EVAL_FOUR.md`](EVAL_FOUR.md)。

命令示例（项目根，PATH 含 elan/lake）：

```powershell
lake env lean StatInferenceLean/Exercises/InteractiveDemo.lean
lake env lean StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.fixed.lean
lake env lean StatInferenceLean/Exercises/Bernoulli.lean
lake env lean StatInferenceLean/Exercises/Week01.lean
lake env lean StatInferenceLean/Exercises/Week02.lean
lake env lean StatInferenceLean/Exercises/Fixtures/InfinitelyManyPrimes.lean
lake env lean StatInferenceLean/Exercises/Fixtures/StrictMonoComp.lean
lake env lean StatInferenceLean/Exercises/Fixtures/DvdTrans.lean
lake env lean StatInferenceLean/Exercises/Fixtures/OddSquareMod8.lean
```

## 负例（应失败）

| ID | 文件 | 期望错误类 |
|----|------|------------|
| N1 | `StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.broken.lean` | `unknown identifier`（缺限定名 / 未 open） |

```powershell
lake env lean StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.broken.lean
# 非零退出 = 通过本负例检查
```

## 一键脚本

日常（sync `--check` + 本清单）：`.\scripts\ops_daily.ps1` / `bash ./scripts/ops_daily.sh`

- Windows：`.\scripts\smoke_verify.ps1`（自动前置 `d:\Lean\elan\bin`）
- Unix/WSL：`bash ./scripts/smoke_verify.sh`

改 Skill 后必须 `.\scripts\sync_opencode_agent.ps1`（或 `.sh`）；CI 跑 `--check`。协议见 [`OPS.md`](OPS.md)。

## 与 Agent 评测的关系

真 API 六任务见 `eval/tasks.yaml`；本清单只保证语料可编译、broken 仍坏。  
Success Bank / routing：[`SUCCESS_BANK.md`](SUCCESS_BANK.md)、[`MODEL_ROUTING.md`](MODEL_ROUTING.md)；代码在 `~/numina-lean-agent`。  
离线评测：`python -m scripts.run_eval --offline`（见 tasks.yaml harness）。
