# MODEL ROUTING — 分层路由与类别门控（Phase 2）

主 KPI：**端到端成功率**。默认 `--max-model-tier` 可到 **3**，但升 tier 受 **错误类别门控**；同诊断指纹无效重试 ≤ **1**。

## Tier 定义

| Tier | 角色 | Mode A（LiteLLM `:4000`） | Mode C（DeepSeek 直连） |
|------|------|---------------------------|-------------------------|
| 0 | 规则自动修复 | （无 LLM） | （无 LLM） |
| 1 | 快 | `anthropic-claude` → `gemini/gemini-2.5-pro` | `deepseek-v4-flash` |
| 2 | 标准 | `anthropic-claude`（已注册别名） | `deepseek-v4-pro` |
| 3 | 强 | `anthropic-claude-strong`（须在 LiteLLM 注册）或 **切 Mode C** | `deepseek-v4-pro` |

### 硬性禁止

- `ANTHROPIC_BASE_URL` 为 `localhost:4000` 时，**禁止**把 `deepseek*` 模型名打到代理（会 1211）。
- 升 tier：Mode A 只用已注册别名；需要更强且无别名时 → 切 Mode C 的 `deepseek-v4-pro`。

## 类别 → 允许最高 tier

| 错误类 | 最高 tier | 说明 |
|--------|-----------|------|
| `syntax` | 1 | 优先 tier-0 规则 |
| `type` | 2 | |
| `dependency` | 2 | 缺 import / 未知标识符 |
| `proof` | 3 | 战术 / 未解 goal 可到强模型 |
| `unknown` | 2 | 无分类时的默认帽 |

有效上限 = `min(全局 max-model-tier, 类别帽)`；多错误并存时取各类别帽的 **最大值**。

## 升级策略

```text
失败 → tier-0 规则（若启用）
     → 注入 Success 最小 diff + Error 短策略
     → 同指纹在本 tier 最多再试 1 次
     → 仍无诊断变化 / 仍失败 → escalate（受类别帽）
     → 已到类别帽且重试用尽 → stop（不再盲升）
```

「无诊断变化不 escalate」：同一 fingerprint 在首次失败时 **不立刻**升 tier，允许同 tier 再试一次；第二次同指纹失败才 escalate。

## 与 Skill / CLI 的 flags

```bash
python -m scripts.run_claude run <file> \
  --cwd <lean_root> \
  --max-model-tier 3 \
  --initial-model-tier 1 \
  --error-bank true \          # 默认开；关闭：--no-error-bank / error_bank=False
  --success-bank true \        # 默认开
  --enable-auto-fix true \
  --auth-mode A                # 可选；默认从 BASE_URL 推断
```

详见 Skill [`lean-agent-numina`](../.cursor/skills/lean-agent-numina/SKILL.md) 与 [`docs/AUTH.md`](AUTH.md)。

## 实现位置

- `~/numina-lean-agent/scripts/error_bank/model_tiers.py`
- Orchestrator：`scripts/error_bank/orchestrator.py`
- 镜像：`d:\Lean\temp\error_bank_implementation\`
