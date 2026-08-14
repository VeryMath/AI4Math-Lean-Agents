# Reference — 认证、启动清单与排障

## 启动检查清单

1. 在可构建 Lean 项目根（有 `lean-toolchain` + `lakefile`）。
2. `lake env lean <目标文件>` 或先确认 Fixture 角色（broken 预期失败）。
3. WSL 中：`~/numina-lean-agent`、`.venv`、`python -m scripts.run_claude --help`。
4. 选模式：**国内个人优先 Mode C**；课题组 / 已有 Gemini 用 Mode A；A 失败再 C。
5. 确认模型名 **无** `[1m]` / 不可见字符：`echo "$ANTHROPIC_MODEL" | od -c | head`。
6. **禁止** `ANTHROPIC_BASE_URL` 为 localhost 且 `ANTHROPIC_MODEL` 为 `deepseek*`。
7. **禁止** `~/.claude/settings.json` 指向智谱 / GLM 却跑 DeepSeek（1211）。`run_claude` 会 abort。
8. Mode A：`curl` LiteLLM `/v1/messages` 正常；`NO_PROXY` 含 `localhost,127.0.0.1`。
9. MCP（若用）：在 **Lean 项目目录** `claude mcp add` + `claude mcp list`。
10. Phase 3：`python -m scripts.run_eval --dry-run` 必须绿；**不要**再跑会长 `clone mathlib` 的全量 `--real-api`，除非护栏已确认。
11. 禁止碰 `.lake/` / mathlib / toolchain / lakefile；round 内验证用 `lake env lean`，不用全仓 `lake build`。

## Mode C：DeepSeek 直连（国内实操推荐 / 回退）

**可跳过 LiteLLM。** 详见 [`docs/AUTH.md`](../../../docs/AUTH.md)。

```bash
export DEEPSEEK_API_KEY='...'
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_API_KEY="$DEEPSEEK_API_KEY"
export ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_API_KEY"
export ANTHROPIC_MODEL="deepseek-v4-flash"
```

## Mode A：LiteLLM（WSL-only）+ Gemini

配置示例 `~/litellm_config.yaml`：

```yaml
model_list:
  - model_name: anthropic-claude
    litellm_params:
      model: gemini/gemini-2.5-pro
      api_key: os.environ/GEMINI_API_KEY
```

```bash
# 仅在 WSL 内
export GEMINI_API_KEY='...'
litellm --config ~/litellm_config.yaml --port 4000
```

Numina 侧：

```bash
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="sk-anything"
export ANTHROPIC_MODEL="anthropic-claude"
export NO_PROXY=localhost,127.0.0.1
```

探测：

```bash
curl -s http://localhost:4000/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: sk-anything" \
  -d '{
    "model": "anthropic-claude",
    "max_tokens": 64,
    "messages": [{"role":"user","content":"reply ok"}]
  }'
```

## 1211 排障树（模型不存在）

现象：`模型不存在` / `code 1211` / 类似 model not found。

```text
1211 / 模型不存在
├─ 1. 模型名是否脏？
│     含 [1m]、颜色码、首尾空格 → 清掉，重设纯文本 id
├─ 2. 当前是 Mode A 还是 C？
│     BASE_URL 含 localhost:4000 → 必须是 Mode A
│     BASE_URL 含 api.deepseek.com → 必须是 Mode C
├─ 3. Mode A
│     MODEL 是否为 anthropic-claude（LiteLLM 别名）？
│       否 → 改为 anthropic-claude（不要直接写 gemini/... 给 Numina，除非你改了 litellm 配置）
│     LiteLLM 是否映射 gemini/gemini-2.5-pro？GEMINI_API_KEY 是否在 litellm 进程？
│     /v1/messages 探测是否成功？
├─ 4. Mode C
│     MODEL 是否 deepseek-v4-flash 或 deepseek-v4-pro？
│     账号是否开通该模型？
├─ 5. 混用？
│     localhost + deepseek* → 禁止；改成纯 A 或纯 C
├─ 6. ~/.claude/settings.json 是否仍指向智谱 / GLM / bigmodel.cn？
│     是且本 run 要 DeepSeek → 改 settings 或移走 env 块（runner 会 abort）
└─ 7. 仍失败 → 换 Mode C 最小命令重试；记录 [check] 与提供商原始报错
```

