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

## D. Phase 5 对比协议（准确度飞轮）

| 对照 | 方法 | 结果 | 笔记 |
|------|------|------|------|
| 离线冷 prompt | `augment_prompt` 无 Success 命中 | 不含 `Minimal diff:` / 不含修复 hunk | unittest |
| 离线热 prompt | pending→approve→retrieve 后 `augment_prompt` | **含该条 `minimal_diff`**（`+…sampleMean` hunk） | `test_retrieve_after_approve_prompt_contains_minimal_diff` |
| 真 API 冷 vs 热 | `--max-rounds 1` × ErrorBankDemo.broken | **未跑** | 需用户批准；abort 见 [`OPS.md`](OPS.md) |

复跑离线对比（WSL）：

```bash
cd ~/numina-lean-agent && source .venv/bin/activate && export PYTHONPATH=$PWD
python -m unittest scripts.error_bank.tests.test_memory_loop -v
```

可选真短跑（**默认不要**；禁止 `run_eval --real-api` 全套）：

```bash
python -m scripts.run_claude run \
  /mnt/d/Lean/projects/stat-inference-lean/StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.broken.lean \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 1 --cwd /mnt/d/Lean/projects/stat-inference-lean \
  --max-model-tier 1 --auth-mode C
```

## E. InfinitelyManyPrimes 短跑（2026-08-16，用户批准）

| 字段 | 值 |
|------|-----|
| 文件 | `StatInferenceLean/Exercises/Fixtures/InfinitelyManyPrimes.lean`（**未**进根 import） |
| 设计 | statement 对齐 `Nat.infinite_setOf_prime`；证明先 `sorry`，agent 补全 |
| Mode / 模型 | C / `deepseek-v4-flash`；`--max-rounds 3`；`--max-model-tier 2` |
| Agent 证明 | **是**：`exact Nat.infinite_setOf_prime`（接上 mathlib，未重写 Euclid） |
| 验证 | Windows `lake env lean` **通过**（exit 0，无 sorry） |
| Runner 轮次 | **1**（round 1 内已改对；WSL `lake env lean` 卡在 mathlib `.git` `git diff` / `index.lock`，约 5–6 min 后人工中止以保环境） |
| 成本 | API `result` 行未写出。会话 token 快照：18535 in / 297 out / 19968 cache_read。按当时 Flash 标价估算 **≈ $0.003–0.02**（远低于 $5） |
| Bank | Success/Error **未**写入 `pending_review`（中止在 Verify，Memory 未跑）。**未** auto-approve |
| 误伤 | 无。`ErrorBankDemo.broken` / 根模块 / lakefile / toolchain / mathlib lakefile 哈希未变；仅改目标 Fixture |
| 护栏 | `probe_auth` pass；settings 为 DeepSeek 非智谱；`Bash(rm *)` / `git clone` 仍在 |

注意：WSL 里 Linux `lake` 对 `/mnt/d` 上的 mathlib 会跑依赖仓 `git diff`，可能持有 `.lake/packages/mathlib/.git/index.lock`。验证优先用 Windows `d:\Lean\elan\bin\lake`。

## 变更相对上次

- 上次：真 API 阻塞（无 key）
- Phase 3：Mode C 连通；单任务 T3 **SUCCESS**；全量自动评测因 agent 误伤 mathlib 中止并已恢复环境
- Phase 4：护栏 + pending_review→active 离线闭环
- Phase 5：日常冒烟/同步纪律；离线热 prompt 含 `minimal_diff` 已锁门；真 API 冷/热对比保留为经批准可选项（因 22 分钟 / rm mathlib 风险，本轮不烧额度）
- 2026-08-16：用户批准 InfinitelyManyPrimes 短跑 — agent 用 `exact Nat.infinite_setOf_prime` 补全；Windows `lake env lean` 通过；WSL lake 卡 mathlib git 后中止；Bank 未入库；冷/热对比仍未跑
- 2026-08-16：四题评测短跑（StrictMonoComp / DvdTrans / EvenSquare / OddSquareMod8）— 详见 [`EVAL_FOUR.md`](EVAL_FOUR.md)
- 2026-08-17：修好 Verify（`lake.exe`）/ infra 不入库 / Success 真写入 + 评测 auto-active；相对裸 LLM 口径见 [`ADVANTAGE.md`](ADVANTAGE.md)。未重跑四题真 API，未跑全量 `--real-api`。


## F. 四题评测短跑（2026-08-16）

未跑全量 `run_eval --real-api`。Mode C / `deepseek-v4-flash` / `--max-rounds 3` / `--max-model-tier 2`。完整过程与「agent vs 裸 LLM」见 [`EVAL_FOUR.md`](EVAL_FOUR.md)。

| 题 | 文件 | 结果 | 轮次 | Windows 验证 | Bank | 备注 |
|----|------|------|------|--------------|------|------|
| 1 | `StrictMonoComp.lean` | **pass**（`exact hg.comp hf`） | 1 内改对后因 `lake exe cache get` 中止 | 通过 | Success 无 | mathlib `StrictMono.comp` |
| 2 | `DvdTrans.lean` | **pass**（`exact dvd_trans`） | 1 COMPLETE（$0.597）；r2 WSL lake 杀掉 | 通过 | Error pending 是「找不到 lake」假阳性；Success 无 | 多了一个非必要 import |
| 3 | `EvenSquare.lean` | **未闭环**（仍 `sorry`） | 第一轮写错 `Even.pow_of_ne_zero`；第二轮 MCP 断 + cache 循环 | sorry 警告 | 无 Success | 唯一「错 lemma 被 lake 拦住」实证；没修到通过 |
| 4 | `OddSquareMod8.lean` | **pass**（`exact Int.eight_dvd_sq_sub_one_of_odd`） | runner 3 轮 COMPLETE，**$0.798** | 通过 | 同上假阳性 Error；Success 仍空 | r1 已证完；r2–3 是 runner 误判 |

四题均未 import 进根模块。`ErrorBankDemo.broken` / InfinitelyManyPrimes / mathlib lakefile / toolchain 未误伤。
