param(
  [switch]$SkipOpenCode
)

$ErrorActionPreference = "Stop"

function Write-Step {
  param([string]$Message)
  Write-Host "[lean-agent-numina] $Message"
}

$skillSourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $skillSourceDir "..\..\..")
$agentSourceFile = Join-Path $projectRoot ".opencode\agents\numina-lean-agent.md"

$cursorSkillTarget = Join-Path $HOME ".cursor\skills\lean-agent-numina"
$openCodeAgentTargetDir = Join-Path $HOME ".opencode\agents"
$openCodeAgentTargetFile = Join-Path $openCodeAgentTargetDir "numina-lean-agent.md"

Write-Step "Source skill: $skillSourceDir"
Write-Step "Target skill: $cursorSkillTarget"

New-Item -ItemType Directory -Force -Path $cursorSkillTarget | Out-Null
Copy-Item -Path (Join-Path $skillSourceDir "*") -Destination $cursorSkillTarget -Recurse -Force
Write-Step "Copied skill files."

if (-not $SkipOpenCode) {
  if (Test-Path $agentSourceFile) {
    New-Item -ItemType Directory -Force -Path $openCodeAgentTargetDir | Out-Null
    Copy-Item -Path $agentSourceFile -Destination $openCodeAgentTargetFile -Force
    Write-Step "Copied OpenCode agent file."
  } else {
    Write-Step "OpenCode agent file not found in project: $agentSourceFile"
    Write-Step "Skill is installed. OpenCode agent copy skipped."
  }
} else {
  Write-Step "SkipOpenCode enabled. OpenCode agent copy skipped."
}

Write-Step "Install complete."
Write-Host ""
Write-Host "Next:"
Write-Host "1) Restart Cursor (or run: Developer: Reload Window)"
Write-Host "2) Verify skill files in: $cursorSkillTarget"
if (-not $SkipOpenCode) {
  Write-Host "3) Verify OpenCode agent in: $openCodeAgentTargetFile"
}