## Lean 项目判定

祖先目录需有：

- `lean-toolchain`
- `lakefile.toml` 或 `lakefile.lean`

```bash
pwd
ls
lake build   # 全仓；或优先 lake env lean <file>
```

## WSL 代理最小排障

```bash
GW=$(ip route | awk '/^default/ {print $3; exit}')
curl -I https://github.com --proxy http://$GW:7890 -m 8
export http_proxy="http://$GW:7890"
export https_proxy="http://$GW:7890"
export NO_PROXY=localhost,127.0.0.1
```

## MCP 目录作用域

```bash
cd <lean_project_root>
claude mcp add lean-lsp -- ~/lean-lsp-mcp/numina-lean-mcp.sh
claude mcp list
```

## 其它常见失败

| 现象 | 动作 |
|------|------|
| 401 AuthenticationError | 检查上游 key、当前 shell 是否 export、Mode 与 BASE_URL 是否匹配 |
| MCP not connected | 在目标 Lean 项目目录重加 MCP |
| lake=fail | 目标不在 Lake 项目内；先 `lake env lean` |
| proxy refused | 查网关端口与 LAN；Mode A 确保 NO_PROXY 含 localhost |
| Command 'wsl' not found | 已在 WSL 内则不要再套 `wsl` |

## 验证前移与 Fixture

- 优先：`lake env lean StatInferenceLean/Exercises/InteractiveDemo.lean`
- Error Bank：`Fixtures/ErrorBankDemo.broken.lean`（预期失败）/ `.fixed.lean`（预期通过）
- Bernoulli：**不要**靠根模块默认 import；单独 `lake env lean …/Bernoulli.lean`

## Phase 2 flags 与记忆飞轮

代码在 `~/numina-lean-agent`；本仓维护语料与文档（`docs/MODEL_ROUTING.md`、`docs/SUCCESS_BANK.md`）。

| Flag | 默认 | 含义 |
|------|------|------|
| `--max-model-tier` | 3 | 全局上限；仍受类别门控 |
| `--initial-model-tier` | 1 | 首轮 LLM tier |
| `--error-bank` / `--no-error-bank` | 开 | Error Bank |
| `--success-bank` / `--success-bank false` | 开 | Success Bank |
| `--enable-auto-fix` | 开 | Tier-0 规则修复 |
| `--auth-mode` | 自动 | `A` / `C` / `B` |

```bash
# 离线评测入口（无 key 则只跑 verify；尊重 max_usd_per_run: 5）
cd ~/numina-lean-agent && PYTHONPATH=$PWD \
  python -m scripts.run_eval --offline \
    --config /mnt/d/Lean/projects/stat-inference-lean/eval/tasks.yaml \
    --project-root /mnt/d/Lean/projects/stat-inference-lean
```

审核：

```bash
python -m scripts.error_bank success review <id> --approve --bank_dir <lean>/.lean-success-bank
python -m scripts.error_bank review <id> --approve --bank_dir <lean>/.lean-error-bank
```

记忆闭环离线证明：`python -m unittest scripts.error_bank.tests.test_memory_loop -v`（见 [`docs/MEMORY_LOOP.md`](../../../docs/MEMORY_LOOP.md)）。

## 禁止操作（工具护栏）

Prove/Fix / Verify 阶段 **不得**：

- `rm -rf .lake` / `.lake/packages/mathlib`；`git clone` mathlib4 当修复
- 改 `lean-toolchain`、`lakefile.toml` / `lakefile.lean`
- 用全仓 `lake build` 作为 round 内验证（用 `lake env lean <file>` / `lean_diagnostic_messages`）
- 把 deepseek 打到 localhost LiteLLM；把智谱 BASE_URL 与 deepseek 模型混用

Runner 侧：`--disallowed-tools Bash(rm *)` 等 + system prompt 硬约束 + mathlib 完整性检查。
