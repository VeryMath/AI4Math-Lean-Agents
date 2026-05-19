# Reference

## 1) Lean 项目判定

目标文件必须位于可构建 Lean 项目中（祖先目录存在）：

- `lean-toolchain`
- `lakefile.toml` 或 `lakefile.lean`

快速检查：

```bash
pwd
ls
lake build
```

## 2) WSL 代理最小排障

获取 WSL 网关并测试：

```bash
GW=$(ip route | awk '/^default/ {print $3; exit}')
echo "$GW"
curl -I https://github.com --proxy http://$GW:7890 -m 8
```

设置会话代理：

```bash
export http_proxy="http://$GW:7890"
export https_proxy="http://$GW:7890"
export all_proxy="http://$GW:7890"
```

## 3) LiteLLM 本地启动（Gemini 后端）

示例配置：

```yaml
model_list:
  - model_name: anthropic-claude
    litellm_params:
      model: gemini/gemini-2.5-pro
      api_key: os.environ/GEMINI_API_KEY
```

启动：

```bash
litellm --config ~/litellm_config.yaml --port 4000
```

验证 Anthropic-compatible 端点：

```bash
export NO_PROXY=localhost,127.0.0.1
curl -s http://localhost:4000/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: sk-anything" \
  -d '{
    "model": "anthropic-claude",
    "max_tokens": 64,
    "messages": [{"role":"user","content":"reply ok"}]
  }'
```

## 4) MCP 目录作用域

在目标 Lean 项目目录执行：

```bash
cd <lean_project_root>
claude mcp add lean-lsp -- ~/lean-lsp-mcp/numina-lean-mcp.sh
claude mcp list
```

## 5) run_claude 常见失败速查

### 401 AuthenticationError

- 上游 key 不正确、过期、格式不符（例如必须 `sk-` 开头）。
- 终端未加载正确环境变量（新开终端丢失）。

### MCP not connected

- 在错误目录执行了 `claude mcp add`。
- 需在当前目标 Lean 项目目录重加。

### lake=fail

- 目标文件不在 Lake 项目里。
- 先切到 `lakefile` 所在目录验证 `lake build`。

### proxy connect refused

- 端口不对或代理未监听局域网。
- 先测端口，再确认 Clash/代理软件启用了 LAN。
