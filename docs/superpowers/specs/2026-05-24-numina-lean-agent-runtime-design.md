# Numina Lean Agent Runtime Skill 设计

## 背景

当前的 `ai4math-lean-agents` skill 是一个有意保持轻量的“蒸馏版”直接 Lean coding-agent 工作流。它把公开 Numina 工作流当作设计来源，但不部署 Numina、不要求 Claude Code、不调用模型 API，也不把 Numina 当成证明后端。

新的工作要补上另一种模式：当用户明确想调用原版 Numina 时，创建一个独立的 sister skill，负责抓取官方上游 Numina Lean Agent、配置本地运行环境，并调用上游 runner。

## 目标

创建新 skill：`numina-lean-agent-runtime`。它指导 Codex 在本地部署并调用官方 `project-numina/numina-lean-agent` 仓库。

这个 skill 必须支持：

- 在本地 clone 或更新官方上游仓库；
- 配置所需本地工具和 Python 依赖；
- 为指定 Lean 项目运行上游 setup 流程；
- 在长时间运行前诊断缺失工具、Lean 项目布局问题和 API key 缺口；
- 调用上游 `scripts.run_claude` 的 `run`、`batch` 和 `from-folder` 任务；
- 保持这个 runtime 工作流和 `ai4math-lean-agents` 相互独立。

## 非目标

- 默认不 vendor、不 fork、不修改 Numina 源码。
- 不让 `ai4math-lean-agents` 依赖 Numina。
- 不声称离线可用，也不声称无需 key。
- 不隐藏上游 Numina 可能调用 Claude、外部服务或第三方 CLI skills。
- 不把密钥写入被 git 跟踪的文件。

## 仓库布局

```text
skills/
  AI4Math-Lean-Agents/
  Numina-Lean-Agent-Runtime/
    SKILL.md
    agents/
      openai.yaml
    config/
      numina_runtime.example.toml
    references/
      upstream_usage.md
    scripts/
      numina_runtime.py
    tests/
      test_numina_runtime.py
```

目录名使用 `Numina-Lean-Agent-Runtime/`，保持和当前仓库的技能包风格一致。skill frontmatter 和文档中的 skill 名使用 `numina-lean-agent-runtime`。

## 运行状态目录

默认运行状态放在 `.ai4math/numina-runtime/`，并且必须被 git 忽略。

```text
.ai4math/
  numina-runtime/
    upstream/            # clone 下来的官方 project-numina/numina-lean-agent
    projects/            # setup.sh 使用的可选项目工作区根目录
    results/             # wrapper 默认结果目录
    .env.local           # 可选本地环境变量覆盖，不跟踪
    numina_runtime.local.toml
```

wrapper 必须支持这些环境变量：

- `AI4MATH_NUMINA_HOME`：覆盖 runtime 根目录。
- `NUMINA_LEAN_AGENT_REPO`：仅在用户明确要求时覆盖上游仓库 URL。
- `NUMINA_LEAN_AGENT_REF`：可选 branch、tag 或 commit。

默认上游 URL 是 `https://github.com/project-numina/numina-lean-agent`。

## CLI Wrapper

`scripts/numina_runtime.py` 提供一层确定性 wrapper，负责包装上游 setup 和 runner 命令。

### `doctor`

输出 JSON 报告：

- 工具可用性：`git`、`curl`、`uv`、`elan`、`lean`、`lake`、`claude`、`python`；
- 上游 clone 状态和当前 commit；
- Python 环境状态；
- required/optional API key 是否存在，输出时必须 redacted；
- 如果传入 target，检查它是否位于 Lake 项目内。

`doctor` 不得调用外部模型 API。

credential 诊断必须区分：

- Claude 配置：`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_BASE_URL`、`ANTHROPIC_MODEL`，或已经登录可用的 `claude` CLI；
- Numina skill keys：`GEMINI_API_KEY`、`OPENAI_API_KEY`、`LEAN_LEANDEX_API_KEY`、`AXLE_API_KEY`；
- required keys 和 optional keys，因为上游 Numina 只在特定 backend 或工具路径下需要部分 key。

### `install`

把上游 Numina clone 或更新到 `.ai4math/numina-runtime/upstream`。

默认行为：

- 缺失时 clone；
- 已存在时 fetch；
- 仅在配置 `NUMINA_LEAN_AGENT_REF` 时 checkout 指定 ref；
- 如果上游 checkout 有本地修改，不覆盖，必须报告。

第一版必须支持 `--dry-run`，返回 clone/fetch/checkout 命令，但不实际执行。

### `configure`

为指定 Lean 项目运行上游 setup：

```bash
python scripts/numina_runtime.py configure --project-name myproofs
```

wrapper 需要：

