$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$terraformDir = Join-Path $repoRoot "terraform"
$tempDir = Join-Path $repoRoot ".terraform-temp"
$cacheDir = Join-Path $repoRoot ".terraform-cache"

New-Item -ItemType Directory -Force -Path $tempDir, $cacheDir | Out-Null

$env:TEMP = $tempDir
$env:TMP = $tempDir
$env:TF_PLUGIN_CACHE_DIR = $cacheDir

Write-Host "TEMP=$env:TEMP"
Write-Host "TMP=$env:TMP"
Write-Host "TF_PLUGIN_CACHE_DIR=$env:TF_PLUGIN_CACHE_DIR"

Push-Location $terraformDir
try {
    terraform init
}
finally {
    Pop-Location
}
