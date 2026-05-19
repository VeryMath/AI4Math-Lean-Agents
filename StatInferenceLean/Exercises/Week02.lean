import Mathlib
import StatInferenceLean.Probability.Defs

namespace StatInferenceLean
namespace Exercises

/-!
# Week 02 — 列表与有限和 / Week 02 — Lists and finite sums

## 复盘衔接 / Bridge from Week 01

- **中文**：Week 01 练了命题、等式重写、化简与少量数值等式。本周把对象换成 **列表** 与 **自然数上的和**，
  这是统计里「样本 \((x_1,\ldots,x_n)\)」「总和 \(\sum_i x_i\)」在形式化里的最小原型。
- **English**: Week 01 was about propositions, rewriting, and simplification. This week we use
  **lists** and **sums over `Nat`**, the minimal formal analogue of samples and finite sums in
  statistics.

## 本文件目标 / Goals

1. 熟悉 `List` 的基本记法与 `List.sum`（在 `Nat` 上）。  
   Get comfortable with `List` notation and `List.sum` over `Nat`.
2. 练习 `linarith`（线性实数不等式）与 `omega`（自然数上的类似推理）。  
   Practice `linarith` (linear arithmetic over `ℝ`) and `omega` (for `ℕ`).
3. 继续巩固 `rw` / `simp` / `norm_num`。  
   Keep drilling `rw`, `simp`, and `norm_num`.

## 与教材的联系 / Link to *Statistical Inference*

- **中文**：样本容量、观测值求和、算术平均的分子分母，在代码里常先表现为 **列表长度** 与 **列表元素和**。
- **English**: Sample size, sums of observations, and the pieces of the sample mean often appear as
  **list length** and **sum of entries** before we switch to full probability theory.
-/

/-!
------------------------------------------------------------------------------
### Example 1 — 列表长度（具体例子）/ List length (concrete)

**中文**  
- `List.length` 给出元素个数；这里用具体数字列表验证。

**English**  
- `List.length` counts elements; we check a small concrete list.

**战术 / Tactics**  
- `rfl`：当目标按定义「显然相等」时可用（此处长度由列表字面量唯一确定）。  
- `rfl`: reflexivity when the goal is definitionally equal.
-/

example : ([1, 2, 3] : List Nat).length = 3 := by
  rfl

/-!
------------------------------------------------------------------------------
### Example 2 — 列表上求和（自然数）/ Sum of a list of natural numbers

**中文**  
- `List.sum` 在加法幺半群上求和；`Nat` 上常用。  
- 验证 `1 + 2 + 3 = 6`。

**English**  
- `List.sum` adds all entries; on `Nat` this is the usual finite sum.  
- Check `1 + 2 + 3 = 6`.

**战术 / Tactics**  
- `norm_num`：归一化数值目标。  
- `norm_num`: normalize numeric goals.
-/

example : ([1, 2, 3] : List Nat).sum = 6 := by
  norm_num

/-!
------------------------------------------------------------------------------
### Example 3 — 线性算术（实数）/ Linear arithmetic over `ℝ`

**中文**  
- 已知两式，推出第三个线性关系；统计里常见「由约束推参数」。

**English**  
- Deduce a linear relation from hypotheses; common when manipulating constraints.

**战术 / Tactics**  
- `linarith`：在有序环/域上解线性等式与不等式（需导入 Mathlib）。  
- `linarith`: solve linear arithmetic goals over `ℝ` (and similar types) with Mathlib loaded.
-/

example (a b : Real) (h1 : a + b = 5) (h2 : a = 2) : b = 3 := by
  linarith

/-!
------------------------------------------------------------------------------
### Example 4 — 自然数上的 `omega` / The `omega` tactic on `ℕ`

**中文**  
- 对自然数，许多「加减乘 + 等式/不等式」目标可用 `omega` 自动完成。

**English**  
- For `ℕ`, many arithmetic goals involving `+`, `*`, `=`, `≤` are solved by `omega`.

**战术 / Tactics**  
- `omega`：决策 Presburger 算术（在自然数上极常用）。  
- `omega`: Presburger arithmetic; very useful on `ℕ`.
-/

example (a b : Nat) (h : a + b = 10) (ha : a = 4) : b = 6 := by
  rw [ha] at h
  omega

/-!
------------------------------------------------------------------------------
### Example 5 — `simp` 与列表 / `simp` and lists

**中文**  
- 空列表连接任意列表不改变；Mathlib 中有相应 `simp` 引理。

**English**  
- Appending an empty list on the left does nothing; Mathlib registers `simp` lemmas for this.

**战术 / Tactics**  
- `simp`：自动搜索可化简的等式。  
- `simp`: try registered simplification lemmas.
-/

example (xs : List Nat) : ([] ++ xs) = xs := by
  simp

/-!
------------------------------------------------------------------------------
### Example 6 — 与 `sampleMean` 的数值直觉（仍用 ℝ）/ Numeric sanity check (still on `ℝ`)

**中文**  
- 回顾项目里的 `Probability.sampleMean`：对实数列表取均值。  
- 与 Week 01 相同思路：`simp` 展开 + `norm_num`。

**English**  
- Recall `Probability.sampleMean` on `List ℝ`.  
- Same proof pattern as Week 01: unfold with `simp`, then `norm_num`.

**注意 / Note**  
- 仍是 **noncomputable** 定义；不要用 `native_decide`。  
- Still **noncomputable**; do not use `native_decide`.
-/

example : Probability.sampleMean [1, 2, 3] = 2 := by
  simp [Probability.sampleMean]
  norm_num

/-!
------------------------------------------------------------------------------
### Example 7 — 小定理：平均为 1 则和等于长度 / Mean 1 implies sum equals length

**中文**  
- 练习：若列表非空，且样本均值（按我们定义）为 `1`，则元素和等于长度。  
- 这是对「均值 × 个数 = 总和」的极简代数翻版（仅数值实例）。

**English**  
- Exercise: for a nonempty list, if our `sampleMean` equals `1`, then the sum equals the length.  
- A toy algebraic shadow of “mean × count = total”.

**提示 / Hint**  
- 先用 `simp [Probability.sampleMean]` 展开，再处理 `if` 分支（列表非空）。  
- Unfold `sampleMean`, then handle the `if` branch (nonempty list).
-/

theorem sum_eq_length_of_mean_one (xs : List Real) (hne : xs.length ≠ 0)
    (hm : Probability.sampleMean xs = 1) : xs.sum = xs.length := by
  simp [Probability.sampleMean, hne] at hm ⊢
  -- hm : xs.sum / ↑xs.length = 1  with  xs.length ≠ 0
  have hlen : (xs.length : Real) ≠ 0 := by
    exact_mod_cast hne
  -- Multiply both sides by length
  field_simp [hlen] at hm
  -- xs.sum = (xs.length : ℝ)
  linarith

/-!
## Week 02 自检清单 / Week 02 checklist

- [ ] 能独立写出 Example 1–6 的证明（可照抄再默写）。  
- [ ] 理解 `linarith` 与 `omega` 各自更擅长哪类目标。  
- [ ] 读过 Example 7 的证明思路（`field_simp` + `linarith` 可先当模板用）。

**English**  
- [ ] Reproduce Examples 1–6 without looking.  
- [ ] Know when to prefer `linarith` vs `omega`.  
- [ ] Read through Example 7 (`field_simp` + `linarith`) as a reusable pattern.
-/

theorem week02_checklist_done : True := by
  trivial

end Exercises
end StatInferenceLean
