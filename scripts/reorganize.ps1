# LifeOS Reorganize Script v2 (Flat Structure - NO SRC)
# Keeps backend-cortex and frontend-body at root for direct access

$rootPath = "c:\Users\benga\Desktop\lifeosjxs-main"
Set-Location $rootPath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LifeOS Reorganize Tool v2 (Flat)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Create Core Support Folders
$folders = @("docs\for-ai", "docs\for-users", "docs\archive", "config", "scripts", "tools", "data")
foreach ($f in $folders) {
    if (-not (Test-Path $f)) { New-Item -Path $f -ItemType Directory -Force | Out-Null }
}

# 2. Organize Global Files
Write-Host "[1/3] Organizing global files..." -ForegroundColor Yellow

# SYSTEM_CONTEXT.md
if (Test-Path "SYSTEM_CONTEXT.md") {
    Move-Item -Path "SYSTEM_CONTEXT.md" -Destination "docs\for-ai\" -Force
    Write-Host "  ✅ SYSTEM_CONTEXT.md -> docs/for-ai/" -ForegroundColor Green
}

# .cursorrules
if (Test-Path ".cursorrules") {
    Copy-Item -Path ".cursorrules" -Destination "config\" -Force
    Write-Host "  ✅ .cursorrules copied to config/" -ForegroundColor Green
}

# 3. Organize Scripts & Tools
Write-Host "[2/3] Organizing scripts and tools..." -ForegroundColor Yellow

$scripts = @("cleanup.ps1", "reorganize.ps1")
foreach ($s in $scripts) {
    if (Test-Path $s) {
        Move-Item -Path $s -Destination "scripts\" -Force
        Write-Host "  ✅ $s -> scripts/" -ForegroundColor Green
    }
}

$rootTools = @("record_handover.py", "build_kernel.py", "test_ingest.py", "driver.py")
foreach ($t in $rootTools) {
    if (Test-Path $t) {
        Move-Item -Path $t -Destination "tools\" -Force
        Write-Host "  ✅ $t -> tools/" -ForegroundColor Green
    }
}

# 4. Clean up Legacy/Redundant Files
Write-Host "[3/3] Performance purification..." -ForegroundColor Yellow

$garbage = @("README1.md", "README_ACTION.md", "SYSTEM_HEALTH_REPORT.md", "TEST_REPORT.md", "main.py", "main")
foreach ($g in $garbage) {
    if (Test-Path $g) {
        Remove-Item -Path $g -Force
        Write-Host "  🗑️  Removed $g" -ForegroundColor Gray
    }
}

# Remove empty src if left behind
if (Test-Path "src") {
    Remove-Item -Path "src" -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "REORGANIZE COMPLETE (No-Src Layout)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Current Hierarchy:" -ForegroundColor White
Write-Host " - backend-cortex/  (Core API)" -ForegroundColor Gray
Write-Host " - frontend-body/   (Core UI)" -ForegroundColor Gray
Write-Host " - docs/           (Truth Source)" -ForegroundColor Gray
Write-Host " - config/         (Rules)" -ForegroundColor Gray
Write-Host " - tools/          (Utilities)" -ForegroundColor Gray
Write-Host " - scripts/        (Maint)" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ System Pure & Flat." -ForegroundColor Green
