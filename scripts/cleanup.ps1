# LifeOS Cleanup Execution Script (ASCII Version)
# Automatically cleans up unnecessary files and directories

$rootPath = "c:\Users\benga\Desktop\lifeosjxs-main"
Set-Location $rootPath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LifeOS Directory Cleanup Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# Step 1: Delete Build Artifacts and Caches
# ============================================================================

Write-Host "[1/5] Deleting build artifacts and caches..." -ForegroundColor Yellow

# Delete .next
if (Test-Path "frontend-body\.next") {
    Write-Host "  - Deleting frontend-body\.next/..." -ForegroundColor Gray
    Remove-Item -Path "frontend-body\.next" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Deleted .next/" -ForegroundColor Green
}

# Delete Python cache
Write-Host "  - Deleting Python cache..." -ForegroundColor Gray
Get-ChildItem -Path "backend-cortex" -Recurse -Include "__pycache__","*.pyc","*.pyo" -ErrorAction SilentlyContinue | 
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  [OK] Deleted Python cache" -ForegroundColor Green

# Delete Python venv (if exists and large)
if (Test-Path "backend-cortex\venv") {
    Write-Host "  - Deleting backend-cortex\venv/..." -ForegroundColor Gray
    Remove-Item -Path "backend-cortex\venv" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Deleted venv/" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# Step 2: Create docs directory
# ============================================================================

Write-Host "[2/5] Creating docs directory structure..." -ForegroundColor Yellow

if (-not (Test-Path "docs")) {
    New-Item -Path "docs" -ItemType Directory | Out-Null
    Write-Host "  [OK] Created docs/" -ForegroundColor Green
}

if (-not (Test-Path "docs\archive")) {
    New-Item -Path "docs\archive" -ItemType Directory | Out-Null
    Write-Host "  [OK] Created docs/archive/" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# Step 3: Move core docs
# ============================================================================

Write-Host "[3/5] Moving core docs to docs/..." -ForegroundColor Yellow

$coreDocs = @(
    "AI_DEV_GUIDE.md",
    "USER_MANUAL.md",
    "C_KERNEL_GUIDE.md",
    "SYSTEM_CONTEXT.md",
    "QUESTION_DRIVEN_ARCHITECTURE.md",
    "README_DOCS.md",
    "CLEANUP_PLAN.md"
)

foreach ($doc in $coreDocs) {
    if (Test-Path $doc) {
        Move-Item -Path $doc -Destination "docs\" -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] Moved $doc" -ForegroundColor Green
    }
}

Write-Host ""

# ============================================================================
# Step 4: Move historical docs to archive
# ============================================================================

Write-Host "[4/5] Moving historical docs to docs/archive/..." -ForegroundColor Yellow

$archiveDocs = @(
    "AI_FLOATING_ASSISTANT_UPDATE.md",
    "ANALYSIS_DISPLAY_FIX.md",
    "CARD_STACK_DASHBOARD.md",
    "CARD_STACK_QUICK_START.md",
    "CONTEXT_ENGINEERING_COMPLETE.md",
    "CONTEXT_ENGINEERING_GUIDE.md",
    "CONTEXT_ENGINEERING_QUICKSTART.md",
    "CORTEXCHAT_CONNECTION_FIX.md",
    "EMBEDDING_MODEL_FIX.md",
    "ERROR_RESOLUTION_REPORT.txt",
    "FIX_SUMMARY.md",
    "MEDIA_CORE_ARCHITECTURE.h",
    "MEDIA_CORE_INTEGRATION.md",
    "MEDIA_CORE_NOMAD_SUMMARY.md",
    "MOBILE_DRAG_FIX.md",
    "NOMAD_LIST_STYLE_DESIGN.md",
    "QUICK_FIX.md",
    "RUNTIME_ERROR_FIX.md",
    "SESSION_COMPLETE_SUMMARY.md",
    "UI_FIX_CAPTUREVIEW.md"
)

foreach ($doc in $archiveDocs) {
    if (Test-Path $doc) {
        Move-Item -Path $doc -Destination "docs\archive\" -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] Moved $doc" -ForegroundColor Green
    }
}

Write-Host ""

# ============================================================================
# Step 5: Results
# ============================================================================

Write-Host "[5/5] Cleanup Complete!" -ForegroundColor Yellow
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Final Sizes" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$dirs = @("frontend-body", "backend-cortex", "node_modules", "docs")
foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        $size = (Get-ChildItem $dir -Recurse -ErrorAction SilentlyContinue | 
                 Measure-Object -Property Length -Sum).Sum / 1MB
        $sizeRounded = [math]::Round($size, 2)
        Write-Host "$dir : $sizeRounded MB" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Reinstall Python venv if needed."
Write-Host "2. Rebuild frontend if needed."
Write-Host "3. Check docs/ for core documentation."
Write-Host ""
Write-Host "[DONE] System Purified." -ForegroundColor Green
