# AI4Math Lean Agents 调用原版 Numina 改造设计

## 背景

当前 `AI4Math-Lean-Agents` skill 的定位是“蒸馏版”直接 Lean coding-agent 工作流：Codex 自己读写 Lean，CLI 只做确定性 guardrail，并且文档明确写着不部署、不调用 Numina。

用户现在希望保留这个 skill 的总框架，但把定位改成：**自动抓取官方原版 Numina Lean Agent，在本地交互配置环境，然后调用上游 Numina runner**。直接 Lean 操作仍可作为诊断、review、最小失败 handoff 和 fallback，但不再是唯一主路径。

## 目标

改造现有 `skills/AI4Math-Lean-Agents/`，不新增 sister skill。

改造后，这个 skill 必须支持：

- clone 或更新官方 `project-numina/numina-lean-agent`；
- 本地配置 Numina 运行环境、Python 依赖、Claude CLI/API key 和相关 skill keys；
- 为用户的 Lean/Lake 项目调用官方 Numina runner；
- 在调用前检查工具、credential、Lake 项目结构和上游 checkout 状态；
- 保留现有 Lean/Lake 校验、patch review、`sorry` 检测、最小失败提取等 guardrails；
- 明确告诉用户：默认证明/修复路线会调用原版 Numina，可能产生外部 API 调用和费用。

## 非目标

- 不创建新的 `Numina-Lean-Agent-Runtime/` skill 目录。
- 默认不 vendor、不 fork、不修改 Numina 源码。
- 不把密钥写入 git 跟踪文件。
- 不假装离线、无 key、无外部 API 可完成 Numina 路线。
- 不删除现有直接 Lean 工具；它们继续服务于检查、review、fallback 和失败最小化。

## 保持不大动的现有框架

继续使用现有包：

```text
skills/
  AI4Math-Lean-Agents/
    SKILL.md
    agents/
      openai.yaml
    config/
    prompts/
    references/
    schemas/
    scripts/
    tests/
```

在现有框架内新增：

```text
skills/AI4Math-Lean-Agents/
  config/
    numina_runtime.example.toml
  references/
    numina_runtime.md
  scripts/
    numina_runtime.py
  tests/
    test_numina_runtime.py
```

并更新：

```text
skills/AI4Math-Lean-Agents/
  SKILL.md
  agents/openai.yaml
  scripts/ai4m_lean.py
  scripts/verify_delivery.py
  README.md
  AGENTS.md
  CLAUDE.md
  GEMINI.md
```

## 运行状态目录

Numina runtime 状态默认放在 `.ai4math/numina-runtime/`，必须被 `.ai4math/.gitignore` 忽略。

```text
.ai4math/
  numina-runtime/
    upstream/            # 官方 project-numina/numina-lean-agent clone
    projects/            # setup.sh 可用的本地项目工作区
    results/             # wrapper 默认结果目录
    .env.local           # 可选本地环境变量覆盖，不跟踪
    numina_runtime.local.toml
```

wrapper 必须支持：

- `AI4MATH_NUMINA_HOME`：覆盖 runtime 根目录。
- `NUMINA_LEAN_AGENT_REPO`：仅在用户明确要求时覆盖上游仓库 URL。
- `NUMINA_LEAN_AGENT_REF`：可选 branch、tag 或 commit。

默认上游 URL 固定为：

```text
https://github.com/project-numina/numina-lean-agent
```

## CLI 设计

继续用 `scripts/ai4m_lean.py` 作为总入口，但不增加一组平行的 `numina-*` 公开命令。Numina 部署和调用应该折叠进现有命令：

```bash
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py doctor --cwd .
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py repair --cwd . --file /path/to/Foo.lean --prompt-file /path/to/prompt.md
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py repair --cwd . --file /path/to/Foo.lean --direct --dry-run
```

