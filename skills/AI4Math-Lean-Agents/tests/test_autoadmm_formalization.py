from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


THIS_FILE = Path(__file__).resolve()
if (THIS_FILE.parents[1] / "autoadmm-formalization").exists():
    SKILL_ROOT = THIS_FILE.parents[1]
    ROOT = SKILL_ROOT.parents[1]
else:
    ROOT = THIS_FILE.parents[1]
    SKILL_ROOT = ROOT / "skills" / "AI4Math-Lean-Agents"
SCRIPT = SKILL_ROOT / "autoadmm-formalization" / "scripts" / "autoadmm_formalize.py"
SKILL_DIR = SKILL_ROOT / "autoadmm-formalization"


VALID_PROGRAM = """
def tau(k, c=1.0, p=1.2):
    return c / ((k + 1.0) ** p)


def update_rho(rho, k, r_norm, s_norm, mu=3.0, c=1.0, p=1.2, eps=1e-12):
    t = tau(k, c, p)
    if r_norm > mu * max(s_norm, eps):
        new_rho = rho * (1.0 + t)
        mode = "mul"
    elif s_norm > mu * max(r_norm, eps):
        new_rho = rho / (1.0 + t)
        mode = "div"
    else:
        new_rho = rho
        mode = "keep"
    aux = t
    return new_rho, aux, mode
"""


DIRECT_RETURN_PROGRAM = """
def tau(k, c=1.0, p=1.2):
    return c / ((k + 1.0) ** p)


def update_rho(rho, k, r_norm, s_norm, mu=3.0, c=1.0, p=1.2, eps=1e-12):
    t = tau(k, c, p)
    if r_norm > mu * max(s_norm, eps):
        return rho * (1.0 + t), t, "mul"
    elif s_norm > mu * max(r_norm, eps):
        return rho / (1.0 + t), t, "div"
    return rho, t, "keep"
"""


INVALID_DIRECT_RETURN_PROGRAM = """
def tau(k, c=1.0, p=1.2):
    return c / ((k + 1.0) ** p)


def update_rho(rho, k, r_norm, s_norm, mu=3.0, c=1.0, p=1.2, eps=1e-12):
    t = tau(k, c, p)
    if r_norm > mu * max(s_norm, eps):
        return rho * (1.0 + 0.5 * t), t, "inc"
    return rho, t, "keep"
"""


SHIFTED_TAU_PROGRAM = """
def tau(k, c=0.2, p=2.0, K0=5):
    if k < K0:
        return 0.0
    return c / ((k - K0 + 1.0) ** p)


def update_rho(rho, k, r_norm, s_norm, mu=2.0, c=0.2, p=2.0, eps=1e-12):
    t = tau(k, c, p)
    if r_norm > mu * max(s_norm, eps):
        return rho * (1.0 + t), t, "mul"
    elif s_norm > mu * max(r_norm, eps):
        return rho / (1.0 + t), t, "div"
    return rho, t, "keep"
"""


INVALID_PROGRAM = """
import numpy as np


def tau(k, c=1.0, p=1.2):
    return c / ((k + 1) ** p)


def update_rho(rho, k, r_norm, s_norm, mu=3.0, c=1.0, p=1.2, eps=1e-12):
    r_ratio = r_norm / max(s_norm, eps)
    s_ratio = s_norm / max(r_norm, eps)
    residual_scale = np.log10(max(r_norm, s_norm, eps) + 1.0)
    t = tau(k, c, p)
    if r_ratio > mu:
        factor = 1.0 + residual_scale * t
        new_rho = rho * factor
        mode = "mul"
    elif s_ratio > mu:
        factor = 1.0 + residual_scale * t
        new_rho = rho / factor
        mode = "div"
    else:
        new_rho = rho
        mode = "keep"
    new_rho = max(min(new_rho, 1e6), 1e-6)
    aux = max(r_ratio, s_ratio)
    return new_rho, aux, mode
"""


class AutoADMMFormalizationTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def write_program(self, directory: Path, source: str) -> Path:
        path = directory / "candidate.py"
        path.write_text(source.strip() + "\n", encoding="utf-8")
        return path

    def load_script_module(self):
        spec = importlib.util.spec_from_file_location("autoadmm_formalize_under_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def test_inspect_accepts_strategy3_safe_update(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            program = self.write_program(Path(tmp), VALID_PROGRAM)

            result = self.run_script("inspect", "--program", str(program), "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["valid"])
            self.assertEqual(payload["classification"], "L1-pseries-ratio-balance")
            self.assertEqual(payload["checks"]["R3"]["status"], "satisfied")
            self.assertEqual(payload["checks"]["R6"]["status"], "satisfied")

    def test_inspect_accepts_strategy3_safe_direct_return_update(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            program = self.write_program(Path(tmp), DIRECT_RETURN_PROGRAM)

            result = self.run_script("inspect", "--program", str(program), "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["valid"])
            self.assertEqual(payload["violated_rules"], [])
            self.assertEqual(payload["checks"]["R4"]["status"], "satisfied")
            self.assertEqual(payload["checks"]["R5"]["status"], "satisfied")

    def test_inspect_rejects_residual_dependent_factor_and_clipping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            program = self.write_program(Path(tmp), INVALID_PROGRAM)

            result = self.run_script("inspect", "--program", str(program), "--json")

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["valid"])
            self.assertEqual(payload["checks"]["R5"]["status"], "violated")
            self.assertEqual(payload["checks"]["R6"]["status"], "violated")
            joined = "\n".join(payload["issues"])
            self.assertIn("numeric update factor", joined)
            self.assertIn("post-processing", joined)
            self.assertIn("Strategy3-safe rewrite", payload["formal_feedback"])
            self.assertIn("Do not introduce factor", payload["repair_guidance"])
            self.assertIn("new_rho = rho * (1.0 + t)", payload["repair_template"])

    def test_inspect_rejects_invalid_direct_return_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            program = self.write_program(Path(tmp), INVALID_DIRECT_RETURN_PROGRAM)

            result = self.run_script("inspect", "--program", str(program), "--json")

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertIn("R4", payload["violated_rules"])
            self.assertIn("R5", payload["violated_rules"])
            self.assertIn("R7", payload["violated_rules"])
            self.assertIn("mode", "\n".join(payload["issues"]))

    def test_inspect_rejects_shifted_piecewise_tau_not_supported_by_current_lean_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            program = self.write_program(Path(tmp), SHIFTED_TAU_PROGRAM)

            result = self.run_script("inspect", "--program", str(program), "--json")

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertIn("R1", payload["violated_rules"])
            self.assertIn("R2", payload["violated_rules"])
            self.assertIn("R3", payload["violated_rules"])
            self.assertIn("supported p-series", "\n".join(payload["issues"]))

    def test_audit_summarizes_python_and_json_code_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self.write_program(tmp_path, DIRECT_RETURN_PROGRAM)
            (tmp_path / "bad.json").write_text(
                json.dumps({"id": "bad", "code": INVALID_DIRECT_RETURN_PROGRAM}),
                encoding="utf-8",
            )
            (tmp_path / "metadata.json").write_text(
                json.dumps({"id": "skip", "metrics": {"score": 1.0}}),
                encoding="utf-8",
            )

            result = self.run_script("audit", "--path", str(tmp_path), "--json")

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["total"], 2)
            self.assertEqual(payload["valid_count"], 1)
            self.assertEqual(payload["invalid_count"], 1)
            self.assertEqual(payload["violated_rule_counts"]["R4"], 1)
            self.assertEqual(payload["violated_rule_counts"]["R5"], 1)
            self.assertEqual(payload["violated_rule_counts"]["R7"], 1)

    def test_audit_reports_highest_scoring_valid_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "invalid_high.json").write_text(
                json.dumps(
                    {
                        "id": "invalid-high",
                        "code": INVALID_PROGRAM,
                        "metrics": {"combined_score": 0.9},
                    }
                ),
                encoding="utf-8",
            )
            (tmp_path / "valid_low.json").write_text(
                json.dumps(
                    {
                        "id": "valid-low",
                        "code": DIRECT_RETURN_PROGRAM,
                        "metrics": {"combined_score": 0.1},
                    }
                ),
                encoding="utf-8",
            )
            (tmp_path / "valid_high.json").write_text(
                json.dumps(
                    {
                        "id": "valid-high",
                        "code": DIRECT_RETURN_PROGRAM,
                        "metrics": {"combined_score": 0.2},
                    }
                ),
                encoding="utf-8",
            )
            self.write_program(tmp_path, DIRECT_RETURN_PROGRAM)

            result = self.run_script("audit", "--path", str(tmp_path), "--json")

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["valid_count"], 3)
            self.assertEqual(payload["invalid_count"], 1)
            self.assertEqual(payload["best_valid_candidate"]["path"], "valid_high.json")
            self.assertEqual(payload["best_valid_candidate"]["id"], "valid-high")
            self.assertEqual(payload["best_valid_candidate"]["score"], 0.2)

    def test_audit_summary_only_omits_candidate_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self.write_program(tmp_path, DIRECT_RETURN_PROGRAM)
            (tmp_path / "bad.json").write_text(
                json.dumps({"id": "bad", "code": INVALID_DIRECT_RETURN_PROGRAM}),
                encoding="utf-8",
            )

            result = self.run_script("audit", "--path", str(tmp_path), "--summary-only", "--json")

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["total"], 2)
            self.assertEqual(payload["valid_count"], 1)
            self.assertEqual(payload["invalid_count"], 1)
            self.assertIn("best_valid_candidate", payload)
            self.assertNotIn("candidates", payload)

    def test_audit_can_write_highest_scoring_valid_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output = tmp_path / "selected.py"
            (tmp_path / "valid_low.json").write_text(
                json.dumps(
                    {
                        "id": "valid-low",
                        "code": DIRECT_RETURN_PROGRAM.replace("mu=3.0", "mu=4.0"),
                        "metrics": {"combined_score": 0.1},
                    }
                ),
                encoding="utf-8",
            )
            (tmp_path / "valid_high.json").write_text(
                json.dumps(
                    {
                        "id": "valid-high",
                        "code": DIRECT_RETURN_PROGRAM,
                        "metrics": {"combined_score": 0.2},
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_script(
                "audit",
                "--path",
                str(tmp_path),
                "--write-best",
                str(output),
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["written_best"]["candidate"]["id"], "valid-high")
            self.assertEqual(output.read_text(encoding="utf-8"), DIRECT_RETURN_PROGRAM)

    def test_audit_can_exclude_initial_and_select_evolved_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            initial = self.write_program(tmp_path, DIRECT_RETURN_PROGRAM)
            output = tmp_path / "selected.py"
            evolved_program = DIRECT_RETURN_PROGRAM.replace("mu=3.0", "mu=2.5")
            (tmp_path / "initial_high.json").write_text(
                json.dumps(
                    {
                        "id": "initial-high",
                        "code": DIRECT_RETURN_PROGRAM,
                        "generation": 0,
                        "parent_id": None,
                        "metrics": {"combined_score": 0.9},
                    }
                ),
                encoding="utf-8",
            )
            (tmp_path / "evolved_low.json").write_text(
                json.dumps(
                    {
                        "id": "evolved-low",
                        "code": evolved_program,
                        "generation": 2,
                        "parent_id": "initial-high",
                        "metrics": {"combined_score": 0.2},
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_script(
                "audit",
                "--path",
                str(tmp_path),
                "--min-generation",
                "1",
                "--exclude-program",
                str(initial),
                "--write-best",
                str(output),
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["best_valid_candidate"]["id"], "evolved-low")
            self.assertEqual(payload["best_valid_candidate"]["generation"], 2)
            self.assertEqual(payload["written_best"]["candidate"]["id"], "evolved-low")
            self.assertEqual(output.read_text(encoding="utf-8"), evolved_program)

    def test_explore_ranks_non_strategy3_evolved_candidate_without_hard_rejecting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            initial = self.write_program(tmp_path, DIRECT_RETURN_PROGRAM)
            (tmp_path / "initial_seed.json").write_text(
                json.dumps(
                    {
                        "id": "initial-seed",
                        "code": DIRECT_RETURN_PROGRAM,
                        "generation": 0,
                        "parent_id": None,
                        "metrics": {"combined_score": 1.0},
                    }
                ),
                encoding="utf-8",
            )
            (tmp_path / "risky_evolved.json").write_text(
                json.dumps(
                    {
                        "id": "risky-evolved",
                        "code": INVALID_PROGRAM,
                        "generation": 3,
                        "parent_id": "initial-seed",
                        "metrics": {"combined_score": 0.9},
                    }
                ),
                encoding="utf-8",
            )
            (tmp_path / "safe_evolved.json").write_text(
                json.dumps(
                    {
                        "id": "safe-evolved",
                        "code": DIRECT_RETURN_PROGRAM.replace("mu=3.0", "mu=2.5"),
                        "generation": 2,
                        "parent_id": "initial-seed",
                        "metrics": {"combined_score": 0.2},
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_script(
                "explore",
                "--path",
                str(tmp_path),
                "--min-generation",
                "1",
                "--exclude-program",
                str(initial),
                "--top-n",
                "2",
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "exploration_ready")
            self.assertEqual(payload["workflow"]["mode"], "soft-gate")
            self.assertEqual(payload["candidates"][0]["id"], "risky-evolved")
            self.assertFalse(payload["candidates"][0]["valid"])
            self.assertEqual(payload["candidates"][0]["proof_route"], "exploratory-coding-agent")
            self.assertEqual(payload["candidates"][0]["static_gate_status"], "strict_fail")
            self.assertEqual(payload["candidates"][1]["id"], "safe-evolved")
            self.assertEqual(payload["candidates"][1]["proof_route"], "strict-template")

    def test_audit_reports_non_candidate_python_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "helper.py").write_text("def helper():\n    return 1\n", encoding="utf-8")

            result = self.run_script("audit", "--path", str(tmp_path), "--json")

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["total"], 1)
            self.assertEqual(payload["invalid_count"], 1)
            self.assertEqual(payload["candidates"][0]["violated_rules"], [f"R{i}" for i in range(1, 8)])
            self.assertIn("update_rho was not found", payload["candidates"][0]["first_issue"])

    def test_render_generates_sorry_free_strategy3_template_for_valid_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            program = self.write_program(tmp_path, VALID_PROGRAM)
            output = tmp_path / "auto_update_rho_generated.lean"

            result = self.run_script(
                "render-lean",
                "--program",
                str(program),
                "--output",
                str(output),
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["valid"])
            self.assertEqual(Path(payload["lean_file"]), output.resolve())
            lean = output.read_text(encoding="utf-8")
            self.assertIn("def tau_seq", lean)
            self.assertIn("def dir_seq", lean)
            self.assertIn("theorem auto_converges", lean)
            self.assertNotIn("sorry", lean)
            self.assertNotIn("admit", lean)

    def test_certify_best_writes_candidate_renders_lean_and_verifies(self) -> None:
        module = self.load_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            openevolve_output = tmp_path / "openevolve_output"
            openevolve_output.mkdir()
            candidate_output = tmp_path / "formal_best.py"
            project_root = tmp_path / "lean_project"
            project_root.mkdir()
            lean_output = project_root / "Optlib" / "Algorithm" / "AdaptiveADMM" / "Strategies" / "auto.lean"
            (openevolve_output / "invalid_high.json").write_text(
                json.dumps(
                    {
                        "id": "invalid-high",
                        "code": INVALID_PROGRAM,
                        "metrics": {"combined_score": 0.9},
                    }
                ),
                encoding="utf-8",
            )
            (openevolve_output / "valid_high.json").write_text(
                json.dumps(
                    {
                        "id": "valid-high",
                        "code": DIRECT_RETURN_PROGRAM,
                        "metrics": {"combined_score": 0.2},
                    }
                ),
                encoding="utf-8",
            )

            with patch.object(
                module.subprocess,
                "run",
                return_value=types.SimpleNamespace(returncode=0, stdout="", stderr=""),
            ) as run:
                payload = module.certify_best(
                    openevolve_output,
                    project_root,
                    candidate_output,
                    lean_output,
                )

            self.assertTrue(payload["ok"], payload)
            self.assertEqual(payload["audit"]["best_valid_candidate"]["id"], "valid-high")
            self.assertEqual(payload["candidate_file"], str(candidate_output.resolve()))
            self.assertEqual(payload["lean_file"], str(lean_output.resolve()))
            self.assertTrue(payload["lean_verify"]["ok"])
            self.assertEqual(candidate_output.read_text(encoding="utf-8"), DIRECT_RETURN_PROGRAM)
            self.assertIn("theorem auto_converges", lean_output.read_text(encoding="utf-8"))
            run.assert_called_once()

    def test_certify_best_cli_can_write_report_file(self) -> None:
        module = self.load_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            openevolve_output = tmp_path / "openevolve_output"
            openevolve_output.mkdir()
            candidate_output = tmp_path / "formal_best.py"
            project_root = tmp_path / "lean_project"
            project_root.mkdir()
            lean_output = project_root / "Optlib" / "Algorithm" / "AdaptiveADMM" / "Strategies" / "auto.lean"
            report_output = tmp_path / "certificate.json"
            (openevolve_output / "valid.json").write_text(
                json.dumps(
                    {
                        "id": "valid",
                        "code": DIRECT_RETURN_PROGRAM,
                        "metrics": {"combined_score": 0.2},
                    }
                ),
                encoding="utf-8",
            )

            with patch.object(
                module.subprocess,
                "run",
                return_value=types.SimpleNamespace(returncode=0, stdout="", stderr=""),
            ):
                with redirect_stdout(io.StringIO()):
                    exit_code = module.main(
                        [
                            "certify-best",
                            "--openevolve-output",
                            str(openevolve_output),
                            "--project-root",
                            str(project_root),
                            "--candidate-output",
                            str(candidate_output),
                            "--lean-output",
                            str(lean_output),
                            "--report-output",
                            str(report_output),
                            "--json",
                        ]
                    )

            self.assertEqual(exit_code, 0)
            report = json.loads(report_output.read_text(encoding="utf-8"))
            self.assertTrue(report["ok"])
            self.assertEqual(report["written_best"]["candidate"]["id"], "valid")
            self.assertEqual(report["candidate_file"], str(candidate_output.resolve()))
            self.assertEqual(report["report_file"], str(report_output.resolve()))

    def test_verify_lean_non_json_output_uses_payload_streams(self) -> None:
        module = self.load_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            project_root = tmp_path / "lean_project"
            project_root.mkdir()
            lean_file = project_root / "Generated.lean"
            lean_file.write_text("#check Nat\n", encoding="utf-8")

            with patch.object(
                module.subprocess,
                "run",
                return_value=types.SimpleNamespace(returncode=0, stdout="ok\n", stderr=""),
            ):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    exit_code = module.main(
                        [
                            "verify-lean",
                            "--project-root",
                            str(project_root),
                            "--lean-file",
                            str(lean_file),
                        ]
                    )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stdout.getvalue(), "ok\n")
            self.assertEqual(stderr.getvalue(), "")

    def test_skill_files_are_present(self) -> None:
        self.assertTrue((SKILL_DIR / "SKILL.md").exists())
        self.assertTrue((SKILL_DIR / "agents" / "openai.yaml").exists())
        self.assertTrue((SKILL_DIR / "references" / "strategy3_contract.md").exists())
        self.assertTrue(SCRIPT.exists())


if __name__ == "__main__":
    unittest.main()
