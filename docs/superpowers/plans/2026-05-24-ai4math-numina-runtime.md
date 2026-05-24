# AI4Math Numina Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 改造现有 `AI4Math-Lean-Agents` skill，使其能自动部署并调用官方 `project-numina/numina-lean-agent`，同时保留现有 Lean guardrails 和 direct fallback。

**Architecture:** 新增 `scripts/numina_runtime.py` 作为纯 Python runtime wrapper，负责本地路径、credential redaction、上游状态、dry-run install、setup 和 runner command plan。`scripts/ai4m_lean.py` 继续作为唯一 CLI 总入口，新增 `numina-*` 子命令，并让 `prove/repair/formalize/complete-sorries/batch` 默认走 Numina runtime，`--direct` 保留旧 direct task envelope。文档和 delivery verifier 更新为“官方 Numina runtime assisted workflow”。

**Tech Stack:** Python 3 standard library, `unittest`, existing Lean/Lake helper modules, `git`, `uv`, `claude` CLI, official `project-numina/numina-lean-agent`.

---

## File Structure

- Create `skills/AI4Math-Lean-Agents/scripts/numina_runtime.py`: deterministic Numina runtime wrapper, no external API calls in dry-run/doctor/tests.
- Create `skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py`: offline unit tests for paths, credential redaction, install dry-run, dirty upstream, command construction, and direct fallback routing expectations.
- Create `skills/AI4Math-Lean-Agents/config/numina_runtime.example.toml`: tracked example config for upstream URL/ref and runtime defaults.
- Create `skills/AI4Math-Lean-Agents/references/numina_runtime.md`: operator reference for official Numina deployment and invocation.
- Modify `skills/AI4Math-Lean-Agents/scripts/common.py`: add `numina-runtime/` to `.ai4math/.gitignore`; keep existing `.env.local` behavior.
- Modify `skills/AI4Math-Lean-Agents/scripts/configure_lean.py`: include Numina readiness summary in `inspect_environment`; add `setup_numina`, `project_name`, and `skip_numina_sync` arguments to `configure`.
- Modify `skills/AI4Math-Lean-Agents/scripts/tool_status.py`: include `uv`, `curl`, and `claude` in tool reporting.
- Modify `skills/AI4Math-Lean-Agents/scripts/direct_task.py`: add Numina task-plan builder while preserving direct builder for `--direct`.
- Modify `skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py`: add `numina-*` commands, wire `configure --setup-numina`, add `--direct` to task commands, update exit-code mapping.
- Modify `skills/AI4Math-Lean-Agents/scripts/verify_delivery.py`: require new files and commands; update guidance-first text checks for Numina runtime workflow.
- Modify docs: `skills/AI4Math-Lean-Agents/SKILL.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `skills/AI4Math-Lean-Agents/agents/openai.yaml`, `skills/AI4Math-Lean-Agents/references/numina_reverse_analysis.md`.

---

### Task 1: Runtime Paths, Local Env, and Gitignore

**Files:**
- Create: `skills/AI4Math-Lean-Agents/scripts/numina_runtime.py`
- Create: `skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py`
- Modify: `skills/AI4Math-Lean-Agents/scripts/common.py`

- [ ] **Step 1: Write failing tests for runtime path defaults and gitignore**

Add this to `skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py`:

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

        self.assertEqual(paths["root"], str(Path(tmp).resolve() / ".ai4math" / "numina-runtime"))
        self.assertEqual(paths["upstream"], str(Path(tmp).resolve() / ".ai4math" / "numina-runtime" / "upstream"))
        self.assertEqual(paths["results"], str(Path(tmp).resolve() / ".ai4math" / "numina-runtime" / "results"))
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
        env = {
            "ANTHROPIC_AUTH_TOKEN": "secret-token",
            "OPENAI_API_KEY": "sk-test",
        }

        report = credential_report(env)

        self.assertTrue(report["claude"]["configured"])
        self.assertEqual(report["claude"]["variables"]["ANTHROPIC_AUTH_TOKEN"], "<redacted>")
        self.assertEqual(report["skill_keys"]["OPENAI_API_KEY"], "<redacted>")
        self.assertNotIn("secret-token", str(report))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py
```

Expected: FAIL with `ModuleNotFoundError: No module named 'numina_runtime'` or missing function imports.

- [ ] **Step 3: Implement minimal runtime path and credential helpers**

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

Modify `ensure_ai4math_gitignore` in `skills/AI4Math-Lean-Agents/scripts/common.py` so the `entries` list includes:

```python
        "numina-runtime/",
```

