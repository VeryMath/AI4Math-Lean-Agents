# 案例：从安装 Lean skills 到验证第一个定理

这个案例来自一次真实的 coding-agent 交互：用户先让 agent 安装 AI4Math Lean skills，随后使用 `lean-setup` 建立共享 Lean/mathlib 工作区，最后验证一个最小的 `Nat` 定理。它适合作为第一次使用本仓库的端到端样例。

## 原始会话截图

![AI4Math Lean Skills 安装和 AddZero 验证会话截图](images/lean-setup-add-zero-session.png)

截图用于展示真实交互形态；可复制的 prompt、规则和 Lean 文件见下文。

## 适用目标

- 安装 `lean-setup`、`lean-formalization` 和 sibling 的 `lean-runtime` 支持层。
- 检查 `elan`、`lean`、`lake` 是否可用。
- 创建或复用 `~/.ai4math/lean-workspace`。
- 用一个最小 Lean 定理确认工作区能够编译。

## 用户可以这样发起

```text
请帮我安装 AI4Math Lean Skills。

仓库：https://github.com/VeryMath/AI4Math-Lean-Agents.git
分支：main
Skill 路径：
- skills/lean-setup
- skills/lean-formalization

安装后请验证这两个 skills 可用，并同时保留 sibling 的 skills/lean-runtime 支持目录。
```

安装完成后，继续运行 setup-only 检查：

```text
Use lean-setup:

请帮我检查当前环境是否已安装 Lean 4，如果缺少则安装，并创建一个可复用的 mathlib 工作区。
```

当 agent 报告 Lean/Lake 可用、共享工作区已存在或已创建后，可以继续请求一个最小验证：

```text
请将 `forall n : Nat, n + 0 = n` 形式化为 Lean 4，并在刚才的共享工作区里验证。
```

命令行验证通过后，也可以让 agent 继续引导人类 IDE 前端配置：

```text
现在请继续引导我完成这个 Lean workspace 的 VS Code 前端配置。

请告诉我应该在 VS Code 中打开哪个目录、先打开哪个 `.lean` 文件、
如何安装或确认 Lean 4 extension，以及我在 Lean InfoView 里应该看到什么，
才能确认 IDE 使用的是刚才通过 smoke test 的同一套 toolchain。
```

## Agent 应该怎么做

1. 读取 `AGENTS.md` 和对应的 skill entrypoint。
2. 对安装任务使用 `lean-setup`，不要向用户索要 theorem target。
3. 优先复用现有 Lean/Lake 项目；没有项目时使用 `~/.ai4math/lean-workspace`。
4. 默认使用 `leanprover/lean4:v4.28.0` 管理 standalone workspace，除非用户明确覆盖。
5. 在写入或编译 Lean 文件前说明路径与目标。
6. 运行 Lean/Lake 验证，并报告具体结果。
7. 如果用户希望配置 IDE 前端，引导其在 VS Code 中打开已验证的 Lake project 或共享 workspace，安装 Lean 4 extension，并确认 Lean InfoView 已连接。
8. 不把本机临时路径、下载缓存、API key 或 Numina runtime 状态提交到仓库。

## 可验证的最小 Lean 文件

在共享 workspace 的 `LeanWorkspace/` 下创建一个文件，例如 `AddZero.lean`：

```lean
import Mathlib.Tactic

theorem my_add_zero (n : Nat) : n + 0 = n := by
  induction n with
  | zero =>
      rfl
  | succ n ih =>
      calc
        Nat.succ n + 0 = Nat.succ (n + 0) := rfl
        _ = Nat.succ n := by rw [ih]
```

一个合格结果应该说明：

- `lean` 和 `lake` 来自 `elan` toolchain；
- workspace 路径是共享工作区，而不是临时下载目录；
- `AddZero.lean` 已通过 Lean 检查；
- 如果 theorem 名称冲突，agent 应重命名 declaration 后重新验证；
- 没有引入 `sorry`、`admit` 或新的 `axiom`。

## 这个案例体现的仓库规则

- setup-only 任务只使用 `lean-setup`，不要求用户提供 theorem。
- 形式化或 proof repair 才交给 `lean-formalization`。
- 默认 coding-agent 路径不需要 API key，也不默认调用 Numina。
- VS Code 和 Lean InfoView 推荐用于人类查看 proof state，但不能替代本地 Lean/Lake 验证。
- Numina、Archon 或其他 backend 只有在用户明确要求 optional backend adapter 时才进入流程。
- 最终交付必须以本地 Lean/Lake 验证结果为准。