底层实现放在 `scripts/numina_runtime.py`，但这些函数是内部实现细节。`ai4m_lean.py` 只公开少量现有入口：`doctor` 展示 Numina readiness，`configure --setup-numina` 执行安装/配置，证明修复类任务默认调用官方 Numina，`--direct` 保留旧 direct task envelope。

## 现有命令语义调整

### 保持原样的 guardrail 命令

这些命令继续是本地确定性工具，不调用外部 API：

- `env`
- `doctor`
- `check`
- `review`
- `detect-sorry`
- `minimize-failure`
- `verify-delivery`

其中 `doctor` 和 `env` 应补充 Numina runtime readiness 摘要，但不得自动 clone、安装或调用模型。

### 扩展 `configure`

现有 `configure --create-workspace` 继续保留，用于 Lean workspace。

新增可选 Numina 配置路径：

```bash
python scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs
```

它等价于执行：

1. 内部 Numina upstream install/update；
2. 内部 Numina setup/configure；
3. 可选 dependency sync，默认开启，可用 `--skip-numina-sync` 跳过。

### 改造任务命令

这些任务命令应默认进入 Numina runtime 路线：

- `prove`
- `formalize`
- `repair`
- `complete-sorries`
- `batch`

默认行为：

1. 检查 target 或 folder 是否存在。
2. 检查 target 是否在 Lake 项目内。
3. 检查 Numina runtime 是否已安装、依赖是否准备好、credential 是否足够。
4. 如果缺 runtime，返回 `missing_numina_runtime` 和下一步命令，不静默 fallback。
5. 如果 runtime ready，则构造并执行官方 Numina runner 命令。

为保留现有轻量能力，第一版允许 `--direct` 或 `--dry-run`：

- `--dry-run`：只返回 Numina command plan，不执行。
- `--direct`：沿用现有 direct coding-agent task envelope，用于用户明确要求不调用 Numina 的场景。

## Numina Runtime Wrapper

`scripts/numina_runtime.py` 需要提供可单测的纯函数。第一版不把这些函数全部暴露成公开 CLI 子命令。

### readiness/doctor helpers

供 `doctor` 和 `env` 调用，输出 JSON 片段，包含：

- `git`、`curl`、`uv`、`elan`、`lean`、`lake`、`claude`、`python` 可用性；
- 上游是否已 clone、当前 commit、是否 dirty；
- Python/uv 环境状态；
- credential 状态，必须 redacted；
- 目标路径的 Lake 项目检测结果。

credential 诊断区分：

- Claude 配置：`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_BASE_URL`、`ANTHROPIC_MODEL`，或已经可用的 `claude` CLI；
- Numina skill keys：`GEMINI_API_KEY`、`OPENAI_API_KEY`、`LEAN_LEANDEX_API_KEY`、`AXLE_API_KEY`；
- required 和 optional keys。

readiness/doctor helpers 不得调用外部模型 API。

### install helpers

clone 或更新官方 Numina：

- 缺失时 clone；
- 已存在时 fetch；
- 配置 `NUMINA_LEAN_AGENT_REF` 时 checkout 指定 ref；
- 上游 checkout dirty 时不覆盖，返回 `upstream_dirty`。

第一版必须支持：

```bash
python scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs --dry-run
```

`--dry-run` 返回将执行的 clone/fetch/checkout/setup/sync 命令，不实际执行。

### configure helpers

为指定 project name 运行上游 setup：

```bash
python scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs
```

行为：

- 确保上游已安装；
- 从上游 `tutorial/` 目录运行 `setup.sh <project-name>`；
- 默认在上游根目录运行 `uv python install` 和 `uv sync`；
- 支持 `--skip-sync`；
- 记录本地 metadata；
- 失败时返回 `setup_failed` 和具体 stderr/stdout 摘要。

### run helpers

供现有 `prove`、`formalize`、`repair` 和 `complete-sorries` 调用官方 runner：

```bash
python scripts/ai4m_lean.py repair \
  --cwd . \
  --file /path/to/Foo.lean \
  --prompt-file /path/to/prompt.md \
  --max-rounds 10
```

