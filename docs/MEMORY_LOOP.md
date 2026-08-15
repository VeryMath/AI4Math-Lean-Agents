# MEMORY LOOP — 最短端到端剧本（准确度飞轮）

> 目标：证明 **pending_review → 人工审核 → active 检索命中**。  
> 用 **离线 unittest**，不要烧一轮可能毁 mathlib 的长 API。

## 门控（锁定）

| 状态 | 检索 / Few-Shot |
|------|-----------------|
| `pending_review` | **不进入** |
| `fixed_code=null` / 空 | **不进入**（Success 禁止写入） |
| `active` 且有可复用 fix | **进入**（Success 优先最小 diff；Error 只给短策略） |
| `invalid` | **不进入** |

verify pass → 写入 Success（及对应 Error 的 `fixed_code`）仍为 `pending_review`，直到人工 `review --approve`。

## 离线证明（推荐，每次改 Bank 后跑）

WSL：

```bash
cd ~/numina-lean-agent && source .venv/bin/activate && export PYTHONPATH=$PWD
python -m unittest scripts.error_bank.tests.test_memory_loop -v
python -m unittest scripts.error_bank.tests.test_error_bank -v
python -m unittest scripts.error_bank.tests.test_guardrails -v
```

`test_memory_loop` 用 ErrorBankDemo 的 broken→fixed 语料：

1. `add_from_fix(broken, fixed)` → `pending_review`；检索为空；Few-Shot 为空
2. `review --approve` → `active`
3. 同类 query（`unknown identifier sampleMean`）检索命中；prompt 含 `Probability.sampleMean` 最小 diff
4. `pending_review` / `fixed_code=null` 永不进 Few-Shot
5. Phase 5：命中后 `augment_prompt` **必须含该条 `minimal_diff` 全文**（冷 prompt 不含）；见 `test_retrieve_after_approve_prompt_contains_minimal_diff`

## 人工 CLI（真实 bank 目录，可选）

语料：`StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.broken.lean` + `.fixed.lean`。  
Bank 在 Lean 根（gitignore）：`.lean-success-bank/`、`.lean-error-bank/`。

```bash
cd ~/numina-lean-agent && source .venv/bin/activate && export PYTHONPATH=$PWD
LEAN=/mnt/d/Lean/projects/stat-inference-lean

# 1) 列出待审（verify pass 后应出现 pending_review）
python -m scripts.error_bank success --bank_dir $LEAN/.lean-success-bank list
python -m scripts.error_bank --bank_dir $LEAN/.lean-error-bank list

# 2) 人工看一眼再入库
python -m scripts.error_bank success --bank_dir $LEAN/.lean-success-bank show <id_prefix>
python -m scripts.error_bank success --bank_dir $LEAN/.lean-success-bank review <id_prefix> --approve

# 3) 下一任务检索只应注入 active（由 runner / SuccessRetriever 保证）
```

## 若做真 API（默认不要）

护栏已上之后，且 **不要让 agent 碰 `.lake`**：

```bash
python -m scripts.run_claude run \
  $LEAN/StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.broken.lean \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 1 \
  --cwd $LEAN --max-model-tier 1 --auth-mode C
```

成功后走上面的 `list` → `review --approve`。全量 `run_eval --real-api` **不要跑**。  
Phase 5 把真短跑标为**可选、需用户批准**；abort 门与日常清单见 [`OPS.md`](OPS.md)。

## 成功标准

- [x] pending 不进检索（unittest）
- [x] approve 后同类任务能检索到 ErrorBankDemo 修复 diff（unittest）
- [x] 命中后 prompt 含该条 `minimal_diff`（Phase 5 离线）
- [ ] 真任务上「命中后下一轮更准」—— 可选短跑，需用户批准；未批准不阻塞运维
