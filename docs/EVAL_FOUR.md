# EVAL_FOUR — 四题真 API 短跑（2026-08-16）

> Mode C / `deepseek-v4-flash`；`--max-rounds 3 --max-model-tier 2 --auth-mode C`。  
> **未**跑全量 6 任务 `run_eval --real-api`。未 push。未打印 API key。  
> 对照：Inspect → Workspace → Formalize（人手写 statement）→ Prove/Fix（`run_claude`）→ Verify（Windows `lake env lean`）→ Memory（仅 runner 真写入 Bank 才算入库）。

## 跑前检查

| 项 | 结果 |
|----|------|
| `~/.claude/settings.json` BASE_URL | `https://api.deepseek.com/anthropic`（非智谱） |
| MODEL | `deepseek-v4-flash` |
| `probe_auth` | errors `[]` |
| `ErrorBankDemo.broken.lean` | 仍为未限定 `sampleMean` |
| mathlib `lakefile.lean` | 在 |
| InfinitelyManyPrimes | 未改坏（仍 `exact Nat.infinite_setOf_prime`） |
| 根 `StatInferenceLean.lean` | **未** import 本四文件（仅注释） |

## 工作流：本轮实际跑到的模块

| 阶段 | 本轮是否发生 | 说明 |
|------|----------------|------|
| Inspect | 是 | 目标文件、项目根、mathlib 4.28 lemma 名 |
| Workspace | 是 | Mode C、venv、`probe_auth` pass；Windows lake 验证优先 |
| Formalize | 是（人手） | 四 Fixture 先 `sorry`；EvenSquare 中途因 `Even.pow_of_ne_zero` 在 `ℤ` 上实例不贴而改指向 `even_pow'` |
| Prove/Fix | 是 | 每题单独 `python -m scripts.run_claude run` |
| Skill 阶段机 / 护栏 | 部分 | runner 带 `Bash(rm *)` / `git clone` disallowed、append-system-prompt 禁碰 `.lake`；**agent 仍反复跑 `lake exe cache get`**（擦边碰 `.lake` 缓存，已多次人工杀掉） |
| Verify（runner `lean_checker`） | 名义上有，实际上常废 | `check_lean_files_parallel` 调 `lake`；多进程 PATH 经常找不到包装的 Windows `lake`，报 `no such file or directory`；60s timeout |
| Verify（Windows `lake env lean`） | **是，作为本评测门** | `d:\Lean\elan\bin\lake.exe`；WSL 原生 `~/.elan/bin/lake env lean` 对 `/mnt/d` 易卡，按护栏 >2–3 min 停掉 |
| Memory Success Bank | **未写入** | `.lean-success-bank` 仍 `total: 0` |
| Memory Error Bank | **有 pending_review，但是假阳性** | 条目 raw_message 为 `no such file or directory`（找不到 `lake`），`fixed_code=null`，**不是**证明错误 |
| Few-Shot / active 检索 | **未用到** | retriever 只取 `active`；本轮无 active Success |
| 升 tier | 未观察到有效升档 | `--max-model-tier 2`；题目在 Flash 上就 `exact` 或卡住环境 |
| MCP `lean_diagnostic_messages` | 不稳定 | OddSquareMod8 round 1 声称用了且空诊断；EvenSquare 重跑出现 `MCP error -32000: Connection closed` |

## 四题明细

### 1. StrictMonoComp

- 路径：`StatInferenceLean/Exercises/Fixtures/StrictMonoComp.lean`
- mathlib：`StrictMono.comp`（`Mathlib.Order.Monotone.Defs`）
- Agent 证明：`exact hg.comp hf`（对齐库定理，未手写单调性）
- 轮次：round 1 内已改对；随后循环 `lake exe cache get`，**人工中止**以免继续烧额度
- 成本：runner 未写出 `result` 行 → **未知**（低于 OddSquareMod8 的 $0.80 量级，未跑满 3 轮）
- Windows `lake env lean`：**通过**（exit 0，无 sorry 声明）
- Bank：Success 无；Error 无对应成功修复
- 1211：无

### 2. DvdTrans