启动前必须验证：

- 文件存在；
- 文件在 Lake 项目内；
- prompt 或 prompt file 存在；
- 上游安装、uv 环境和 credential 状态可用。

实际上游命令等价于：

```bash
python -m scripts.run_claude run <file> --prompt-file <prompt-file> --max-rounds <n> --result-dir <dir>
```

### folder/batch helpers

供现有 `batch` 或未来 folder 任务调用：

```bash
python scripts/ai4m_lean.py batch --cwd . --folder /path/to/LeanFolder
```

默认 result dir 放在 `.ai4math/numina-runtime/results/`。

## Skill 文档改造

`SKILL.md` 需要从“Numina 不部署不调用”改成：

- 默认工作流是官方 Numina runtime assisted workflow；
- Codex 先用本地 guardrails 识别目标、检查 Lake 项目、检查 runtime；
- runtime 未安装时，引导 `configure --setup-numina --project-name ...`；
- runtime ready 时调用官方 Numina runner；
- runner 结束后用 `check`、`detect-sorry`、`review` 做交付前验证；
- 如果 Numina 路线失败，使用 `minimize-failure` 给出最小失败片段和下一步。

`references/numina_reverse_analysis.md` 可以保留，但应改为历史/背景材料，不再承担“只蒸馏不调用”的政策含义。

## 安全和本地文件

被 git 跟踪的文件只能包含 example config。

本地文件必须忽略：

```text
.ai4math/numina-runtime/
```

wrapper 必须读取 `.ai4math/numina-runtime/.env.local`（如果存在），但输出 redacted 状态，不打印真实 secret。除非用户明确要求，不写入用户密钥。

## 错误状态

新增或使用这些 status：

- `numina_ready`
- `missing_numina_runtime`
- `missing_numina_credentials`
- `missing_lake_project`
- `upstream_dirty`
- `numina_setup_failed`
- `numina_run_failed`
- `direct_task_ready`

`ai4m_lean.py` 需要把 Numina 相关失败映射到稳定 exit code，避免和 Lean 编译失败混淆。

## 测试

默认测试必须离线、确定性、无 API。

新增单测覆盖：

- Numina runtime 默认路径解析；
- `.ai4math/.gitignore` 写入 `numina-runtime/`；
- Lake project root detection 复用现有逻辑；
- `configure --setup-numina --dry-run` 使用官方上游 URL；
- dirty upstream 保护；
- credential redaction；
- `prove/repair/complete-sorries/batch --dry-run` 构造官方 Numina runner command plan；
- `prove/repair/complete-sorries/batch --dry-run` 走 Numina command plan；
- `--direct` 保留旧 direct task envelope；
- `verify-delivery` 检查新增文件和命令。

默认测试不得：

- clone 官方仓库；
- 运行 `uv sync`；
- 调用 `claude`；
- 调用外部 API。

可选集成测试用环境变量门控：

```text
AI4MATH_NUMINA_INTEGRATION=1
```

## 验收标准

实现完成时必须满足：

- `verify-delivery --run-tests` 通过；
- 新增 Numina runtime offline tests 通过；
- `configure --setup-numina --dry-run` 输出官方上游 URL；
- `doctor` 在未安装 runtime 的 fresh checkout 上清楚报告下一步；
- `SKILL.md`、README、AGENTS/CLAUDE/GEMINI 说明一致：本 skill 现在会部署并调用官方 Numina；
- 最终交付仍拒绝 `sorry`、`admit` 和新 `axiom`。

## 实现决策

- 不新增 sister skill，直接改造 `AI4Math-Lean-Agents`。
- 保留现有 direct Lean guardrails。
- 证明/修复类任务默认准备或调用 Numina runtime。
- 第一版必须支持 `--dry-run` 和 `--direct`，降低迁移风险。
- 默认 runtime 根目录是 `.ai4math/numina-runtime/`。
