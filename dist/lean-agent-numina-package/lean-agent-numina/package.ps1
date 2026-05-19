param(
  [string]$OutputDir = ".\dist"
)

$ErrorActionPreference = "Stop"

function Write-Step {
  param([string]$Message)
  Write-Host "[lean-agent-numina] $Message"
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "..\..\..")

$sourceSkillDir = $scriptDir
$sourceAgentFile = Join-Path $projectRoot ".opencode\agents\numina-lean-agent.md"

$outDir = Resolve-Path "." | ForEach-Object { Join-Path $_ $OutputDir }
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$stageDir = Join-Path $outDir "lean-agent-numina-package"
if (Test-Path $stageDir) {
  Remove-Item -Recurse -Force $stageDir
}
New-Item -ItemType Directory -Force -Path $stageDir | Out-Null

$stageSkillDir = Join-Path $stageDir "lean-agent-numina"
New-Item -ItemType Directory -Force -Path $stageSkillDir | Out-Null
Copy-Item -Path (Join-Path $sourceSkillDir "*") -Destination $stageSkillDir -Recurse -Force

if (Test-Path $sourceAgentFile) {
  $stageAgentDir = Join-Path $stageDir ".opencode\agents"
  New-Item -ItemType Directory -Force -Path $stageAgentDir | Out-Null
  Copy-Item -Path $sourceAgentFile -Destination (Join-Path $stageAgentDir "numina-lean-agent.md") -Force
}

$bundleReadme = @'
# Lean Agent Numina 分发包

## 内容

- `lean-agent-numina/`：Cursor Skill 全部文件
- `.opencode/agents/numina-lean-agent.md`：OpenCode 子 Agent 定义（若包含）

## 安装（Windows）

1. 解压 zip
2. 在解压目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File ".\lean-agent-numina\install.ps1"
```

## 安装（WSL/Linux/macOS）

1. 解压 zip
2. 在解压目录执行：

```bash
bash ./lean-agent-numina/install.sh
```
'@
Set-Content -Path (Join-Path $stageDir "README_INSTALL.md") -Value $bundleReadme -Encoding UTF8

$zipFile = Join-Path $outDir "lean-agent-numina-package.zip"
if (Test-Path $zipFile) {
  Remove-Item -Force $zipFile
}
Compress-Archive -Path (Join-Path $stageDir "*") -DestinationPath $zipFile -Force

Write-Step "Package created: $zipFile"
Write-Step "You can send this zip directly."
