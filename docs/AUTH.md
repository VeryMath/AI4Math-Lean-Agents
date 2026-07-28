# AUTH — 认证速查

详细排障与启动清单以 Skill 为单源，避免双处漂移：

- 主流程与 Mode 选择：[`../.cursor/skills/lean-agent-numina/SKILL.md`](../.cursor/skills/lean-agent-numina/SKILL.md)
- 1211 树 / LiteLLM / DeepSeek：[`../.cursor/skills/lean-agent-numina/reference.md`](../.cursor/skills/lean-agent-numina/reference.md)
- 可复制命令：[`../.cursor/skills/lean-agent-numina/examples.md`](../.cursor/skills/lean-agent-numina/examples.md)
- 环境变量模板：[`.env.example`](../.env.example)

## 锁定摘要

| 模式 | 何时用 | BASE_URL | MODEL |
|------|--------|----------|-------|
| **A（默认）** | Gemini + LiteLLM（WSL） | `http://localhost:4000` | `anthropic-claude` → 映射 `gemini/gemini-2.5-pro` |
| **C（回退）** | Mode A 失败 / 无 LiteLLM | `https://api.deepseek.com/anthropic` | `deepseek-v4-flash`（或 `deepseek-v4-pro`） |
| B（可选） | Anthropic 直连 | `https://api.anthropic.com` | Claude 模型 id |

## 硬性禁止

1. 模型名含 ANSI / `[1m]` 等脏字符（复制终端高亮时易混入）  
2. `ANTHROPIC_BASE_URL` 指向 localhost（LiteLLM），同时 `ANTHROPIC_MODEL=deepseek*`  

## 启动检查清单（最短）

- [ ] 密钥只在环境变量 / 本地 `.env`（已 gitignore），未写入仓库  
- [ ] Mode A：WSL 内 LiteLLM 在 `:4000`，且 `NO_PROXY` 含 `localhost,127.0.0.1`  
- [ ] Mode A：`ANTHROPIC_MODEL=anthropic-claude`（不是 gemini 原始名、不是 deepseek）  
- [ ] Mode C：`BASE_URL` 为 DeepSeek Anthropic 端点，且 `API_KEY`/`AUTH_TOKEN` 已导出  
- [ ] `python -m scripts.run_claude --help` 在 `~/numina-lean-agent` 可用  
