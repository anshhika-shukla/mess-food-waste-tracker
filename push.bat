@echo off
cd /d "%~dp0"
echo =====================================================================
echo  Pushing Smart Mess Tracker to GitHub: anshhika-shukla/mess-food-waste-tracker
echo =====================================================================
echo.

echo [1/5] Checking Git repository initialization...
if not exist ".git" (
    git init -b main
) else (
    echo Git repository already initialized.
)

echo.
echo [2/5] Staging files...
git add .

echo.
echo [3/5] Committing initial release...
git commit -m "feat: initial release of Smart Mess Food Feedback and Waste Tracker"

echo.
echo [4/5] Setting remote origin to https://github.com/anshhika-shukla/mess-food-waste-tracker.git ...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/anshhika-shukla/mess-food-waste-tracker.git
git branch -M main

echo.
echo [5/5] Pushing branch main to origin...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =====================================================================
    echo  [SUCCESS] Successfully pushed to https://github.com/anshhika-shukla/mess-food-waste-tracker !
    echo =====================================================================
) else (
    echo.
    echo [ERROR] Push failed. If this is a private repo or authentication is needed,
    echo         make sure you are logged in via 'gh auth login' or your Git credentials.
)

echo.
pause