- 确保上游仓库已安装；
- 从上游 `tutorial/` 目录运行 `tutorial/setup.sh <project-name>`；
- 当 `uv` 可用时，在上游根目录运行 `uv python install` 和 `uv sync`；
- 把路径和状态记录到本地 JSON/TOML metadata；
- 当 `claude`、API keys、Lean 或 Lake 配置缺失时，返回明确下一步。

`configure` 默认执行依赖同步，并支持 `--skip-sync`，给只想生成上游项目脚手架的用户使用。

### `run`

调用上游单目标模式：

```bash
python scripts/numina_runtime.py run \
  --target /path/to/Foo.lean \
  --prompt-file /path/to/prompt.md \
  --max-rounds 10
```

启动上游 Numina 前先验证：

- target 存在；
- target 位于包含 `lean-toolchain` 和 `lakefile.lean` 或 `lakefile.toml` 的 Lake 项目内；
- 已提供 prompt 或 prompt file；
- 上游安装和 Python 环境已存在。

实际上游命令应等价于：

```bash
python -m scripts.run_claude run <target> --prompt-file <prompt-file> --max-rounds <n> --result-dir <dir>
```

### `from-folder`

调用上游文件夹扫描模式：

```bash
python scripts/numina_runtime.py from-folder \
  --target /path/to/LeanFolder \
  --prompt-file prompts/autosearch/main_entry.md \
  --max-rounds 10
```

如果用户没有提供结果目录，wrapper 应默认使用 `.ai4math/numina-runtime/results/` 下的目录。

### `batch`

透传到上游 YAML 或 JSON config 的 batch 模式：

```bash
python scripts/numina_runtime.py batch --config /path/to/config.yaml
```

wrapper 必须先验证 config 文件存在，然后调用上游 `python -m scripts.run_claude batch`。

## Skill 行为

skill body 应指导 Codex：

1. 先确认用户想要官方 Numina runtime 模式，而不是蒸馏版 direct Lean 工作流。
2. 在安装或调用前先运行 `doctor`。
3. 用 `install` 抓取上游。
4. 第一次设置时用 `configure`。
5. 在 `run`、`batch` 或 `from-folder` 前验证目标 Lake 项目。
6. 报告缺失 credential，但不打印 secret value。
7. 把上游 runner 输出和 result directories 当作事实来源。
8. 只有当用户选择直接本地 Lean repair 时，才回退到 `ai4math-lean-agents`。

## 错误处理

wrapper 的所有命令都应返回 machine-readable JSON。

常见 status：

- `ready`：本地 runtime 可用。
- `missing_tool`：缺少必需可执行文件。
- `missing_upstream`：上游仓库尚未 clone。
- `upstream_dirty`：上游 checkout 有本地修改。
- `missing_credentials`：缺少模型或 skill API keys。
- `missing_lake_project`：target 不在 Lake 项目内。
- `setup_failed`：上游 setup 或 dependency sync 失败。
- `run_failed`：上游 runner 非零退出。

面向人的 diagnostics 应说明下一条具体命令。

## Secrets 和本地文件

被 git 跟踪的文件只能包含 example，例如：

```text
config/numina_runtime.example.toml
```

本地文件必须被忽略：

```text
.ai4math/numina-runtime/
```

wrapper 必须在存在时读取 `.ai4math/numina-runtime/.env.local`，输出时 redacted，并且除非用户明确要求，不写入用户密钥。

## 测试

默认测试必须离线且确定性。

必需单测覆盖：

- Lake project root detection；
- `install`、`configure`、`run`、`from-folder` 和 `batch` 的命令构造；
- missing tool diagnostics；
- missing upstream diagnostics；
- dirty upstream protection；
- key redaction；
- `.ai4math/numina-runtime` 下默认路径解析；
- JSON output shape。

默认测试不得 clone 上游、运行 `uv sync`、调用 `claude` 或调用外部 API。

可选集成测试可以用环境变量门控，例如 `AI4MATH_NUMINA_INTEGRATION=1`。

## 验证

实现可接受的条件：

- 新 skill 通过 skill validation；
- 仓库单测通过；
- wrapper 离线测试在无网络、无 API keys 情况下通过；
- `doctor` 在 fresh checkout 上能正常运行，并清楚报告缺失 runtime state；
- `install --dry-run` 或等价命令构造测试证明使用官方上游 URL；
- 现有 `ai4math-lean-agents` delivery verification 仍然通过。

## 实现决策

- 第一版必须支持 `install --dry-run`。
- `.env.local` 读取放在 wrapper 中，输出 redacted 状态。
- `configure` 默认运行 `uv sync`，并支持 `--skip-sync`。
- 第一版保持 per-skill 验证，不新增仓库级 `verify-all` helper。