- 路径：`StatInferenceLean/Exercises/Fixtures/DvdTrans.lean`
- mathlib：`dvd_trans`
- Agent 证明：`exact dvd_trans hab hbc`；并多加了 `import Mathlib.Algebra.Ring.Int.Defs`（非必要，仍能编过）
- 轮次：round 1 `COMPLETE`，cost **$0.597**（141 in / 149 out / 22400 cache_read；modelUsage 显示更大 token 累计）。round 2 卡在 WSL `~/.elan/bin/lake env lean`，人工杀掉
- Windows `lake env lean`：**通过**
- Bank：Error `802f629b` **pending_review**，类别 `proof/goal_unsolved`，正文是 **lake 找不到**，`fixed_code=null`。Success **未**入库

### 3. EvenSquare

- 路径：`StatInferenceLean/Exercises/Fixtures/EvenSquare.lean`
- 第一版 Formalize 指向 `Even.pow_of_ne_zero`（`Mathlib.Algebra.Ring.Parity`）。该 lemma 要 Semiring 的 `Add`，与 `ℤ` 的 `Int.instAdd` **对不上**
- **第一轮 agent 行为（准确度相关实证）**：
  1. `exact Even.pow_of_ne_zero hn (by norm_num : (2 : ℤ) ≠ 0)` → Windows 验证失败（unknown tactic / 指数类型错）
  2. 改为 `(by decide : (2 : ℤ) ≠ 0)` 仍错
  3. 改为 `(2 : ℕ)` 仍 instance 错
  4. 改为 `(n := 2) (by decide)` 仍错
  5. 退回 `sorry` 并插入 `#check` → **脱轨**，杀掉
- 随后 Formalize 改为 `even_pow'`（`Mathlib.Algebra.Group.Int.Even`，对 `ℤ` 成立），文件恢复 `sorry` 后重跑
- **第二轮**：MCP lean-lsp `Connection closed`；agent 循环 `lake exe cache get`，**从未改掉 sorry**，杀掉保额度
- 最终文件：**仍 `sorry`**（本评测 **未闭环证明**）
- 成本：第一轮 jsonl 曾在 WSL `/tmp` 后丢失；第二轮无 `result` 行 → **未知**（第一轮会话很长，量级可能与 DvdTrans 的 ~$0.6 相近，但不要当精确值）
- Windows：当前 `sorry` 版本 `lake env lean` exit 0 **带 sorry 警告**；不算证明通过
- Bank：无 Success

### 4. OddSquareMod8

- 路径：`StatInferenceLean/Exercises/Fixtures/OddSquareMod8.lean`
- mathlib：`Int.eight_dvd_sq_sub_one_of_odd`
- Agent 证明：`exact Int.eight_dvd_sq_sub_one_of_odd hk`（round 1 已写入）
- Runner：`success=true`，`COMPLETE`，**3 轮**（round 1 已证完；2–3 轮因 runner 找不到 `lake` 误判失败而重问；模型重复声称 COMPLETE）
- 成本：**$0.798**（34862+33799+34131 in / 1524+293+523 out / cache_read 410240）
- Windows `lake env lean`：**通过**
- Bank：Error `a5d6d192` **pending_review**，同样是 `no such file or directory`（假阳性）；Success **仍空**。尽管 runner 报 success，`handle_verification_success` **没有**写入 Success Bank（verify 回调未真正 lake-pass）

## Agent vs 直接 LLM（按这四题，不空吹）

「直接 LLM」= 同一类模型（DeepSeek Flash）看自然语言/文件里的命题，**不跑 lake、不闭环、不 Bank**。对照物：agent **第一稿** vs **经 Windows lake 验证的最终文件**。没有再烧 4 次无验证长会话。

