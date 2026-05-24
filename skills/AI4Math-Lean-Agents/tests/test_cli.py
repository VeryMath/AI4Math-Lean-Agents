from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from ai4m_lean import EXIT_LEAN_FAILED, _exit_code  # noqa: E402

CLI = SKILL_ROOT / "scripts" / "ai4m_lean.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class CliTests(unittest.TestCase):
    def test_dry_run_prove_outputs_direct_task(self) -> None:
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
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "dry_run")
        self.assertEqual(payload["agent_mode"], "direct-coding-agent")
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

    def test_doctor_outputs_tool_report(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CLI), "doctor", "--cwd", str(SKILL_ROOT)],
            text=True,
            capture_output=True,
            check=False,
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
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "configure",
                    "--cwd",
                    tmp,
                    "--setup-numina",
                    "--project-name",
                    "demo_project",
                    "--dry-run",
                ],
                text=True,
                capture_output=True,
                check=False,
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


if __name__ == "__main__":
    unittest.main()