- [ ] **Step 4: Run the focused tests to verify they pass**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py
```

Expected: PASS.

- [ ] **Step 5: Commit Task 1**

```bash
git add skills/AI4Math-Lean-Agents/scripts/numina_runtime.py \
  skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py \
  skills/AI4Math-Lean-Agents/scripts/common.py
git commit -m "Add Numina runtime path helpers"
```

---

### Task 2: Upstream Status, Doctor, and Install Dry-Run

**Files:**
- Modify: `skills/AI4Math-Lean-Agents/scripts/numina_runtime.py`
- Modify: `skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py`
- Modify: `skills/AI4Math-Lean-Agents/scripts/tool_status.py`

- [ ] **Step 1: Add failing tests for upstream status and install planning**

Append to `skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py`:

```python
from numina_runtime import build_install_plan, inspect_upstream, numina_doctor  # noqa: E402


class NuminaRuntimeInstallTests(unittest.TestCase):
    def test_install_dry_run_clones_official_upstream_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_install_plan(Path(tmp), dry_run=True)

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "dry_run")
        self.assertEqual(result["upstream_url"], DEFAULT_UPSTREAM_URL)
        self.assertEqual(result["actions"][0]["command"][:2], ["git", "clone"])
        self.assertIn(DEFAULT_UPSTREAM_URL, result["actions"][0]["command"])

    def test_dirty_upstream_blocks_update(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            upstream = Path(tmp) / ".ai4math" / "numina-runtime" / "upstream"
            upstream.mkdir(parents=True)
            (upstream / ".git").mkdir()
            with patch("numina_runtime.run_command") as run:
                run.return_value = {"ok": True, "stdout": " M file.py\n", "stderr": "", "returncode": 0}

                result = build_install_plan(Path(tmp), dry_run=False)

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "upstream_dirty")

    def test_doctor_reports_missing_upstream_without_installing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = numina_doctor(Path(tmp))

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "reported")
        self.assertFalse(result["numina"]["upstream"]["exists"])
        self.assertIn("numina-install", result["recommended_next_action"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py
```

Expected: FAIL with missing `build_install_plan`, `inspect_upstream`, or `numina_doctor`.

- [ ] **Step 3: Implement upstream inspection and dry-run install planning**

Add these imports to `skills/AI4Math-Lean-Agents/scripts/numina_runtime.py`:

```python
from common import run_command
from tool_status import find_tool, tool_versions
```

Add these functions:

```python
def upstream_url() -> str:
    return os.environ.get("NUMINA_LEAN_AGENT_REPO") or DEFAULT_UPSTREAM_URL


def upstream_ref() -> str | None:
    return os.environ.get("NUMINA_LEAN_AGENT_REF") or None


def inspect_upstream(cwd: str | Path) -> dict[str, Any]:
    upstream = runtime_root(cwd) / "upstream"
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


def _install_commands(cwd: str | Path) -> list[dict[str, Any]]:
    paths = runtime_paths(cwd)
    upstream = paths["upstream"]
    url = upstream_url()
    ref = upstream_ref()
    actions: list[dict[str, Any]] = []
    if not Path(upstream).exists():
        actions.append({"command": ["git", "clone", url, upstream], "cwd": str(Path(cwd).resolve())})
    else:
        actions.append({"command": ["git", "fetch", "--all", "--tags"], "cwd": upstream})
    if ref:
        actions.append({"command": ["git", "checkout", ref], "cwd": upstream})
    return actions


def build_install_plan(cwd: str | Path, dry_run: bool = False) -> dict[str, Any]:
    info = inspect_upstream(cwd)
    if info["exists"] and info["is_git"] and info["dirty"] and not dry_run:
        return {
            "ok": False,
            "status": "upstream_dirty",
            "upstream": info,
            "recommended_next_action": "commit, stash, or clean the upstream checkout before updating",
        }
    actions = _install_commands(cwd)
    if dry_run:
        return {
            "ok": True,
            "status": "dry_run",
            "upstream_url": upstream_url(),
            "upstream_ref": upstream_ref(),
            "actions": actions,
        }
    return {
        "ok": True,
        "status": "install_plan_ready",
        "upstream_url": upstream_url(),
        "upstream_ref": upstream_ref(),
        "actions": actions,
    }


def numina_doctor(cwd: str | Path, target: str | Path | None = None) -> dict[str, Any]:
    env_local = read_numina_env_local(cwd)
    upstream = inspect_upstream(cwd)
    missing = []
    if not upstream["exists"]:
        missing.append("numina_runtime")
    return {
        "ok": True,
        "status": "reported",
        "cwd": str(Path(cwd).resolve()),
        "tools": tool_versions(["git", "curl", "uv", "elan", "lean", "lake", "claude", "python3"]),
        "credentials": credential_report(env_local),
        "numina": {
            "runtime_paths": runtime_paths(cwd),
            "upstream": upstream,
        },
        "missing": missing,
        "recommended_next_action": "run numina-install --dry-run, then numina-install" if missing else "ready for numina-configure or numina-run",
    }
```

- [ ] **Step 4: Update tool status defaults**

Modify `DEFAULT_TOOLS` in `skills/AI4Math-Lean-Agents/scripts/tool_status.py`:

```python
DEFAULT_TOOLS = ["git", "python3", "curl", "uv", "elan", "lean", "lake", "claude"]
```

- [ ] **Step 5: Run focused tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py
```

Expected: PASS.

- [ ] **Step 6: Commit Task 2**

```bash
git add skills/AI4Math-Lean-Agents/scripts/numina_runtime.py \
  skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py \
  skills/AI4Math-Lean-Agents/scripts/tool_status.py
git commit -m "Add Numina runtime doctor and install plan"
```

---

### Task 3: Numina Configure and Runner Command Plans

**Files:**
- Modify: `skills/AI4Math-Lean-Agents/scripts/numina_runtime.py`
- Modify: `skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py`

- [ ] **Step 1: Add failing tests for configure/run/from-folder/batch plans**

Append to `skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py`:

```python
from numina_runtime import (  # noqa: E402
    build_batch_plan,
    build_configure_plan,
    build_from_folder_plan,
    build_run_plan,
)


class NuminaRuntimeCommandPlanTests(unittest.TestCase):
    def make_lake_project(self, root: Path) -> Path:
        (root / "lean-toolchain").write_text("leanprover/lean4:v4.28.0\n", encoding="utf-8")
        (root / "lakefile.toml").write_text('name = "proj"\n', encoding="utf-8")
        source = root / "Main.lean"
        source.write_text("example : True := by trivial\n", encoding="utf-8")
        return source

    def make_upstream(self, root: Path) -> Path:
        upstream = root / ".ai4math" / "numina-runtime" / "upstream"
        upstream.mkdir(parents=True)
        (upstream / ".git").mkdir()
        return upstream

    def test_configure_plan_runs_setup_and_uv_sync(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_upstream(root)

            result = build_configure_plan(root, project_name="myproofs", skip_sync=False, dry_run=True)

        self.assertTrue(result["ok"])
        commands = [action["command"] for action in result["actions"]]
        self.assertIn(["./setup.sh", "myproofs"], commands)
        self.assertIn(["uv", "python", "install"], commands)
        self.assertIn(["uv", "sync"], commands)

    def test_run_plan_requires_lake_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "Main.lean"
            target.write_text("example : True := by trivial\n", encoding="utf-8")

            result = build_run_plan(root, target, prompt_file=None, prompt="prove it", max_rounds=5, result_dir=None, dry_run=True)

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "missing_lake_project")

    def test_run_plan_builds_upstream_runner_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_upstream(root)
            target = self.make_lake_project(root)
            prompt = root / "prompt.md"
            prompt.write_text("prove the target\n", encoding="utf-8")

            result = build_run_plan(root, target, prompt_file=prompt, prompt=None, max_rounds=7, result_dir=None, dry_run=True)

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "dry_run")
        command = result["command"]
        self.assertEqual(command[:4], ["python", "-m", "scripts.run_claude", "run"])
        self.assertIn("--max-rounds", command)
        self.assertIn("7", command)

    def test_from_folder_plan_builds_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_upstream(root)
            self.make_lake_project(root)

            result = build_from_folder_plan(root, root, prompt_file=None, max_rounds=3, result_dir=None, dry_run=True)

        self.assertTrue(result["ok"])
        self.assertEqual(result["command"][:4], ["python", "-m", "scripts.run_claude", "from-folder"])

    def test_batch_plan_requires_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_batch_plan(Path(tmp), Path(tmp) / "missing.yaml", dry_run=True)

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "file_not_found")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py
```

Expected: FAIL with missing plan functions.

- [ ] **Step 3: Implement configure and runner plan functions**

Add to `skills/AI4Math-Lean-Agents/scripts/numina_runtime.py`:

```python
from check_lean_project import find_project_root


def _upstream_path(cwd: str | Path) -> Path:
    return Path(runtime_paths(cwd)["upstream"])


def _default_result_dir(cwd: str | Path, task_type: str) -> Path:
    root = Path(runtime_paths(cwd)["results"])
    return root / task_type


def build_configure_plan(
    cwd: str | Path,
    project_name: str,
    skip_sync: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    upstream = _upstream_path(cwd)
    if not upstream.exists():
        return {
            "ok": False,
            "status": "missing_numina_runtime",
            "recommended_next_action": "run numina-install first",
        }
    actions = [
        {"command": ["./setup.sh", project_name], "cwd": str(upstream / "tutorial")},
    ]
    if not skip_sync:
        actions.extend([
            {"command": ["uv", "python", "install"], "cwd": str(upstream)},
            {"command": ["uv", "sync"], "cwd": str(upstream)},
        ])
    return {
        "ok": True,
        "status": "dry_run" if dry_run else "configure_plan_ready",
        "project_name": project_name,
        "actions": actions,
    }


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
        return {"ok": False, "status": "missing_numina_runtime", "recommended_next_action": "run numina-install"}
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


def build_from_folder_plan(
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
        return {"ok": False, "status": "missing_numina_runtime", "recommended_next_action": "run numina-install"}
    output_dir = Path(result_dir).expanduser().resolve() if result_dir else _default_result_dir(cwd, "from-folder")
    command = ["python", "-m", "scripts.run_claude", "from-folder", str(folder_path)]
    if prompt_file:
        command.extend(["--prompt-file", str(Path(prompt_file).expanduser().resolve())])
    command.extend(["--max-rounds", str(max_rounds), "--result-dir", str(output_dir)])
    return {
        "ok": True,
        "status": "dry_run" if dry_run else "numina_from_folder_ready",
        "command": command,
        "cwd": str(upstream),
        "project_root": str(project_root),
        "result_dir": str(output_dir),
    }


def build_batch_plan(cwd: str | Path, config: str | Path, dry_run: bool = False) -> dict[str, Any]:
    config_path = Path(config).expanduser().resolve()
    if not config_path.exists():
        return {"ok": False, "status": "file_not_found", "config": str(config_path)}
    upstream = _upstream_path(cwd)
    if not upstream.exists():
        return {"ok": False, "status": "missing_numina_runtime", "recommended_next_action": "run numina-install"}
    command = ["python", "-m", "scripts.run_claude", "batch", str(config_path)]
    return {
        "ok": True,
        "status": "dry_run" if dry_run else "numina_batch_ready",
        "command": command,
        "cwd": str(upstream),
    }
```

- [ ] **Step 4: Run focused tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py
```

Expected: PASS.

- [ ] **Step 5: Commit Task 3**

```bash
git add skills/AI4Math-Lean-Agents/scripts/numina_runtime.py \
  skills/AI4Math-Lean-Agents/tests/test_numina_runtime.py
git commit -m "Add Numina runtime command planning"
```

---

### Task 4: Wire Numina Commands into `ai4m_lean.py`

**Files:**
- Modify: `skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py`
- Modify: `skills/AI4Math-Lean-Agents/tests/test_cli.py`

- [ ] **Step 1: Add failing CLI tests for new parser commands**

Append to `skills/AI4Math-Lean-Agents/tests/test_cli.py`:

```python
    def test_numina_install_dry_run_outputs_official_upstream(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(CLI), "numina-install", "--cwd", tmp, "--dry-run"],
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "dry_run")
        self.assertEqual(payload["upstream_url"], "https://github.com/project-numina/numina-lean-agent")

    def test_numina_doctor_reports_missing_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(CLI), "numina-doctor", "--cwd", tmp],
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "reported")
        self.assertIn("numina_runtime", payload["missing"])
