Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host " Pushing Smart Mess Tracker to anshhika-shukla/mess-food-waste-tracker" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

if (-not (Test-Path ".git")) {
    Write-Host "[1/5] Initializing git repository on main..." -ForegroundColor Yellow
    git init -b main
} else {
    Write-Host "[1/5] Git repository already initialized." -ForegroundColor Green
    git branch -M main
}

Write-Host "[2/5] Staging files..." -ForegroundColor Yellow
git add .

Write-Host "[3/5] Committing release..." -ForegroundColor Yellow
git commit -m "feat: initial release of Smart Mess Food Feedback and Waste Tracker"

Write-Host "[4/5] Setting remote origin..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin https://github.com/anshhika-shukla/mess-food-waste-tracker.git
git branch -M main

Write-Host "[5/5] Pushing to GitHub main branch..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Successfully pushed to https://github.com/anshhika-shukla/mess-food-waste-tracker !" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[NOTICE] If push failed, make sure you are logged in to GitHub via 'gh auth login' or Personal Access Token." -ForegroundColor Red
}
