from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = SKILL_ROOT.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from ai4m_lean import EXIT_LEAN_FAILED, _exit_code  # noqa: E402
from verify_delivery import _lean_setup_entrypoint_check, _package_hygiene, _root_discovery_boundary_check  # noqa: E402

CLI = SKILL_ROOT / "scripts" / "ai4m_lean.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class CliTests(unittest.TestCase):
    def test_dry_run_prove_outputs_coding_agent_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / ".ai4math" / "lean-workspace"
            workspace.mkdir(parents=True)
            (workspace / "lean-toolchain").write_text("leanprover/lean4:v4.28.0\n", encoding="utf-8")
            (workspace / "lakefile.toml").write_text('name = "lean_workspace"\n', encoding="utf-8")
            target = root / "Failure.lean"
            target.write_text((FIXTURES / "failure.lean").read_text(encoding="utf-8"), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "prove",
                    "--cwd",
                    str(root),
                    "--file",
                    str(target),
                    "--dry-run",
                ],
                text=True,
                capture_output=True,
                check=False,
                env={**os.environ, "AI4MATH_LEAN_WORKSPACE": str(workspace), "AI4MATH_NUMINA_HOME": str(root / "shared-ai4math" / "numina-runtime")},
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "dry_run")
        self.assertEqual(payload["agent_mode"], "coding-agent")
        self.assertEqual(payload["backend"], "none")
        self.assertIn("direct_workflow", payload)
        self.assertNotIn("command", payload)

    def test_check_skip_build_outputs_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "lean-toolchain").write_text("leanprover/lean4:v4.26.0\n", encoding="utf-8")
            (root / "lakefile.toml").write_text('name = "proj"\n', encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLI), "check", "--cwd", str(root), "--skip-build"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["toolchain"], "leanprover/lean4:v4.26.0")

    def test_smoke_test_dry_run_uses_bundled_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = subprocess.run(
                [sys.executable, str(CLI), "smoke-test", "--cwd", str(root), "--dry-run"],
                text=True,
                capture_output=True,
                check=False,
                env={**os.environ, "AI4MATH_HOME": str(root / "shared-ai4math"), "AI4MATH_LEAN_WORKSPACE": ""},
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "dry_run")
        self.assertTrue(payload["smoke_file"].endswith("examples/smoke/NuminaSmoke.lean"))
        self.assertFalse(payload["external_api_call"])

    def test_doctor_outputs_tool_report(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CLI), "doctor", "--cwd", str(SKILL_ROOT)],
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "AI4MATH_HOME": str(SKILL_ROOT / ".test-ai4math-home"), "AI4MATH_NUMINA_HOME": ""},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertIn("tools", payload)
        self.assertIn("readiness", payload)
        self.assertIn("numina", payload)
        self.assertIn("readiness", payload["numina"])

    def test_configure_setup_numina_dry_run_outputs_official_upstream(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "configure",
                    "--cwd",
                    str(root),
                    "--setup-numina",
                    "--project-name",
                    "demo_project",
                    "--dry-run",
                ],
                text=True,
                capture_output=True,
                check=False,
                env={**os.environ, "AI4MATH_HOME": str(root / "shared-ai4math"), "AI4MATH_NUMINA_HOME": ""},
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("numina", payload)
        self.assertEqual(payload["numina"]["status"], "dry_run")
        commands = [action["command"] for action in payload["numina"]["actions"]]
        self.assertIn("https://github.com/project-numina/numina-lean-agent", str(commands))
        self.assertIn(["./setup.sh", "demo_project"], commands)

    def test_lean_workspace_deploy_failure_uses_lean_exit_code(self) -> None:
        self.assertEqual(
            _exit_code({"ok": False, "status": "lean_workspace_setup_failed"}),
            EXIT_LEAN_FAILED,
        )

    def test_verify_delivery_package_checks(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CLI), "verify-delivery", "--cwd", str(SKILL_ROOT)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "delivery_ready")
        self.assertIn("verify-delivery", payload["commands"]["available"])
        self.assertTrue(payload["checks"]["lean_setup_entrypoint"])
        self.assertFalse(payload["lean_setup_entrypoint"]["missing_phrases"])

    def test_root_discovery_does_not_steal_setup_only_tasks(self) -> None:
        boundary = _root_discovery_boundary_check()
        self.assertTrue(boundary["ok"], boundary)
        self.assertFalse(boundary["root_setup_only_trigger_hits"])

    def test_lean_setup_entrypoint_uses_sibling_helper_layout(self) -> None:
        setup = _lean_setup_entrypoint_check()
        self.assertTrue(setup["ok"], setup)
        self.assertTrue(setup["helper_script_exists"], setup)
        self.assertFalse(setup["repo_root_command_hits"], setup)

    def test_two_public_skills_share_hidden_runtime_layer(self) -> None:
        runtime_root = SKILLS_ROOT / "lean-runtime"
        runtime_cli = runtime_root / "scripts" / "ai4m_lean.py"
        setup_text = (SKILLS_ROOT / "lean-setup" / "SKILL.md").read_text(encoding="utf-8")
        formalization_text = (SKILLS_ROOT / "lean-formalization" / "SKILL.md").read_text(encoding="utf-8")

        self.assertTrue(runtime_cli.exists())
        self.assertIn("../lean-runtime/scripts/ai4m_lean.py", setup_text)
        self.assertIn("../lean-runtime/scripts/ai4m_lean.py", formalization_text)
        self.assertNotIn("../lean-formalization/scripts/ai4m_lean.py", setup_text)

    def test_lean_setup_offers_default_names_for_isolated_setup(self) -> None:
        text = (SKILL_ROOT.parent / "lean-setup" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("When creating an isolated test directory or workspace", text)
        self.assertIn("suggest a safe default name", text)
        self.assertIn("use the default if the user has no naming preference", text)

    def test_lean_setup_guides_next_step_after_successful_setup(self) -> None:
        text = (SKILL_ROOT.parent / "lean-setup" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("After successful setup or smoke-test validation", text)
        self.assertIn("Offer a short next-step menu", text)
        self.assertIn("inspect an existing Lean/Lake project", text)
        self.assertIn("repair a Lean file or complete `sorry`", text)
        self.assertIn("formalize a natural-language or LaTeX theorem", text)
        self.assertIn("mention optional Numina only when the user explicitly asks", text)

    def test_optional_backend_language_distinguishes_current_and_future_adapters(self) -> None:
        repo_root = SKILLS_ROOT.parent
        texts = [
            (SKILLS_ROOT / "lean-formalization" / "SKILL.md").read_text(encoding="utf-8"),
            (SKILL_ROOT / "references" / "numina_runtime.md").read_text(encoding="utf-8"),
        ]
        readme_path = repo_root / "README.md"
        readme_zh_path = repo_root / "README.zh-CN.md"
        if readme_path.exists():
            texts.append(readme_path.read_text(encoding="utf-8"))

        for text in texts:
            self.assertIn("optional Lean-specialist backend", text)
            self.assertIn("Currently supported optional backend: official Numina Lean Agent runtime", text)
            self.assertIn("Future backend adapters", text)
            self.assertIn("do not claim support until deployment, readiness checks, invocation, validation, and failure triage are documented", text)
            self.assertNotIn("Currently supported optional backend: Archon", text)

        if readme_zh_path.exists():
            readme_zh = readme_zh_path.read_text(encoding="utf-8")
            self.assertIn("可选 Lean 专用 agent backend", readme_zh)
            self.assertIn("当前支持的可选 backend：official Numina Lean Agent runtime", readme_zh)
            self.assertIn("未来 backend adapter", readme_zh)
            self.assertIn("不要写成已支持", readme_zh)

    def test_package_hygiene_scans_lean_setup_entrypoint(self) -> None:
        generated = SKILL_ROOT.parent / "lean-setup" / "__pycache__" / "sentinel.pyc"
        generated.parent.mkdir(exist_ok=True)
        try:
            generated.write_bytes(b"placeholder")
            hygiene = _package_hygiene()
            self.assertIn("lean-setup/__pycache__/sentinel.pyc", hygiene["generated_files"])
        finally:
            generated.unlink(missing_ok=True)
            try:
                generated.parent.rmdir()
            except OSError:
                pass


if __name__ == "__main__":
    unittest.main()
