# AI4Math Numina Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 改造现有 `AI4Math-Lean-Agents` skill，使 coding agent 能通过交互式流程部署并调用官方 `project-numina/numina-lean-agent`，同时保留现有 Lean guardrails 和 direct task envelope。

**Architecture:** 新增 `scripts/numina_runtime.py` 作为内部 runtime helper，负责本地路径、credential redaction、上游状态、安装/配置计划和官方 runner command plan。公开 CLI 不新增一组平行的 `numina-*` 命令；`doctor` 展示 Numina readiness，`configure --setup-numina` 负责可审阅的安装/配置，`SKILL.md` 和 `references/numina_runtime.md` 指导 coding agent 何时向用户说明、何时调用上游 Numina、何时使用本地 guardrails。现有 `prove/repair/formalize/complete-sorries/batch` 保持 task envelope/辅助入口，不强制改造成 Numina 流水线。

**Tech Stack:** Python 3 standard library, `unittest`, existing Lean/Lake helper modules, `git`, `uv`, `claude` CLI, official `project-numina/numina-lean-agent`.

---

## File Structure

- Create `skills/AI4Math-Lean-Agents/scripts/numina_runtime.py`: internal deterministic Numina runtime wrapper. It has no external API calls in `doctor`, `dry_run`, or tests.
- Create `skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py`: offline tests for runtime paths, credential redaction, install/configure plans, dirty upstream protection, and runner command construction.
- Create `skills/AI4Math-Lean-Agents/config/numina_runtime.example.toml`: tracked example config.
- Create `skills/AI4Math-Lean-Agents/references/numina_runtime.md`: operator reference for official Numina deployment through existing commands.
- Modify `skills/AI4Math-Lean-Agents/scripts/common.py`: add `numina-runtime/` to `.ai4math/.gitignore`.
- Modify `skills/AI4Math-Lean-Agents/scripts/tool_status.py`: include `curl`, `uv`, and `claude` in tool reporting.
- Modify `skills/AI4Math-Lean-Agents/scripts/configure_lean.py`: add Numina readiness to `inspect_environment`; add `setup_numina`, `project_name`, `skip_numina_sync` handling to `configure`.
- Modify `skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py`: wire `configure --setup-numina`; keep task commands as existing envelopes.
- Modify `skills/AI4Math-Lean-Agents/scripts/verify_delivery.py`: require new runtime files and update policy checks.
- Modify docs: `skills/AI4Math-Lean-Agents/SKILL.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `skills/AI4Math-Lean-Agents/agents/openai.yaml`, `skills/AI4Math-Lean-Agents/references/numina_reverse_analysis.md`.

---

### Task 1: Internal Runtime Paths, Credentials, and Gitignore

**Files:**
- Create: `skills/AI4Math-Lean-Agents/scripts/numina_runtime.py`
- Create: `skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py`
- Modify: `skills/AI4Math-Lean-Agents/scripts/common.py`

- [ ] **Step 1: Write failing tests**

Create `skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py`:

```python
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from common import ensure_ai4math_gitignore  # noqa: E402
from numina_runtime import (  # noqa: E402
    DEFAULT_UPSTREAM_URL,
    credential_report,
    read_numina_env_local,
    runtime_paths,
)


