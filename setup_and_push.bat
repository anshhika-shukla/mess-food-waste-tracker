@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo  Git & GitHub Auto-Setup: Smart Mess Food Feedback & Waste Tracker
echo =====================================================================
echo.

:: 1. Check Git
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git is not installed or not in your PATH.
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

:: 2. Initialize Git repo if not already initialized
if not exist ".git" (
    echo [*] Initializing local Git repository on main branch...
    git init -b main
) else (
    echo [*] Local Git repository already initialized.
    git branch -M main
)

:: 3. Configure Git user if not already set globally
git config user.name >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set /p GIT_NAME="Enter your Git name: "
    git config user.name "!GIT_NAME!"
)
git config user.email >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set /p GIT_EMAIL="Enter your Git email: "
    git config user.email "!GIT_EMAIL!"
)

:: 4. Stage and commit files
echo [*] Staging all files...
git add .

echo [*] Committing initial release...
git commit -m "feat: initial release of Smart Mess Food Feedback and Waste Tracker"

:: 5. GitHub Remote setup
echo.
echo =====================================================================
echo  Configuring GitHub Remote
echo =====================================================================
where gh >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [*] GitHub CLI (gh) detected. Checking authentication status...
    gh auth status >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Authenticated with GitHub CLI!
        echo [*] Creating remote repository 'mess-food-waste-tracker' on GitHub...
        gh repo create mess-food-waste-tracker --public --source=. --remote=origin --push
        if %ERRORLEVEL% EQU 0 (
            echo.
            echo [SUCCESS] Repository successfully created and pushed to GitHub!
            pause
            exit /b 0
        ) else (
            echo [NOTE] gh repo create returned a notice (repository may already exist). Trying git push...
            git push -u origin main
        )
    ) else (
        echo [INFO] gh is installed but not logged in.
        echo Run 'gh auth login' or specify manual remote URL below.
    )
)

:: Fallback to manual remote
echo.
set /p REPO_URL="Enter your GitHub Repository URL (or press Enter if origin is already set): "
if not "!REPO_URL!"=="" (
    git remote remove origin >nul 2>&1
    git remote add origin !REPO_URL!
)

echo [*] Pushing branch main to origin...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Repository successfully pushed to GitHub!
) else (
    echo.
    echo [NOTICE] If pushing failed, please ensure your GitHub authentication token is configured or run:
    echo          gh auth login
    echo          git push -u origin main
)

echo.
pause