```

- [ ] **Step 2: Run CLI tests to verify they fail**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest skills/AI4Math-Lean-Agents/tests/test_cli.py
```

Expected: FAIL because `numina-install` and `numina-doctor` are invalid subcommands.

- [ ] **Step 3: Add imports and parser entries**

Modify imports in `skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py`:

```python
from numina_runtime import (
    build_batch_plan,
    build_configure_plan,
    build_from_folder_plan,
    build_install_plan,
    build_run_plan,
    numina_doctor,
)
```

Add a helper near `add_common`:

```python
def add_numina_common(parser: argparse.ArgumentParser) -> None:
    add_common(parser)
    parser.add_argument("--dry-run", action="store_true")
```

Add parser definitions in `build_parser()`:

```python
    numina_doctor_parser = sub.add_parser("numina-doctor", help="Report official Numina runtime readiness")
    add_common(numina_doctor_parser)
    numina_doctor_parser.add_argument("--target", default=None)

    numina_install = sub.add_parser("numina-install", help="Clone or update official Numina Lean Agent")
    add_numina_common(numina_install)

    numina_configure = sub.add_parser("numina-configure", help="Run upstream Numina tutorial setup")
    add_numina_common(numina_configure)
    numina_configure.add_argument("--project-name", required=True)
    numina_configure.add_argument("--skip-sync", action="store_true")

    numina_run = sub.add_parser("numina-run", help="Run official Numina on one Lean file")
    add_numina_common(numina_run)
    numina_run.add_argument("--file", required=True)
    numina_run.add_argument("--prompt-file", default=None)
    numina_run.add_argument("--prompt", default=None)
    numina_run.add_argument("--max-rounds", type=int, default=5)
    numina_run.add_argument("--result-dir", default=None)

    numina_folder = sub.add_parser("numina-from-folder", help="Run official Numina on a folder")
    add_numina_common(numina_folder)
    numina_folder.add_argument("--folder", required=True)
    numina_folder.add_argument("--prompt-file", default=None)
    numina_folder.add_argument("--max-rounds", type=int, default=5)
    numina_folder.add_argument("--result-dir", default=None)

    numina_batch = sub.add_parser("numina-batch", help="Run official Numina batch config")
    add_numina_common(numina_batch)
    numina_batch.add_argument("--config-file", "--config", dest="batch_config", required=True)
```