class NuminaRuntimePathTests(unittest.TestCase):
    def test_runtime_paths_default_under_ai4math(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = runtime_paths(Path(tmp))

        root = Path(tmp).resolve() / ".ai4math" / "numina-runtime"
        self.assertEqual(paths["root"], str(root))
        self.assertEqual(paths["upstream"], str(root / "upstream"))
        self.assertEqual(paths["results"], str(root / "results"))
        self.assertEqual(paths["default_upstream_url"], DEFAULT_UPSTREAM_URL)

    def test_runtime_paths_honor_ai4math_numina_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            custom = Path(tmp) / "custom-numina"
            with patch.dict(os.environ, {"AI4MATH_NUMINA_HOME": str(custom)}, clear=False):
                paths = runtime_paths(Path(tmp))

        self.assertEqual(paths["root"], str(custom.resolve()))
        self.assertEqual(paths["upstream"], str(custom.resolve() / "upstream"))

    def test_numina_runtime_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gitignore = ensure_ai4math_gitignore(tmp)

            lines = gitignore.read_text(encoding="utf-8").splitlines()

        self.assertIn("numina-runtime/", lines)


class NuminaRuntimeCredentialTests(unittest.TestCase):
    def test_env_local_is_read_from_numina_runtime_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".ai4math" / "numina-runtime" / ".env.local"
            env_path.parent.mkdir(parents=True)
            env_path.write_text(
                "export ANTHROPIC_AUTH_TOKEN=secret-token\n"
                "OPENAI_API_KEY=sk-test\n",
                encoding="utf-8",
            )

            values = read_numina_env_local(Path(tmp))

        self.assertEqual(values["ANTHROPIC_AUTH_TOKEN"], "secret-token")
        self.assertEqual(values["OPENAI_API_KEY"], "sk-test")

    def test_credential_report_redacts_values(self) -> None:
        report = credential_report({
            "ANTHROPIC_AUTH_TOKEN": "secret-token",
            "OPENAI_API_KEY": "sk-test",
        })

        self.assertTrue(report["claude"]["configured"])
        self.assertEqual(report["claude"]["variables"]["ANTHROPIC_AUTH_TOKEN"], "<redacted>")
        self.assertEqual(report["skill_keys"]["OPENAI_API_KEY"], "<redacted>")
        self.assertNotIn("secret-token", str(report))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Verify tests fail**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py
```

Expected: FAIL with missing `numina_runtime` module or missing imported functions.

- [ ] **Step 3: Implement runtime path and credential helpers**

Create `skills/AI4Math-Lean-Agents/scripts/numina_runtime.py`:

```python
from __future__ import annotations

import os
import shlex
from pathlib import Path
from typing import Any

from common import expand_path


DEFAULT_UPSTREAM_URL = "https://github.com/project-numina/numina-lean-agent"
CLAUDE_ENV_KEYS = ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL"]
SKILL_ENV_KEYS = ["GEMINI_API_KEY", "OPENAI_API_KEY", "LEAN_LEANDEX_API_KEY", "AXLE_API_KEY"]


def runtime_root(cwd: str | Path) -> Path:
    cwd_path = Path(cwd).resolve()
    override = os.environ.get("AI4MATH_NUMINA_HOME")
    if override:
        return expand_path(override, cwd_path) or (cwd_path / ".ai4math" / "numina-runtime")
    return cwd_path / ".ai4math" / "numina-runtime"


def runtime_paths(cwd: str | Path) -> dict[str, str]:
    root = runtime_root(cwd)
    return {
        "root": str(root),
        "upstream": str(root / "upstream"),
        "projects": str(root / "projects"),
        "results": str(root / "results"),
        "env_local": str(root / ".env.local"),
        "local_config": str(root / "numina_runtime.local.toml"),
        "default_upstream_url": DEFAULT_UPSTREAM_URL,
    }


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = shlex.split(line, comments=True, posix=True)
        if parts and parts[0] == "export":
            parts = parts[1:]
        for part in parts:
            if "=" in part:
                key, value = part.split("=", 1)
                values[key] = value
    return values


def read_numina_env_local(cwd: str | Path) -> dict[str, str]:
    return _parse_env_file(runtime_root(cwd) / ".env.local")


def _redact(value: str | None) -> str | None:
    return "<redacted>" if value else None


def credential_report(env: dict[str, str] | None = None) -> dict[str, Any]:
    merged = dict(os.environ)
    if env:
        merged.update(env)
    claude_variables = {key: _redact(merged.get(key)) for key in CLAUDE_ENV_KEYS}
    skill_keys = {key: _redact(merged.get(key)) for key in SKILL_ENV_KEYS}
    return {
        "claude": {
            "configured": bool(merged.get("ANTHROPIC_AUTH_TOKEN")),
            "variables": claude_variables,
        },
        "skill_keys": skill_keys,
        "missing_skill_keys": [key for key in SKILL_ENV_KEYS if not merged.get(key)],
    }
```

Modify the `entries` list in `skills/AI4Math-Lean-Agents/scripts/common.py`:

```python
        "numina-runtime/",
```

- [ ] **Step 4: Verify focused tests pass**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/AI4Math-Lean-Agents/scripts/numina_runtime.py \
  skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py \
  skills/AI4Math-Lean-Agents/scripts/common.py
git commit -m "Add Numina runtime helpers"
```

---

### Task 2: Internal Install, Configure, and Runner Plans

**Files:**
- Modify: `skills/AI4Math-Lean-Agents/scripts/numina_runtime.py`
- Modify: `skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py`
- Modify: `skills/AI4Math-Lean-Agents/scripts/tool_status.py`

- [ ] **Step 1: Add failing tests for internal plans**

Append to `skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py`:

```python
from numina_runtime import (  # noqa: E402
    build_batch_plan,
    build_configure_plan,
    build_install_plan,
    build_run_plan,
    numina_readiness,
)


class NuminaRuntimePlanTests(unittest.TestCase):
    def make_lake_project(self, root: Path) -> Path:
        (root / "lean-toolchain").write_text("leanprover/lean4:v4.28.0\n", encoding="utf-8")
        (root / "lakefile.toml").write_text('name = "proj"\n', encoding="utf-8")
        target = root / "Main.lean"
        target.write_text("example : True := by trivial\n", encoding="utf-8")
        return target

    def make_upstream(self, root: Path) -> Path:
        upstream = root / ".ai4math" / "numina-runtime" / "upstream"
        upstream.mkdir(parents=True)
        (upstream / ".git").mkdir()
        return upstream

    def test_install_dry_run_uses_official_upstream(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_install_plan(Path(tmp), dry_run=True)

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "dry_run")
        self.assertEqual(result["upstream_url"], DEFAULT_UPSTREAM_URL)
        self.assertEqual(result["actions"][0]["command"][:2], ["git", "clone"])

    def test_dirty_upstream_blocks_non_dry_run_update(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            upstream = self.make_upstream(Path(tmp))
            with patch("numina_runtime.run_command") as run:
                run.return_value = {"ok": True, "stdout": " M file.py\n", "stderr": "", "returncode": 0}

                result = build_install_plan(Path(tmp), dry_run=False)

        self.assertEqual(str(upstream), result["upstream"]["path"])
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "upstream_dirty")

    def test_readiness_reports_missing_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = numina_readiness(Path(tmp))

        self.assertTrue(result["ok"])
        self.assertFalse(result["upstream"]["exists"])
        self.assertIn("configure --setup-numina", result["recommended_next_action"])

    def test_configure_plan_includes_install_setup_and_sync(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_upstream(root)

            result = build_configure_plan(root, project_name="myproofs", skip_sync=False, dry_run=True)

        commands = [action["command"] for action in result["actions"]]
        self.assertIn(["git", "fetch", "--all", "--tags"], commands)
        self.assertIn(["./setup.sh", "myproofs"], commands)
        self.assertIn(["uv", "python", "install"], commands)
        self.assertIn(["uv", "sync"], commands)

    def test_run_plan_requires_lake_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "Main.lean"
            target.write_text("example : True := by trivial\n", encoding="utf-8")

            result = build_run_plan(Path(tmp), target, prompt_file=None, prompt="prove it", max_rounds=5, result_dir=None, dry_run=True)

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "missing_lake_project")

    def test_run_plan_builds_official_runner_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_upstream(root)
            target = self.make_lake_project(root)
            prompt = root / "prompt.md"
            prompt.write_text("prove the target\n", encoding="utf-8")

            result = build_run_plan(root, target, prompt_file=prompt, prompt=None, max_rounds=7, result_dir=None, dry_run=True)

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "dry_run")
        self.assertEqual(result["command"][:4], ["python", "-m", "scripts.run_claude", "run"])
        self.assertIn("--max-rounds", result["command"])
        self.assertIn("7", result["command"])

    def test_batch_plan_requires_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_batch_plan(Path(tmp), Path(tmp) / "missing", prompt_file=None, max_rounds=5, result_dir=None, dry_run=True)

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "file_not_found")
```

- [ ] **Step 2: Verify tests fail**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py
```

Expected: FAIL with missing plan functions.

- [ ] **Step 3: Implement internal plan functions**

Append to `skills/AI4Math-Lean-Agents/scripts/numina_runtime.py`:

```python
from check_lean_project import find_project_root
from common import run_command
from tool_status import tool_versions


def upstream_url() -> str:
    return os.environ.get("NUMINA_LEAN_AGENT_REPO") or DEFAULT_UPSTREAM_URL


def upstream_ref() -> str | None:
    return os.environ.get("NUMINA_LEAN_AGENT_REF") or None


def _upstream_path(cwd: str | Path) -> Path:
    return Path(runtime_paths(cwd)["upstream"])


def inspect_upstream(cwd: str | Path) -> dict[str, Any]:
    upstream = _upstream_path(cwd)
    exists = upstream.exists()
    is_git = (upstream / ".git").exists()
    result: dict[str, Any] = {
        "path": str(upstream),
        "exists": exists,
        "is_git": is_git,
        "dirty": False,
        "commit": None,
    }
    if not is_git:
        return result
    status = run_command(["git", "status", "--short"], cwd=upstream, timeout=30)
    result["dirty"] = bool((status.get("stdout") or "").strip())
    rev = run_command(["git", "rev-parse", "HEAD"], cwd=upstream, timeout=30)
    if rev.get("ok"):
        result["commit"] = (rev.get("stdout") or "").strip()
    return result


def build_install_plan(cwd: str | Path, dry_run: bool = False) -> dict[str, Any]:
    upstream = inspect_upstream(cwd)
    if upstream["exists"] and upstream["is_git"] and upstream["dirty"] and not dry_run:
        return {
            "ok": False,
            "status": "upstream_dirty",
            "upstream": upstream,
            "recommended_next_action": "clean, commit, or stash .ai4math/numina-runtime/upstream before updating",
        }
    upstream_path = _upstream_path(cwd)
    actions: list[dict[str, Any]] = []
    if not upstream_path.exists():
        actions.append({"command": ["git", "clone", upstream_url(), str(upstream_path)], "cwd": str(Path(cwd).resolve())})
    else:
        actions.append({"command": ["git", "fetch", "--all", "--tags"], "cwd": str(upstream_path)})
    if upstream_ref():
        actions.append({"command": ["git", "checkout", upstream_ref() or ""], "cwd": str(upstream_path)})
    return {
        "ok": True,
        "status": "dry_run" if dry_run else "install_plan_ready",
        "upstream_url": upstream_url(),
        "upstream_ref": upstream_ref(),
        "upstream": upstream,
        "actions": actions,
    }


def numina_readiness(cwd: str | Path, target: str | Path | None = None) -> dict[str, Any]:
    env_local = read_numina_env_local(cwd)
    upstream = inspect_upstream(cwd)
    missing = []
    if not upstream["exists"]:
        missing.append("numina_runtime")
    return {
        "ok": True,
        "status": "reported",
        "runtime_paths": runtime_paths(cwd),
        "tools": tool_versions(["git", "curl", "uv", "elan", "lean", "lake", "claude", "python3"]),
        "credentials": credential_report(env_local),
        "upstream": upstream,
        "missing": missing,
        "recommended_next_action": "run configure --setup-numina --project-name <name>" if missing else "ready for Numina task commands",
    }


def build_configure_plan(
    cwd: str | Path,
    project_name: str,
    skip_sync: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    install = build_install_plan(cwd, dry_run=dry_run)
    actions = list(install.get("actions", []))
    upstream = _upstream_path(cwd)
    actions.append({"command": ["./setup.sh", project_name], "cwd": str(upstream / "tutorial")})
    if not skip_sync:
        actions.extend([
            {"command": ["uv", "python", "install"], "cwd": str(upstream)},
            {"command": ["uv", "sync"], "cwd": str(upstream)},
        ])
    return {
        "ok": bool(install.get("ok")),
        "status": "dry_run" if dry_run else "configure_plan_ready",
        "project_name": project_name,
        "actions": actions,
    }


def _default_result_dir(cwd: str | Path, task_type: str) -> Path:
    return Path(runtime_paths(cwd)["results"]) / task_type


def _validate_lake_target(path: Path) -> tuple[Path | None, dict[str, Any] | None]:
    root = find_project_root(path)
    if root is None:
        return None, {"ok": False, "status": "missing_lake_project", "target": str(path)}
    return root, None


def build_run_plan(
    cwd: str | Path,
    file: str | Path,
    prompt_file: str | Path | None,
    prompt: str | None,
    max_rounds: int,
    result_dir: str | Path | None,
    dry_run: bool = False,
) -> dict[str, Any]:
    target = Path(file).expanduser().resolve()
    if not target.exists():
        return {"ok": False, "status": "file_not_found", "target": str(target)}
    project_root, error = _validate_lake_target(target)
    if error:
        return error
    upstream = _upstream_path(cwd)
    if not upstream.exists():
        return {"ok": False, "status": "missing_numina_runtime", "recommended_next_action": "run configure --setup-numina --project-name <name>"}
    if prompt_file is None and not prompt:
        return {"ok": False, "status": "missing_prompt"}
    output_dir = Path(result_dir).expanduser().resolve() if result_dir else _default_result_dir(cwd, "run")
    command = ["python", "-m", "scripts.run_claude", "run", str(target)]
    if prompt_file:
        command.extend(["--prompt-file", str(Path(prompt_file).expanduser().resolve())])
    if prompt:
        command.extend(["--prompt", prompt])
    command.extend(["--max-rounds", str(max_rounds), "--result-dir", str(output_dir)])
    return {
        "ok": True,
        "status": "dry_run" if dry_run else "numina_run_ready",
        "command": command,
        "cwd": str(upstream),
        "project_root": str(project_root),
        "result_dir": str(output_dir),
    }


def build_batch_plan(
    cwd: str | Path,
    folder: str | Path,
    prompt_file: str | Path | None,
    max_rounds: int,
    result_dir: str | Path | None,
    dry_run: bool = False,
) -> dict[str, Any]:
    folder_path = Path(folder).expanduser().resolve()
    if not folder_path.exists():
        return {"ok": False, "status": "file_not_found", "target": str(folder_path)}
    project_root, error = _validate_lake_target(folder_path)
    if error:
        return error
    upstream = _upstream_path(cwd)
    if not upstream.exists():
        return {"ok": False, "status": "missing_numina_runtime", "recommended_next_action": "run configure --setup-numina --project-name <name>"}
    output_dir = Path(result_dir).expanduser().resolve() if result_dir else _default_result_dir(cwd, "batch")
    command = ["python", "-m", "scripts.run_claude", "from-folder", str(folder_path), "--max-rounds", str(max_rounds), "--result-dir", str(output_dir)]
    if prompt_file:
        command.extend(["--prompt-file", str(Path(prompt_file).expanduser().resolve())])
    return {
        "ok": True,
        "status": "dry_run" if dry_run else "numina_batch_ready",
        "command": command,
        "cwd": str(upstream),
        "project_root": str(project_root),
        "result_dir": str(output_dir),
    }
```

- [ ] **Step 4: Update tool status defaults**

Modify `DEFAULT_TOOLS` in `skills/AI4Math-Lean-Agents/scripts/tool_status.py`:

```python
DEFAULT_TOOLS = ["git", "python3", "curl", "uv", "elan", "lean", "lake", "claude"]
```

- [ ] **Step 5: Verify focused tests pass**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/AI4Math-Lean-Agents/scripts/numina_runtime.py \
  skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py \
  skills/AI4Math-Lean-Agents/scripts/tool_status.py
git commit -m "Add Numina runtime command plans"
```

---

### Task 3: Configure and Doctor Use Runtime Readiness

**Files:**
- Modify: `skills/AI4Math-Lean-Agents/scripts/configure_lean.py`
- Modify: `skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py`
- Modify: `skills/AI4Math-Lean-Agents/tests/test_configure_lean.py`
- Modify: `skills/AI4Math-Lean-Agents/tests/test_cli.py`

- [ ] **Step 1: Add failing tests**

Append to `skills/AI4Math-Lean-Agents/tests/test_configure_lean.py`:

```python
    def test_inspect_environment_includes_numina_runtime_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = inspect_environment(tmp)

        self.assertIn("numina", result)
        self.assertFalse(result["numina"]["upstream"]["exists"])
        self.assertIn("configure --setup-numina", result["numina"]["recommended_next_action"])
```

Append to `skills/AI4Math-Lean-Agents/tests/test_cli.py`:

```python
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
                    "myproofs",
                    "--dry-run",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("numina_actions", payload)
        commands = [action["command"] for action in payload["numina_actions"][0]["actions"]]
        self.assertIn(["git", "clone", "https://github.com/project-numina/numina-lean-agent", str(Path(tmp).resolve() / ".ai4math" / "numina-runtime" / "upstream")], commands)
```

- [ ] **Step 2: Verify tests fail**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest \
  skills/AI4Math-Lean-Agents/tests/test_configure_lean.py \
  skills/AI4Math-Lean-Agents/tests/test_cli.py
```

Expected: FAIL because `numina` summary and `--setup-numina` parser args are absent.

- [ ] **Step 3: Add Numina readiness to environment inspection**

Modify imports in `skills/AI4Math-Lean-Agents/scripts/configure_lean.py`:

```python
from numina_runtime import build_configure_plan, numina_readiness
```

In `inspect_environment`, before the return:

```python
    numina = numina_readiness(cwd_path, target=target_path)
```

Add to the returned dict:

```python
        "numina": {
            "status": numina.get("status"),
            "runtime_paths": numina.get("runtime_paths"),
            "upstream": numina.get("upstream"),
            "missing": numina.get("missing", []),
            "recommended_next_action": numina.get("recommended_next_action"),
        },
```

- [ ] **Step 4: Add configure setup arguments**

Change `configure()` signature in `configure_lean.py`:

```python
def configure(
    cwd: str | Path = ".",
    config_path: str | Path | None = None,
    target: str | Path | None = None,
    create_workspace: bool = False,
    toolchain: str | None = None,
    save_local: bool = False,
    dry_run: bool = False,
    setup_numina: bool = False,
    project_name: str | None = None,
    skip_numina_sync: bool = False,
) -> dict[str, Any]:
```

Before returning `env`, add:

```python
    numina_actions: list[dict[str, Any]] = []
    if setup_numina:
        if not project_name:
            numina_actions.append({
                "ok": False,
                "status": "missing_project_name",
                "recommended_next_action": "pass --project-name when using --setup-numina",
            })
        else:
            numina_actions.append(build_configure_plan(cwd_path, project_name, skip_sync=skip_numina_sync, dry_run=dry_run))
    env["numina_actions"] = numina_actions
```

In `ai4m_lean.py`, add parser args to `configure_parser`:

```python
    configure_parser.add_argument("--setup-numina", action="store_true")
    configure_parser.add_argument("--project-name", default=None)
    configure_parser.add_argument("--skip-numina-sync", action="store_true")
```

Pass them into `configure()`.

- [ ] **Step 5: Verify focused tests pass**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest \
  skills/AI4Math-Lean-Agents/tests/test_configure_lean.py \
  skills/AI4Math-Lean-Agents/tests/test_cli.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/AI4Math-Lean-Agents/scripts/configure_lean.py \
  skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py \
  skills/AI4Math-Lean-Agents/tests/test_configure_lean.py \
  skills/AI4Math-Lean-Agents/tests/test_cli.py
git commit -m "Add Numina setup through configure"
```

---

### Task 4: Documentation and Delivery Verification

**Files:**
- Create: `skills/AI4Math-Lean-Agents/config/numina_runtime.example.toml`
- Create: `skills/AI4Math-Lean-Agents/references/numina_runtime.md`
- Modify: `skills/AI4Math-Lean-Agents/SKILL.md`
- Modify: `skills/AI4Math-Lean-Agents/agents/openai.yaml`
- Modify: `skills/AI4Math-Lean-Agents/references/numina_reverse_analysis.md`
- Modify: `README.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`
- Modify: `skills/AI4Math-Lean-Agents/scripts/verify_delivery.py`
- Modify: `skills/AI4Math-Lean-Agents/tests/test_cli.py`

- [ ] **Step 1: Add runtime config and reference**

Create `skills/AI4Math-Lean-Agents/config/numina_runtime.example.toml`:

```toml
[numina]
upstream_url = "https://github.com/project-numina/numina-lean-agent"
runtime_root = ".ai4math/numina-runtime"
default_ref = "main"
results_dir = ".ai4math/numina-runtime/results"
sync_dependencies_by_default = true

[credentials]
read_env_local = true
env_local_path = ".ai4math/numina-runtime/.env.local"
```

Create `skills/AI4Math-Lean-Agents/references/numina_runtime.md`:

```markdown
# Numina Runtime Workflow

Use this reference when the user wants official Numina deployment or invocation through AI4Math Lean Agents.

## First-Time Setup

Run:

```bash
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py doctor --cwd .
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs --dry-run
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs
```

## Invocation

After explaining the external API implications and confirming with the user, the coding agent can run an upstream Numina command from the cloned upstream checkout. A typical command shape is:

```bash
python -m scripts.run_claude run path/to/Foo.lean --prompt-file path/to/prompt.md --max-rounds 5 --result-dir .ai4math/numina-runtime/results/run
```

The existing direct local task envelope remains available:

```bash
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py repair --cwd . --file path/to/Foo.lean --dry-run
```

## Safety

The Numina route may call external model APIs through upstream Numina and Claude. Never print secret values. Use `.ai4math/numina-runtime/.env.local` or the shell environment for credentials.
```

- [ ] **Step 2: Update skill and root docs**

Update:

- `skills/AI4Math-Lean-Agents/SKILL.md`: workflow is official Numina runtime assisted and human-in-the-loop; direct local Lean guardrails remain part of diagnosis and final validation.
- `README.md`: show `doctor`, `configure --setup-numina`, an example upstream `scripts.run_claude` command, and existing `repair/prove --dry-run` task-envelope usage.
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`: replace no-Numina policy with official Numina runtime default plus external API warning.
- `skills/AI4Math-Lean-Agents/agents/openai.yaml`: mention official Numina runtime.
- `skills/AI4Math-Lean-Agents/references/numina_reverse_analysis.md`: add a top note that it is historical background and no longer defines a no-call policy.

- [ ] **Step 3: Update delivery verifier**

Modify `REQUIRED_FILES` in `verify_delivery.py`:

```python
    "config/numina_runtime.example.toml",
    "references/numina_runtime.md",
    "scripts/numina_runtime.py",
```

Do not add public `numina-*` commands to `REQUIRED_COMMANDS`. The required command set remains centered on existing `doctor`, `configure`, and task commands.

Replace `_guidance_first_check()` required phrases with:

```python
    required_phrases = [
        "## Agent Playbook",
        "## Helper Toolbox",
        "official Numina runtime",
        "Use official Numina through a human-in-the-loop runtime workflow",
    ]
```

Update `external_api_note`:

```python
        "external_api_note": "The Numina runtime workflow may call upstream Numina, Claude, and external model APIs after user-facing explanation/confirmation. Guardrail commands and default tests remain local/offline.",
```

Update `test_verify_delivery_package_checks` in `test_cli.py`:

```python
        self.assertIn("scripts/numina_runtime.py", [item["path"] for item in payload["files"]])
        self.assertIn("configure", payload["commands"]["available"])
```

- [ ] **Step 4: Run full tests and delivery verification**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s skills/AI4Math-Lean-Agents/tests
```

Expected: all tests pass.

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

Expected: JSON has `"ok": true`, `"status": "delivery_ready"`, and `"unit_tests": {"ok": true, ...}`.

- [ ] **Step 5: Commit**

```bash
git add README.md AGENTS.md CLAUDE.md GEMINI.md \
  skills/AI4Math-Lean-Agents/SKILL.md \
  skills/AI4Math-Lean-Agents/agents/openai.yaml \
  skills/AI4Math-Lean-Agents/config/numina_runtime.example.toml \
  skills/AI4Math-Lean-Agents/references/numina_runtime.md \
  skills/AI4Math-Lean-Agents/references/numina_reverse_analysis.md \
  skills/AI4Math-Lean-Agents/scripts/verify_delivery.py \
  skills/AI4Math-Lean-Agents/tests/test_cli.py
git commit -m "Document official Numina runtime workflow"
```

---

## Final Verification Checklist

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s skills/AI4Math-Lean-Agents/tests
```

Expected: all tests pass.

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

Expected: `"ok": true` and `"status": "delivery_ready"`.

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name dryrun --dry-run
```

Expected: JSON includes `numina_actions` and the official upstream URL.

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py doctor --cwd .
```

Expected: JSON includes a Numina readiness summary and no secret values.

- [ ] Run:

```bash
git status --short
```

Expected: no unstaged or uncommitted implementation changes.

---

## Self-Review Notes

- Spec coverage: The plan covers existing-skill modification, official upstream install/configure through existing CLI, runtime state, human-in-the-loop Numina invocation guidance, docs, tests, delivery verifier, and external API disclosure.
- Completeness scan: The plan uses concrete code snippets, exact commands, expected outputs, and no open-ended steps.
- Type consistency: Runtime status names use the spec vocabulary: `missing_numina_runtime`, `upstream_dirty`, `numina_run_ready`, and `direct_task_ready`.
