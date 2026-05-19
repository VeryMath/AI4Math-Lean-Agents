# Examples

## 示例 1：单文件运行（当前项目）

```bash
cd ~/numina-lean-agent
source .venv/bin/activate
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="sk-anything"
export ANTHROPIC_MODEL="anthropic-claude"

python -m scripts.run_claude run \
  /mnt/d/Lean/projects/stat-inference-lean/StatInferenceLean/Exercises/Week02.lean \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 3 \
  --cwd /mnt/d/Lean/projects/stat-inference-lean
```

## 示例 2：目录批量

```bash
python -m scripts.run_claude from-folder \
  /mnt/d/Lean/projects/stat-inference-lean/StatInferenceLean/Exercises \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 3 \
  --cwd /mnt/d/Lean/projects/stat-inference-lean
```

## 示例 3：批量配置并行

```bash
python -m scripts.run_claude batch config/config_minif2f.yaml --parallel --max-workers 4
```

## 示例 4：实时汇报模板

```text
[check] lean project root detected | pass
[check] litellm /v1/messages reachable | pass
[check] claude mcp in target scope | pass
[next action] run_claude run Week02.lean with max_rounds=3
```

## 示例 5：401 鉴权故障汇报模板

```text
[check] litellm started on :4000 | pass
[check] upstream model auth | fail
[next action] 更新上游 key 并重启 litellm，再重测 /v1/messages
```
