#Requires -Version 5.1
<#
.SYNOPSIS
  Phase 5 daily ops: Skill↔OpenCode sync check, then smoke_verify.
  Does NOT call the LLM. Live short-run is opt-in (see docs/OPS.md).
#>
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")
Set-Location $projectRoot

Write-Host "==> Skill <-> OpenCode sync check"
& (Join-Path $scriptDir "sync_opencode_agent.ps1") -CheckOnly
if ($LASTEXITCODE -ne 0) { throw "sync check failed; run scripts/sync_opencode_agent.ps1" }

Write-Host ""
Write-Host "==> smoke_verify (PATH prefers d:\Lean\elan\bin)"
& (Join-Path $scriptDir "smoke_verify.ps1")
if ($LASTEXITCODE -ne 0) { throw "smoke_verify failed" }

Write-Host ""
Write-Host "ops_daily: sync check + smoke passed."
Write-Host "Live API short-run is NOT included. Abort unless docs/OPS.md gate is green AND the user approved."