- [ ] **Step 4: Add command dispatch**

In `main()`, before existing task dispatch, add:

```python
    if args.command == "numina-doctor":
        result = numina_doctor(args.cwd, target=args.target)
        _finish(result, args.json_output)

    if args.command == "numina-install":
        result = build_install_plan(args.cwd, dry_run=args.dry_run)
        _finish(result, args.json_output)

    if args.command == "numina-configure":
        result = build_configure_plan(
            args.cwd,
            project_name=args.project_name,
            skip_sync=args.skip_sync,
            dry_run=args.dry_run,
        )
        _finish(result, args.json_output)

    if args.command == "numina-run":
        result = build_run_plan(
            args.cwd,
            args.file,
            prompt_file=args.prompt_file,
            prompt=args.prompt,
            max_rounds=args.max_rounds,
            result_dir=args.result_dir,
            dry_run=args.dry_run,
        )
        _finish(result, args.json_output)

    if args.command == "numina-from-folder":
        result = build_from_folder_plan(
            args.cwd,
            args.folder,
            prompt_file=args.prompt_file,
            max_rounds=args.max_rounds,
            result_dir=args.result_dir,
            dry_run=args.dry_run,
        )
        _finish(result, args.json_output)

    if args.command == "numina-batch":
        result = build_batch_plan(args.cwd, args.batch_config, dry_run=args.dry_run)
        _finish(result, args.json_output)
```

