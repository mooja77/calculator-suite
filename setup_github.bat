@echo off
echo 🚀 Calculator Suite - GitHub Setup Script
echo ==========================================

echo.
echo 📋 Step 1: Initialize Git Repository
git init
if %errorlevel% neq 0 (
    echo ❌ Git init failed. Make sure Git is installed.
    pause
    exit /b 1
)

echo.
echo 📁 Step 2: Add all files to Git
git add .
if %errorlevel% neq 0 (
    echo ❌ Git add failed.
    pause
    exit /b 1
)

echo.
echo 💾 Step 3: Create initial commit
git commit -m "Calculator Suite v1.0 - Production Ready with 21+ Calculators"
if %errorlevel% neq 0 (
    echo ❌ Git commit failed.
    pause
    exit /b 1
)

echo.
echo 🌐 Step 4: Setup for GitHub
echo.
echo IMPORTANT: Before continuing, create a GitHub repository:
echo 1. Go to https://github.com
echo 2. Click "New Repository"
echo 3. Name: calculator-suite (or your preferred name)
echo 4. Set to PUBLIC (required for free deployment)
echo 5. DON'T initialize with README
echo 6. Click "Create Repository"
echo.

set /p username="Enter your GitHub username: "
set /p reponame="Enter your repository name (default: calculator-suite): "

if "%reponame%"=="" set reponame=calculator-suite

echo.
echo 🔗 Step 5: Connect to GitHub
git remote add origin https://github.com/%username%/%reponame%.git
if %errorlevel% neq 0 (
    echo ❌ Failed to add remote. Check your username and repository name.
    pause
    exit /b 1
)

echo.
echo 📤 Step 6: Push to GitHub
git branch -M main
git push -u origin main
if %errorlevel% neq 0 (
    echo ❌ Push failed. Make sure your GitHub repository exists and is public.
    echo You may need to authenticate with GitHub.
    pause
    exit /b 1
)

echo.
echo ✅ SUCCESS! Your Calculator Suite is now on GitHub!
echo.
echo 🔗 Repository URL: https://github.com/%username%/%reponame%
echo.
echo 🚀 Next Steps:
echo 1. Go to render.com and create a free account
echo 2. Create a new Web Service
echo 3. Connect your GitHub repository
echo 4. Follow the deployment guide in DEPLOY_NOW.md
echo.
echo Press any key to open your GitHub repository...
pause >nul
start https://github.com/%username%/%reponame%