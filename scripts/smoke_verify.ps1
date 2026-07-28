#Requires -Version 5.1
<#
.SYNOPSIS
  Smoke regression: lake build + lake env lean on positive targets; broken must fail.
#>
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")
Set-Location $projectRoot

# Prefer project-known elan if present
$elanBin = "d:\Lean\elan\bin"
if (Test-Path (Join-Path $elanBin "lake.exe")) {
  $env:Path = "$elanBin;$env:Path"
}

function Invoke-Ok {
  param([string]$Label, [scriptblock]$Cmd)
  Write-Host "==> $Label"
  & $Cmd
  if ($LASTEXITCODE -ne 0) { throw "FAILED (expected ok): $Label (exit $LASTEXITCODE)" }
  Write-Host "OK: $Label"
}

function Invoke-ExpectFail {
  param([string]$Label, [scriptblock]$Cmd)
  Write-Host "==> $Label (expect fail)"
  & $Cmd
  if ($LASTEXITCODE -eq 0) { throw "FAILED (expected non-zero): $Label" }
  Write-Host "OK (failed as expected): $Label"
}

Invoke-Ok "lake build" { lake build }

$positives = @(
  "StatInferenceLean/Exercises/InteractiveDemo.lean",
  "StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.fixed.lean",
  "StatInferenceLean/Exercises/Bernoulli.lean"
)

foreach ($f in $positives) {
  Invoke-Ok "lake env lean $f" { lake env lean $f }
}

Invoke-ExpectFail "lake env lean broken" {
  lake env lean "StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.broken.lean"
}

Write-Host ""
Write-Host "smoke_verify: all checks passed."
