# SUCCESS BANK — 架构与用法（Phase 2）

Success Bank 与 Error Bank **架构独立**：索引、审核流、检索 API 分开；物理上可复用同一份 `fixed_code` / Fixture，但逻辑库与默认策略不同。

## 定位

| 库 | 路径 | 存什么 | 何时写入 |
|----|------|--------|----------|
| **Error Bank** | `<lean_root>/.lean-error-bank/` | 失败轨迹、错误类、修复策略 | 验证失败 / 自动修复尝试 |
| **Success Bank** | `<lean_root>/.lean-success-bank/` | 成功证明路径、`minimal_diff` / `fixed_code` | **verify pass** 后 |

二者均 gitignore；默认入库 status = **`pending_review`**。

## Schema（实现字段）

```yaml
id: string
theorem_path: string
theorem_name: string
minimal_diff: string          # unified diff；Few-Shot 优先
fixed_code: string | null     # 非空才允许入库 / 进检索
source_error_id: string | null
resolved_tier: int | null
status: pending_review | active | invalid
goal_hash: string
created_at: iso8601
reviewed_at: iso8601 | null
```

## 门控（锁定）

1. 入库默认 `pending_review`；**retriever 只取 `active`**。
2. `fixed_code=null` / 空串 **禁止**写入 Success，也 **禁止**进 Few-Shot。
3. Few-Shot：**优先 Success 最小 diff**；Error Bank 只注入短「勿再犯」策略，不 dump 整文件。
4. Success 命中 **不**自动跳过 Verify。

## CLI（`~/numina-lean-agent`）

```bash
cd ~/numina-lean-agent && source .venv/bin/activate && export PYTHONPATH=$PWD

# Success（注意：success 子命令用 --bank_dir 指向 success 库）
python -m scripts.error_bank success --bank_dir <lean_root>/.lean-success-bank list
python -m scripts.error_bank success --bank_dir <lean_root>/.lean-success-bank show <id_prefix>
python -m scripts.error_bank success --bank_dir <lean_root>/.lean-success-bank review <id_prefix> --approve
python -m scripts.error_bank success --bank_dir <lean_root>/.lean-success-bank review <id_prefix> --reject
python -m scripts.error_bank success --bank_dir <lean_root>/.lean-success-bank stats

# Error（pending_review → approve 后才进检索）
python -m scripts.error_bank --bank_dir <lean_root>/.lean-error-bank list
python -m scripts.error_bank --bank_dir <lean_root>/.lean-error-bank review <id_prefix> --approve
python -m scripts.error_bank --bank_dir <lean_root>/.lean-error-bank review <id_prefix> --reject
```

## 与 runner 的钩子

`run_claude` 默认启用 Error Bank + Success Bank：

```bash
python -m scripts.run_claude run <file> \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 5 \
  --cwd <lean_project_root> \
  --max-model-tier 3 \
  --success-bank true
# 关闭：--success-bank false  /  --no-error-bank
```

verify pass → 投影 `fixed_code` + `minimal_diff` → Success（默认 `pending_review`）。对应 Error 条目亦保持 `pending_review` 直至人工 `review --approve`。

评测短跑可自动 `active`（日常仍要审核）：

```bash
export NUMINA_SUCCESS_AUTO_ACTIVE=1
# 或 run_claude --success-auto-active
```

`infra_error` / `fixed_code=null` **永不**进检索。Verify 必须是 Windows/elan `lake.exe`；Linux lake 对 `/mnt/d` mathlib 不作成功判据。

端到端剧本（ErrorBankDemo + 离线 unittest）：[`MEMORY_LOOP.md`](MEMORY_LOOP.md)。进度与缺口：[`PROGRESS.md`](PROGRESS.md)。

## 本仓语料

- `StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.fixed.lean`
- `StatInferenceLean/Exercises/InteractiveDemo.lean`
- `StatInferenceLean/Exercises/Bernoulli.lean`（单独验证，不进根 import）

实现代码：`~/numina-lean-agent/scripts/error_bank/`；Windows 镜像：`d:\Lean\temp\error_bank_implementation\`（`deploy.py` 同步）。
