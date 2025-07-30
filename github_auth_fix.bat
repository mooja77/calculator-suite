@echo off
echo 🔐 GitHub Authentication Fix
echo ===========================

echo.
echo The browser authentication is stuck. Let's use a different method.
echo.

echo 📋 Option 1: Personal Access Token (RECOMMENDED)
echo ------------------------------------------------
echo 1. Go to: https://github.com/settings/tokens
echo 2. Click "Generate new token (classic)"
echo 3. Give it a name: "Calculator Suite Deployment"
echo 4. Select scopes: ✓ repo (all checkboxes under repo)
echo 5. Click "Generate token" at the bottom
echo 6. COPY THE TOKEN NOW (you won't see it again!)
echo.
echo 7. When Git asks for:
echo    Username: your-github-username
echo    Password: paste-your-token-here (NOT your GitHub password)
echo.

echo 📋 Option 2: Use GitHub Desktop (EASIEST)
echo ----------------------------------------
echo 1. Download GitHub Desktop: https://desktop.github.com/
echo 2. Sign in with your GitHub account
echo 3. Add your local repository
echo 4. Push to GitHub through the GUI
echo.

echo 📋 Option 3: Use HTTPS with stored credentials
echo ----------------------------------------------
echo Let's configure Git to store your credentials:
echo.

choice /C YN /M "Do you want to configure credential storage"
if errorlevel 2 goto :skip_cred

echo.
echo Configuring credential manager...
git config --global credential.helper manager-core
git config --global credential.https://github.com.username %username%

echo.
echo ✅ Credential manager configured!
echo.

:skip_cred

echo 🚀 Now let's try pushing again with your chosen method:
echo.
echo Run this command:
echo git push -u origin main
echo.
echo And use one of the authentication methods above.
echo.

pause