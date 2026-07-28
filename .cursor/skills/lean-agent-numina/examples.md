# Examples

## 示例 0：阶段检查点模板

```text
[check] stage=Inspect target=InteractiveDemo.lean | pass
[check] stage=Workspace Mode A litellm :4000 | fail
[check] stage=Workspace fallback Mode C | pass
[next action] python -m scripts.run_claude run ... --max-rounds 1
```

## 示例 1：Mode A（Gemini + LiteLLM，WSL）

```bash
# 终端 1（WSL）：LiteLLM
export GEMINI_API_KEY='...'
litellm --config ~/litellm_config.yaml --port 4000

# 终端 2（WSL）：Numina
cd ~/numina-lean-agent
source .venv/bin/activate
export PYTHONPATH="$PWD"
export NO_PROXY=localhost,127.0.0.1
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="sk-anything"
export ANTHROPIC_MODEL="anthropic-claude"

python -m scripts.run_claude run \
  /mnt/d/Lean/projects/stat-inference-lean/StatInferenceLean/Exercises/InteractiveDemo.lean \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 3 \
  --cwd /mnt/d/Lean/projects/stat-inference-lean \
  --max-model-tier 3
```

验证前移：

```bash
cd /mnt/d/Lean/projects/stat-inference-lean
lake env lean StatInferenceLean/Exercises/InteractiveDemo.lean
```

## 示例 2：Mode C 回退（DeepSeek）

```bash
cd ~/numina-lean-agent
source .venv/bin/activate
export PYTHONPATH="$PWD"
export DEEPSEEK_API_KEY='...'
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_API_KEY="$DEEPSEEK_API_KEY"
export ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_API_KEY"
export ANTHROPIC_MODEL="deepseek-v4-flash"

python -m scripts.run_claude run \
  /mnt/d/Lean/projects/stat-inference-lean/StatInferenceLean/Exercises/Week01.lean \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 3 \
  --cwd /mnt/d/Lean/projects/stat-inference-lean
```

## 示例 3：Error Bank Fixture

```bash
# 负例：应失败（unknown identifier）
lake env lean StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.broken.lean

# 正例：应通过
lake env lean StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.fixed.lean

# Agent 修 broken（勿把 broken import 进根模块）
python -m scripts.run_claude run \
  /mnt/d/Lean/projects/stat-inference-lean/StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.broken.lean \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 5 \
  --cwd /mnt/d/Lean/projects/stat-inference-lean \
  --max-model-tier 3
```

## 示例 4：Bernoulli 单独验证

```bash
lake env lean StatInferenceLean/Exercises/Bernoulli.lean
```

## 示例 5：目录批量 / batch

```bash
python -m scripts.run_claude from-folder \
  /mnt/d/Lean/projects/stat-inference-lean/StatInferenceLean/Exercises \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 3 \
  --cwd /mnt/d/Lean/projects/stat-inference-lean
```

```bash
python -m scripts.run_claude batch config/config_minif2f.yaml --parallel --max-workers 4
```

## 示例 6：OpenCode 会话指令

```text
调用 numina-lean-agent。按阶段：Inspect → Workspace → Formalize → Prove/Fix → Verify → Memory。
目标：把「任意实数 x y，证明 x+y=y+x」写到 StatInferenceLean/Exercises/InteractiveDemo.lean。
认证优先 Mode A，失败回退 Mode C。验证用 lake env lean。输出 [check]/[next action]。
```

## 示例 7：1211 汇报模板

```text
[check] ANTHROPIC_MODEL clean (no [1m]) | pass
[check] Mode consistency BASE_URL vs MODEL | fail
[next action] 当前是 localhost LiteLLM，将 ANTHROPIC_MODEL 改为 anthropic-claude（不要用 deepseek）
```

## 示例 8：反模式（禁止）

```bash
# 错误：LiteLLM + deepseek 混用
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_MODEL="deepseek-v4-flash"   # 禁止
```
