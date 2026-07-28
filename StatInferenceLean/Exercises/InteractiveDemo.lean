import Mathlib

namespace StatInferenceLean
namespace Exercises

/-!
# InteractiveDemo — 冒烟 / Formalize 靶

## 角色

- **冒烟**：快速确认 Lean 工具链与本文件可 `lake env lean` / 随 `lake build` 通过。
- **Formalize**：自然语言定理 → 写入本文件（或同类 Exercises）后再走 Prove/Fix → Verify。
- 默认被 `StatInferenceLean.lean` import；保持证明正确，勿改成 broken。

## 如何使用

1. 光标放在 `by` 后查看目标。
2. `lake env lean StatInferenceLean/Exercises/InteractiveDemo.lean`（验证前移）。
3. 需要全仓时再 `lake build`。
4. Agent：`python -m scripts.run_claude run …/InteractiveDemo.lean`（见 Skill）。
-/

/-!
### Theorem — 加法交换律

对任意实数 `x` `y`，证明 `x + y = y + x`。  
可用 `exact add_comm x y` / `simp` / `ring`。
-/

theorem add_comm_demo (x y : ℝ) : x + y = y + x := by
  exact add_comm x y

end Exercises
end StatInferenceLean