| 维度 | 这四题实际观察到的 |
|------|-------------------|
| 正确性 | 3 题最终 Windows 通过，都是一行 `exact` 库定理。EvenSquare **第一稿是错的**（类型/实例），lake 拦住了；agent **没修到能编过**。裸 LLM 同样会写出那种 `Even.pow_of_ne_zero` 错应用，且**不会自己知道编不过** |
| 与 mathlib 对齐 | 对得上库名的三题，agent 就是 `exact`/`hg.comp`，没有更巧的证明。增量不在「证明能力」 |
| 失败恢复 | EvenSquare：有 compile fail 后改稿，但改稿仍错，后脱轨。OddSquareMod8 的「3 轮」是 **runner 假失败**，不是证明失败恢复 |
| 记忆飞轮 | **本轮没有**成功案例检索/入库。Error pending 是「找不到 lake」，注入 Few-Shot 也无益。不要写成飞轮已转起来 |
| 成本与时延 | 有数的：DvdTrans round1 $0.60；OddSquareMod8 三轮 $0.80 / ~15 min。大量时间耗在 `lake exe cache get`、WSL lake、MCP 断开，而不是思考证明 |
| 环境风险 | 护栏挡住了 `rm`/`git clone`。agent 仍打 `lake exe cache get`（碰 `.lake` 缓存）。WSL 对 `/mnt/d` mathlib 仍危险。验证必须 Windows lake |

**分题结论**

1. **StrictMonoComp / DvdTrans / OddSquareMod8**：标准、mathlib 已有。相对裸 LLM，优势几乎全在 **Verify 门 + 工程约束**（禁毁环境、单文件验证），**不在证明得更巧**。文件头已经写了 lemma 名，模型对齐 `exact` 并不需要闭环。
2. **EvenSquare**：这是本轮唯一「裸模型易写错」的实证。Agent 因（人工）Windows lake 发现错误；但 **闭环没能修好**。所以：Verify 有准确度价值；「自动修好」这轮 **没有做成**。
3. **不能说明的**：Success Bank 命中后下一题更准（没入库、没检索）；MCP 稳定时的完整 Memory；比 Flash 更强的模型是否还需要 `exact` 提示。

## 复跑

Windows 验证（PATH 前置 elan）：

```powershell
cd d:\Lean\projects\stat-inference-lean
$env:Path = 'd:\Lean\elan\bin;' + $env:Path
lake env lean StatInferenceLean/Exercises/Fixtures/StrictMonoComp.lean
lake env lean StatInferenceLean/Exercises/Fixtures/DvdTrans.lean
lake env lean StatInferenceLean/Exercises/Fixtures/OddSquareMod8.lean
# EvenSquare 当前仍 sorry，会警告 declaration uses sorry
lake env lean StatInferenceLean/Exercises/Fixtures/EvenSquare.lean
```

单题真 API（WSL；**不要** `run_eval --real-api` 全套）：

```bash
cd ~/numina-lean-agent && source .venv/bin/activate && export PYTHONPATH=$PWD
set -a && source .env && set +a
LEAN=/mnt/d/Lean/projects/stat-inference-lean

python -m scripts.run_claude run \
  $LEAN/StatInferenceLean/Exercises/Fixtures/DvdTrans.lean \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 3 --cwd $LEAN \
  --max-model-tier 2 --auth-mode C
```

验证请用 Windows `lake env lean`。若 WSL `lake` 停在 `.lake/packages/mathlib/.git` 超过 2–3 分钟：停掉，改 Windows。

## 2026-08-17 修复后（未重跑四题真 API）

工程根因已在 runner / `lean_checker` / Bank 落地，见 [`ADVANTAGE.md`](ADVANTAGE.md)。**本轮没有**再烧四题 `--real-api`，因此上表数字仍是 08-16 的历史记录。

预期行为（下一短跑应看到）：

- Verify 打印 `Verify lake=/mnt/d/Lean/elan/bin/lake.exe`
- 证明已对 → round 1 COMPLETE → Success 有条目（日常 `pending_review`；评测加 `--success-auto-active` 则 `active` 可检索）
- 找不到 lake / timeout → `INFRA_ERROR`，**不**写 Error pending，**不**再问模型
- Agent 不再被 prompt 推去 `lake exe cache get`

仍未证明：热检索让下一同类题少轮次（需一次 auto-active 后的 `--max-rounds 1` 对照）。EvenSquare 仍 sorry，不要长烧。
