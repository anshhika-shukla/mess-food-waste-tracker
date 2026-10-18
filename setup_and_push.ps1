<#
.SYNOPSIS
    Automated Git and GitHub repository setup script for Smart Mess Food Feedback & Waste Tracker.
#>

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  Git & GitHub Auto-Setup: Smart Mess Food Feedback & Waste Tracker" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Git is not installed or not in PATH. Please install Git from https://git-scm.com/" -ForegroundColor Red
    exit 1
}

# 2. Initialize Git
if (-not (Test-Path ".git")) {
    Write-Host "[*] Initializing local Git repository on main branch..." -ForegroundColor Yellow
    git init -b main
} else {
    Write-Host "[*] Git repository already initialized." -ForegroundColor Green
    git branch -M main
}

# 3. Stage and commit
Write-Host "[*] Staging files..." -ForegroundColor Yellow
git add .

Write-Host "[*] Committing initial release..." -ForegroundColor Yellow
git commit -m "feat: initial release of Smart Mess Food Feedback and Waste Tracker"

# 4. GitHub remote setup via gh or git remote
Write-Host ""
Write-Host "[*] Checking GitHub CLI (gh)..." -ForegroundColor Yellow
$ghAvailable = Get-Command gh -ErrorAction SilentlyContinue

if ($ghAvailable) {
    gh auth status 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Authenticated with GitHub CLI." -ForegroundColor Green
        Write-Host "[*] Creating remote repository 'mess-food-waste-tracker' on GitHub..." -ForegroundColor Yellow
        gh repo create mess-food-waste-tracker --public --source=. --remote=origin --push
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "[SUCCESS] Repository created and pushed to GitHub successfully!" -ForegroundColor Green
            exit 0
        } else {
            Write-Host "[*] Trying standard git push to origin..." -ForegroundColor Yellow
            git push -u origin main
        }
    } else {
        Write-Host "[INFO] gh is installed but not authenticated. Run 'gh auth login' or enter remote URL below." -ForegroundColor Yellow
    }
}

$repoUrl = Read-Host "Enter your GitHub Repository URL (or press Enter if origin is already set)"
if ($repoUrl -and $repoUrl.Trim() -ne "") {
    git remote remove origin 2>$null
    git remote add origin $repoUrl.Trim()
}

Write-Host "[*] Pushing to origin main..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Repository successfully pushed to GitHub!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[NOTICE] If push failed, authenticate your GitHub account via:" -ForegroundColor DarkYellow
    Write-Host "         gh auth login" -ForegroundColor White
    Write-Host "         git push -u origin main" -ForegroundColor White
}