- [ ] **Step 5: Run CLI tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest skills/AI4Math-Lean-Agents/tests/test_cli.py
```

Expected: PASS.

- [ ] **Step 6: Commit Task 4**

```bash
git add skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py \
  skills/AI4Math-Lean-Agents/tests/test_cli.py
git commit -m "Wire Numina runtime CLI commands"
```

---

### Task 5: Default Task Commands Use Numina, `--direct` Preserves Old Behavior

**Files:**
- Modify: `skills/AI4Math-Lean-Agents/scripts/direct_task.py`
- Modify: `skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py`
- Modify: `skills/AI4Math-Lean-Agents/tests/test_direct_task.py`
- Modify: `skills/AI4Math-Lean-Agents/tests/test_cli.py`

- [ ] **Step 1: Add failing tests for Numina default and direct fallback**

Append to `skills/AI4Math-Lean-Agents/tests/test_direct_task.py`:

```python
from direct_task import build_numina_task  # noqa: E402


class NuminaTaskRoutingTests(unittest.TestCase):
    def test_numina_task_dry_run_reports_missing_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "lean-toolchain").write_text("leanprover/lean4:v4.28.0\n", encoding="utf-8")
            (root / "lakefile.toml").write_text('name = "proj"\n', encoding="utf-8")
            target = root / "Main.lean"
            target.write_text("example : True := by trivial\n", encoding="utf-8")

            result = build_numina_task("repair", root, target, max_rounds=5, prompt_file=None, result_dir=None, dry_run=True)

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "missing_numina_runtime")
        self.assertEqual(result["backend"], "official-numina")
