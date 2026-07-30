@echo off
title ZipLoot Cloudflare AI Studio Automated Installer
cls
echo ========================================================
echo   ZipLoot Cloudflare AI Bot & API Studio (Automated)
echo ========================================================
echo.

where python >nul 2>&1
if %errorlevel% equ 0 goto :FOUND_PY

echo [ERROR] Python is not installed or not in PATH!
echo Please install Python 3.9+ from https://python.org and rerun.
pause
exit /b 1

:FOUND_PY
echo [1/3] Installing Python dependencies...
python -m pip install flask requests --quiet

echo.
echo [2/3] Authenticating with Cloudflare via Wrangler...
echo Opening browser for Cloudflare 1-Click Permission...
cmd.exe /c "npx -y wrangler login"

echo.
echo [3/3] Building & Deploying Serverless AI Worker to Cloudflare...
cmd.exe /c "npx -y wrangler deploy worker.js --name cloudflare-ai-bot-studio"

echo.
echo ========================================================
echo [SUCCESS] Cloudflare AI Worker Deployed Automatically!
echo Launching Local Studio & AI Chatbot Interface...
echo ========================================================
python app.py

pause
