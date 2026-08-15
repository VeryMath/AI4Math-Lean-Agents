# AUTH — 认证速查

详细排障与启动清单以 Skill 为单源，避免双处漂移：

- 主流程与 Mode 选择：[`../.cursor/skills/lean-agent-numina/SKILL.md`](../.cursor/skills/lean-agent-numina/SKILL.md)
- 1211 树 / LiteLLM / DeepSeek：[`../.cursor/skills/lean-agent-numina/reference.md`](../.cursor/skills/lean-agent-numina/reference.md)
- 可复制命令：[`../.cursor/skills/lean-agent-numina/examples.md`](../.cursor/skills/lean-agent-numina/examples.md)
- 环境变量模板：[`.env.example`](../.env.example)

---

## 谁用哪条路径？（先看这里）

| 你是谁 | 推荐 | 说明 |
|--------|------|------|
| **国内个人开发者**（只能买国内 API） | **先走 Mode C（DeepSeek 直连）** | 无需 LiteLLM；一条 `export` + `run_claude` / `run_eval --real-api --auth-mode C` |
| **课题组默认叙事 / 已有 Gemini** | Mode A（Gemini + LiteLLM，WSL） | `anthropic-claude` → `gemini/gemini-2.5-pro` |
| Mode A 挂了 / 1211 | 回退 Mode C | 见下方与 Skill reference 1211 树 |

> VISION 锁定：仓库文档默认叙事仍是 **Mode A**；**国内实操默认先 C**。二者不矛盾。

---

## 锁定摘要

| 模式 | 何时用 | BASE_URL | MODEL |
|------|--------|----------|-------|
| **A（课题组默认）** | Gemini + LiteLLM（WSL） | `http://localhost:4000` | `anthropic-claude` → 映射 `gemini/gemini-2.5-pro` |
| **C（国内实操推荐 / 回退）** | 无 LiteLLM / 仅 DeepSeek | `https://api.deepseek.com/anthropic` | `deepseek-v4-flash`（或 `deepseek-v4-pro`） |
| B（可选） | Anthropic 直连 | `https://api.anthropic.com` | Claude 模型 id |

## 硬性禁止

1. 模型名含 ANSI / `[1m]` 等脏字符（复制终端高亮时易混入）  
2. `ANTHROPIC_BASE_URL` 指向 localhost（LiteLLM），同时 `ANTHROPIC_MODEL=deepseek*`  
3. `~/.claude/settings.json` 指向智谱 / GLM / `bigmodel.cn`，同时本 run 要用 DeepSeek（**1211 根因**）  
4. 把 deepseek 模型打到 localhost LiteLLM / 把智谱 BASE_URL 与 deepseek 模型混用  

`run_claude` 启动时会 `probe_auth`：Mode 混用或 settings 冲突则 **直接 abort**（`NUMINA_IGNORE_SETTINGS_CONFLICT=1` 可强制继续，不推荐）。

### 真 API 短跑 abort（Phase 5）

日常只跑 [`OPS.md`](OPS.md) 清单。再烧 `--max-rounds 1` 之前，下列任一成立则 **abort**（只做离线对比）：

- settings.json 的 BASE_URL 仍是智谱 / GLM / `bigmodel.cn`
- `probe_auth` 失败（localhost+deepseek、脏模型名）
- 护栏缺失（prompt 未禁 `.lake`/mathlib，或 CLI 无 `Bash(rm *)` / `Bash(git clone *)`）
- 用户未明确批准本次短跑
- 请求的是全量 6 任务 `--real-api`

### 1211：settings.json 曾指向智谱

Claude Code 会读 `~/.claude/settings.json`（user 级）。若其中 `env.ANTHROPIC_BASE_URL` 是智谱，即使 shell 已 `export` DeepSeek，仍可能 1211。

```bash
# 查看（不要把 key 贴到聊天/git）
python3 -c "import json,pathlib; p=pathlib.Path.home()/'.claude'/'settings.json'; print(p.exists()); d=json.loads(p.read_text()) if p.exists() else {}; e=d.get('env',{}); print('BASE_URL', e.get('ANTHROPIC_BASE_URL','<unset>')); print('MODEL', e.get('ANTHROPIC_MODEL','<unset>'))"
```

修复：把 settings 里的 BASE_URL/MODEL 改成与当前 Mode 一致（Mode C → `https://api.deepseek.com/anthropic` + `deepseek-v4-flash`），或暂时移走冲突的 `env` 块。  

## Mode C 最小步骤（国内）

1. 打开 [https://platform.deepseek.com](https://platform.deepseek.com) → 注册 / 充值 → 创建 API Key  
2. 在 WSL 写入 `~/numina-lean-agent/.env` 或 Lean 仓 `.env`（已 gitignore）：

```bash
DEEPSEEK_API_KEY=sk-你的key
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_API_KEY=${DEEPSEEK_API_KEY}
ANTHROPIC_AUTH_TOKEN=${DEEPSEEK_API_KEY}
ANTHROPIC_MODEL=deepseek-v4-flash
```

3. **可跳过 LiteLLM**（Mode C 直连，不需要 `:4000`）  
4. 最小命令：

```bash
cd ~/numina-lean-agent && source .venv/bin/activate && export PYTHONPATH=$PWD
set -a && source .env && set +a   # 或手动 export 上述变量
python -m scripts.run_claude run \
  /mnt/d/Lean/projects/stat-inference-lean/StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.broken.lean \
  --prompt-file prompts/prompt_complete_file.txt --max-rounds 3 \
  --cwd /mnt/d/Lean/projects/stat-inference-lean --max-model-tier 3 --auth-mode C

# 或整套评测（$5 硬顶）
python -m scripts.run_eval --real-api --auth-mode C \
  --config /mnt/d/Lean/projects/stat-inference-lean/eval/tasks.yaml \
  --project-root /mnt/d/Lean/projects/stat-inference-lean
```

## 启动检查清单（最短）

- [ ] 密钥只在环境变量 / 本地 `.env`（已 gitignore），未写入仓库  
- [ ] 国内用户：Mode C 变量已导出；**未**同时设 localhost + deepseek  
- [ ] Mode A：WSL 内 LiteLLM 在 `:4000`，且 `NO_PROXY` 含 `localhost,127.0.0.1`  
- [ ] Mode A：`ANTHROPIC_MODEL=anthropic-claude`（不是 gemini 原始名、不是 deepseek）  
- [ ] `~/.claude/settings.json` 的 BASE_URL **未**指向智谱（若本 run 是 Mode C）  
- [ ] `python -m scripts.run_claude --help` 与 `python -m scripts.run_eval --dry-run` 可用  