```

Append to `skills/AI4Math-Lean-Agents/tests/test_cli.py`:

```python
    def test_repair_direct_preserves_old_task_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "lean-toolchain").write_text("leanprover/lean4:v4.28.0\n", encoding="utf-8")
            (root / "lakefile.toml").write_text('name = "proj"\n', encoding="utf-8")
            target = root / "Main.lean"
            target.write_text("example : True := by trivial\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLI), "repair", "--cwd", str(root), "--file", str(target), "--dry-run", "--direct"],
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["agent_mode"], "direct-coding-agent")
        self.assertEqual(payload["backend"], "none")

    def test_repair_default_routes_to_numina(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "lean-toolchain").write_text("leanprover/lean4:v4.28.0\n", encoding="utf-8")
            (root / "lakefile.toml").write_text('name = "proj"\n', encoding="utf-8")
            target = root / "Main.lean"
            target.write_text("example : True := by trivial\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLI), "repair", "--cwd", str(root), "--file", str(target), "--dry-run"],
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 4, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["backend"], "official-numina")
        self.assertEqual(payload["status"], "missing_numina_runtime")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest \
  skills/AI4Math-Lean-Agents/tests/test_direct_task.py \
  skills/AI4Math-Lean-Agents/tests/test_cli.py
```

Expected: FAIL with missing `build_numina_task` and unknown `--direct`.

- [ ] **Step 3: Implement Numina task builder**

Modify `skills/AI4Math-Lean-Agents/scripts/direct_task.py`:

```python
from numina_runtime import build_batch_plan, build_run_plan
```

Add:

```python
def build_numina_task(
    task_type: str,
    cwd: str | Path,
    target: str | Path,
    max_rounds: int = 5,
    prompt_file: str | Path | None = None,
    result_dir: str | Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    if task_type == "batch":
        result = build_batch_plan(cwd, target, dry_run=dry_run)
    else:
        result = build_run_plan(
            cwd,
            target,
            prompt_file=prompt_file,
            prompt=None,
            max_rounds=max_rounds,
            result_dir=result_dir,
            dry_run=dry_run,
        )
    result.setdefault("task_type", task_type)
    result["agent_mode"] = "numina-runtime"
    result["backend"] = "official-numina"
    return result
```

- [ ] **Step 4: Wire `--direct` in CLI task commands**

In `skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py`, import:

```python
from direct_task import run_direct_task, build_numina_task
```

Add `--direct` to proof and batch parsers:

```python
        proof.add_argument("--direct", action="store_true", help="Use direct local Lean task envelope instead of official Numina")
```

For `batch`:

```python
    batch.add_argument("--direct", action="store_true", help="Use direct local Lean batch envelope instead of official Numina")
```

Change task dispatch:

```python
    if args.command in {"prove", "formalize", "repair", "complete-sorries"}:
        if args.direct:
            result = run_direct_task(...)
        else:
            result = build_numina_task(
                args.command,
                cwd=args.cwd,
                target=args.file,
                max_rounds=args.max_rounds,
                prompt_file=args.prompt_file,
                result_dir=args.result_dir,
                dry_run=args.dry_run,
            )
        ...
```

For `batch`, route to `build_numina_task("batch", ...)` unless `args.direct` is set.

- [ ] **Step 5: Update exit-code mapping for missing Numina runtime**

Modify `_exit_code` in `skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py`:

```python
    if status in {"missing_config", "direct_task_missing_config", "missing_numina_runtime", "missing_numina_credentials"}:
        return EXIT_MISSING_CONFIG
```

- [ ] **Step 6: Run focused tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest \
  skills/AI4Math-Lean-Agents/tests/test_direct_task.py \
  skills/AI4Math-Lean-Agents/tests/test_cli.py
```

Expected: PASS.

- [ ] **Step 7: Commit Task 5**

```bash
git add skills/AI4Math-Lean-Agents/scripts/direct_task.py \
  skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py \
  skills/AI4Math-Lean-Agents/tests/test_direct_task.py \
  skills/AI4Math-Lean-Agents/tests/test_cli.py
git commit -m "Route task commands through Numina runtime"
```

---

### Task 6: Configure Integration and Environment Readiness

**Files:**
- Modify: `skills/AI4Math-Lean-Agents/scripts/configure_lean.py`
- Modify: `skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py`
- Modify: `skills/AI4Math-Lean-Agents/tests/test_configure_lean.py`

- [ ] **Step 1: Add failing tests for Numina readiness in environment inspection**

Append to `skills/AI4Math-Lean-Agents/tests/test_configure_lean.py`:

```python
    def test_inspect_environment_includes_numina_runtime_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = inspect_environment(tmp)

        self.assertIn("numina", result)
        self.assertFalse(result["numina"]["upstream"]["exists"])
        self.assertIn("numina-install", result["numina"]["recommended_next_action"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest skills/AI4Math-Lean-Agents/tests/test_configure_lean.py
```

Expected: FAIL because `numina` key is absent.

- [ ] **Step 3: Add Numina summary to `inspect_environment`**

Modify `skills/AI4Math-Lean-Agents/scripts/configure_lean.py` imports:

```python
from numina_runtime import numina_doctor, build_configure_plan, build_install_plan
```

In `inspect_environment`, before return:

```python
    numina = numina_doctor(cwd_path, target=target_path)
```

Add to returned dict:

```python
        "numina": {
            "status": numina.get("status"),
            "upstream": numina.get("numina", {}).get("upstream"),
            "runtime_paths": numina.get("numina", {}).get("runtime_paths"),
            "missing": numina.get("missing", []),
            "recommended_next_action": numina.get("recommended_next_action"),
        },
```

- [ ] **Step 4: Add configure `--setup-numina` support**

Change `configure()` signature:

```python
def configure(..., setup_numina: bool = False, project_name: str | None = None, skip_numina_sync: bool = False) -> dict[str, Any]:
```

Inside `configure`, after workspace handling:

```python
    numina_actions: list[dict[str, Any]] = []
    if setup_numina:
        install = build_install_plan(cwd_path, dry_run=dry_run)
        numina_actions.append(install)
        if install.get("ok") and project_name:
            numina_actions.append(build_configure_plan(cwd_path, project_name, skip_sync=skip_numina_sync, dry_run=dry_run))
```

Before return:

```python
    env["numina_actions"] = numina_actions
```

In `ai4m_lean.py`, add parser args to `configure`:

```python
    configure_parser.add_argument("--setup-numina", action="store_true")
    configure_parser.add_argument("--project-name", default=None)
    configure_parser.add_argument("--skip-numina-sync", action="store_true")
```

Pass them to `configure()`.

- [ ] **Step 5: Run configure tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest skills/AI4Math-Lean-Agents/tests/test_configure_lean.py
```

Expected: PASS.

- [ ] **Step 6: Commit Task 6**

```bash
git add skills/AI4Math-Lean-Agents/scripts/configure_lean.py \
  skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py \
  skills/AI4Math-Lean-Agents/tests/test_configure_lean.py
git commit -m "Add Numina runtime configure integration"
```

---

### Task 7: Config, Reference, and Skill Documentation

**Files:**
- Create: `skills/AI4Math-Lean-Agents/config/numina_runtime.example.toml`
- Create: `skills/AI4Math-Lean-Agents/references/numina_runtime.md`
- Modify: `skills/AI4Math-Lean-Agents/SKILL.md`
- Modify: `skills/AI4Math-Lean-Agents/agents/openai.yaml`
- Modify: `skills/AI4Math-Lean-Agents/references/numina_reverse_analysis.md`
- Modify: `README.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`

- [ ] **Step 1: Add runtime example config**

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

- [ ] **Step 2: Add runtime reference**

Create `skills/AI4Math-Lean-Agents/references/numina_runtime.md`:

```markdown
# Numina Runtime Workflow

Use this reference when the user wants official Numina deployment or invocation.

## First-Time Setup

Run:

```bash
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py numina-doctor --cwd .
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py numina-install --cwd . --dry-run
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py numina-install --cwd .
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py numina-configure --cwd . --project-name myproofs
```

## Invocation

Run one file:

```bash
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py numina-run --cwd . --file path/to/Foo.lean --prompt-file path/to/prompt.md
```

Run a task command through the default Numina route:

```bash
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py repair --cwd . --file path/to/Foo.lean --prompt-file path/to/prompt.md
```

Use the old direct local task envelope only when explicitly requested:

```bash
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py repair --cwd . --file path/to/Foo.lean --direct --dry-run
```

## Safety

The Numina route may call external model APIs through upstream Numina and Claude. Never print secret values. Use `.ai4math/numina-runtime/.env.local` or the shell environment for credentials.
```

- [ ] **Step 3: Rewrite `SKILL.md` runtime sections**

Modify `skills/AI4Math-Lean-Agents/SKILL.md` so the opening says:

```markdown
AI4Math Lean Agents uses an official Numina runtime assisted workflow by default. The skill can fetch `project-numina/numina-lean-agent`, configure local dependencies, call upstream Numina runners, and then use local Lean/Lake guardrails for validation, patch review, `sorry` detection, and minimal failure handoff.
```

Replace the old “Numina is not deployed or called” rule with:

```markdown
Official Numina may be deployed and called when the user requests proof repair, theorem proving, formalization, `sorry` completion, or batch Lean work. Direct local Lean editing remains available as a fallback via `--direct` and for validation/review tasks.
```

Add `references/numina_runtime.md` to the References list.

- [ ] **Step 4: Update root-facing docs**

Update these files consistently:

- `README.md`: describe default Numina runtime, new `numina-*` commands, external API caveat.
- `AGENTS.md`: instruct agents to use `AI4Math-Lean-Agents/SKILL.md`, deploy/call official Numina by default, and keep direct guardrails.
- `CLAUDE.md`: same as AGENTS, with Claude CLI credential note.
- `GEMINI.md`: same policy wording for Gemini.
- `skills/AI4Math-Lean-Agents/agents/openai.yaml`: update `short_description` and `default_prompt` to mention official Numina runtime.
- `skills/AI4Math-Lean-Agents/references/numina_reverse_analysis.md`: add a top note saying it is historical background and no longer defines the no-call policy.

- [ ] **Step 5: Commit Task 7**

```bash
git add README.md AGENTS.md CLAUDE.md GEMINI.md \
  skills/AI4Math-Lean-Agents/SKILL.md \
  skills/AI4Math-Lean-Agents/agents/openai.yaml \
  skills/AI4Math-Lean-Agents/config/numina_runtime.example.toml \
  skills/AI4Math-Lean-Agents/references/numina_runtime.md \
  skills/AI4Math-Lean-Agents/references/numina_reverse_analysis.md
git commit -m "Update skill docs for official Numina runtime"
```

---

### Task 8: Delivery Verification and Full Test Pass

**Files:**
- Modify: `skills/AI4Math-Lean-Agents/scripts/verify_delivery.py`
- Modify: `skills/AI4Math-Lean-Agents/tests/test_cli.py`

- [ ] **Step 1: Update required delivery files and commands**

Modify `REQUIRED_FILES` in `skills/AI4Math-Lean-Agents/scripts/verify_delivery.py` to include:

```python
    "config/numina_runtime.example.toml",
    "references/numina_runtime.md",
    "scripts/numina_runtime.py",
```

Modify `REQUIRED_COMMANDS` to include:

```python
    "numina-doctor",
    "numina-install",
    "numina-configure",
    "numina-run",
    "numina-from-folder",
    "numina-batch",
```

- [ ] **Step 2: Update guidance check**

Replace `_guidance_first_check()` required phrases with phrases matching the new policy:

```python
    required_phrases = [
        "## Agent Playbook",
        "## Helper Toolbox",
        "official Numina runtime",
        "Direct local Lean editing remains available as a fallback via `--direct`",
    ]
```

Update `external_api_note` in `verify()`:

```python
        "external_api_note": "The default Numina runtime workflow may call upstream Numina, Claude, and external model APIs. Guardrail commands and default tests remain local/offline.",
```

- [ ] **Step 3: Add CLI delivery expectation**

In `skills/AI4Math-Lean-Agents/tests/test_cli.py`, update `test_verify_delivery_package_checks`:

```python
        self.assertIn("numina-install", payload["commands"]["available"])
        self.assertIn("scripts/numina_runtime.py", [item["path"] for item in payload["files"]])
```

- [ ] **Step 4: Run package tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s skills/AI4Math-Lean-Agents/tests
```

Expected: all tests pass.

- [ ] **Step 5: Run delivery verification**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

Expected: JSON has `"ok": true`, `"status": "delivery_ready"`, and `"unit_tests": {"ok": true, ...}`.

- [ ] **Step 6: Commit Task 8**

```bash
git add skills/AI4Math-Lean-Agents/scripts/verify_delivery.py \
  skills/AI4Math-Lean-Agents/tests/test_cli.py
git commit -m "Verify Numina runtime delivery"
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
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py numina-install --cwd . --dry-run
```

Expected: JSON includes `"status": "dry_run"` and `"upstream_url": "https://github.com/project-numina/numina-lean-agent"`.

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py numina-doctor --cwd .
```

Expected: JSON includes `numina.runtime_paths`, `credentials`, and no secret values.

- [ ] Run:

```bash
git status --short
```

Expected: no unstaged or uncommitted implementation changes.

---

## Self-Review Notes

- Spec coverage: The plan covers existing-skill modification, official upstream install/dry-run, runtime state, CLI commands, task routing, `--direct`, docs, tests, delivery verifier, and external API disclosure.
- Completeness scan: The plan uses concrete code snippets, exact commands, expected outputs, and no open-ended steps.
- Type consistency: Runtime status names use the spec vocabulary: `missing_numina_runtime`, `upstream_dirty`, `numina_run_ready`, and `direct_task_ready`.
