# ADVANTAGE — 相对裸 LLM 的闭环优势（实现口径）

> 主 KPI：**端到端成功率**。优势不靠「证明得更巧」，而靠闭环让 **flash 级廉价模型**（Mode C 默认 `deepseek-v4-flash`）也能写出可 `lake env lean` 通过的证明，并把错稿拦住。  
> 成本是次要 KPI：主要通过 **少假失败轮次** 下降，而不是换更弱的证明策略。

## 本轮修了什么（根因 → 行为）

| 根因 | 旧行为 | 现行为 |
|------|--------|--------|
| WSL PATH / 并行 worker 找不到 `lake` | 把 `no such file or directory` 当 Lean 错题写入 Error Bank（`fixed_code=null`） | **infra_error**：不入库、不检索、不升 tier、不加 LLM 轮次 |
| Linux `~/.elan/bin/lake` 对 `/mnt/d` mathlib 卡 git | 证明已对仍判失败 → Success 不写 | Verify 优先 **Windows/elan `lake.exe`**；拒绝 Linux lake 作为成功判据 |
| Success Bank 从未写入 | Few-Shot 检索从未发生 | **真 pass**（`lake.exe env lean` exit 0 且无 error）后写入 Success |
| MCP `lean_diagnostic_messages` Connection closed | agent 空转 / `lake exe cache get` | 诊断主路径 = runner 的 `lake env lean`；MCP 失败则 **跳过、不重试**；禁 `lake exe cache` |

## 飞轮怎么用

日常（入库 `pending_review`，人工审核后才进检索）：

```bash
cd ~/numina-lean-agent && source .venv/bin/activate && export PYTHONPATH=$PWD
set -a && source .env && set +a
LEAN=/mnt/d/Lean/projects/stat-inference-lean

python -m scripts.run_claude run <file.lean> \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 3 --cwd $LEAN --max-model-tier 1 --auth-mode C

python -m scripts.error_bank success --bank_dir $LEAN/.lean-success-bank list
python -m scripts.error_bank success --bank_dir $LEAN/.lean-success-bank review <id> --approve
```

评测短跑（**仅用于证明检索**；日常仍要审核）：

```bash
export NUMINA_SUCCESS_AUTO_ACTIVE=1
# 或：--success-auto-active
python -m scripts.run_claude run <file.lean> \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 3 --cwd $LEAN --max-model-tier 1 --auth-mode C \
  --success-auto-active
```

可选显式 lake：

```bash
export LAKE_PATH=/mnt/d/Lean/elan/bin/lake.exe
# 或 NUMINA_LAKE
```

不要用会卡 mathlib `.git` 的 Linux lake。不要全量 `run_eval --real-api`。

## vs 裸 LLM（同等命题，flash）

| 能力 | 裸 LLM（无检查） | 本闭环（flash + Verify + Bank） |
|------|------------------|--------------------------------|
| 写出可编译证明 | 碰运气 | **Windows `lake env lean` 门**：过了才算成功 |
| 错稿（EvenSquare 类） | 模型不知道编不过 | Verify **拦住**；不把环境故障当成错题 |
| 下一同类题少轮次 | 无记忆 | Success **minimal_diff** 注入热 prompt（retriever 只取 `active`） |
| 假失败烧钱 | — | infra 不再触发 DvdTrans/OddSquare 那种「已经对了还再问 2–3 轮」 |

对比口径：**同等命题，flash + Verify vs 裸 LLM 无检查**。不比较「谁的证明更巧」。

## 实证边界（诚实）

本轮用 **unittest + 离线写入→auto-active→retrieve** 锁门：

- lake 绝对路径优先 `lake.exe`
- infra **不**进 Error Bank / 检索
- 真 pass 后 Success 写入；auto-active 后下一题 prompt **含 `minimal_diff`**
- DvdTrans 语料：`sorry` → `exact dvd_trans` 的 diff 出现在热 prompt

**尚未**用真 API 证明「下一题更省轮次/更省钱」。四题评测当时 Success 为空、Error 是假阳性；修好 Verify 之后需要一次经批准的 `--max-rounds 1` 短跑才能填这个数。

EvenSquare 仍 `sorry`：本轮 **不**为它长烧 API。
