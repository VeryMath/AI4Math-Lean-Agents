# OPS — Phase 5 稳态运维（准确度飞轮）

> 本文件把 Phase 5 锁成 **运维清单 + 对比协议**。  
> 不教 Lean。主 KPI 仍是端到端成功率。  
> **默认不烧真 API。**

## 日常清单（习惯化）

Windows（PATH 会自动前置 `d:\Lean\elan\bin`）：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\ops_daily.ps1
```

等价拆开：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\sync_opencode_agent.ps1 -CheckOnly
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_verify.ps1
```

Unix / WSL：

```bash
bash ./scripts/ops_daily.sh
# 或：bash ./scripts/sync_opencode_agent.sh --check && bash ./scripts/smoke_verify.sh
```

Bank 代码改过之后（WSL，`~/numina-lean-agent`）：

```bash
cd ~/numina-lean-agent && source .venv/bin/activate && export PYTHONPATH=$PWD
python -m unittest scripts.error_bank.tests.test_memory_loop \
  scripts.error_bank.tests.test_error_bank \
  scripts.error_bank.tests.test_guardrails \
  scripts.error_bank.tests.test_lean_checker -v
```

## Skill ↔ OpenCode 同步纪律

- **主源**：`.cursor/skills/lean-agent-numina/SKILL.md`
- **派生**：`.opencode/agents/numina-lean-agent.md`（文件头 DO NOT EDIT）
- 改 Skill **必须**立刻：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\sync_opencode_agent.ps1
```

CI（`lean_action_ci.yml`）会跑 `sync_opencode_agent.sh --check`：忘了 sync 则红。

## 短跑基线对比（准确度飞轮的最小证明）

### A. 默认：离线（每次改 Bank 后必跑）

`test_memory_loop.test_retrieve_after_approve_prompt_contains_minimal_diff`：

1. `add_from_fix(broken, fixed)` → `pending_review`（检索为空）
2. `review --approve` → `active`
3. 同类 query 命中后，`augment_prompt` **必须含该条 `minimal_diff`**（冷 prompt 不含）

这就是「命中后下一轮 prompt 更具体」的门控，不碰 `.lake`、不花额度。

### B. 可选：真 API 短跑（需用户书面批准）

目标：`--max-rounds 1` 修 `ErrorBankDemo.broken`，对比 **无 Bank（冷）** vs **approve 后有 Bank（热）**。  
**禁止**全量 6 任务 `--real-api`。**禁止**让 agent 碰 `.lake` / mathlib。

上次教训：真任务曾跑约 22 分钟，并 `rm` mathlib。因此 **本 Phase 默认不做 B**。

#### Abort（任一成立则停，只做 A）

| 条件 | 为何 abort |
|------|------------|
| `~/.claude/settings.json` 的 `ANTHROPIC_BASE_URL` 指向智谱 / GLM / `bigmodel.cn` | 1211 / 错后端 |
| `probe_auth` 失败（Mode A/C 混用、脏模型名） | runner 会硬停 |
| 护栏缺失（prompt 未禁 `.lake`/mathlib，或无 `Bash(rm *)` / `Bash(git clone *)`） | 会再毁环境 |
| 用户未明确批准本次短跑 | 额度与 mathlib 风险 |
| 打算跑 `run_eval --real-api` 全套 6 任务 | Phase 5 明确禁止 |

#### 若批准，仅此命令（Mode C，1 round）

```bash
cd ~/numina-lean-agent && source .venv/bin/activate && export PYTHONPATH=$PWD
set -a && source .env && set +a
LEAN=/mnt/d/Lean/projects/stat-inference-lean

python -m scripts.run_claude run \
  $LEAN/StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.broken.lean \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 1 --cwd $LEAN --max-model-tier 1 --auth-mode C
```

成功后走 [`MEMORY_LOOP.md`](MEMORY_LOOP.md) 的 `list` → `review --approve`。  
把结果填回 [`BASELINE.md`](BASELINE.md) 的「Phase 5 可选短跑」表；冷/热对比未跑则保持「未批准」。

## 成功标准（本 Phase）

- [x] `smoke_verify.ps1` 一键可跑，并写入日常清单
- [x] 改 Skill 必须 sync；`--check` + CI 卡住漂移
- [x] 离线：approve 后命中 prompt 含 `minimal_diff`
- [ ] 真 API 冷/热短跑 — **可选，需用户批准**；未批准不算缺口阻塞
