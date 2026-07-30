@echo off
title ZipLoot Cloudflare AI Studio Installer
cls
echo ========================================================
echo   ZipLoot Cloudflare AI Bot & API Studio (1-Click)
echo ========================================================
echo.

where python >nul 2>&1
if %errorlevel% equ 0 goto :FOUND_PY

echo [ERROR] Python is not installed or not in PATH!
echo Please install Python 3.9+ from https://python.org and rerun.
pause
exit /b 1

:FOUND_PY
echo [1/2] Checking and installing requirements...
python -m pip install flask requests --quiet

echo.
echo [2/2] Launching ZipLoot Cloudflare AI Studio...
echo Opening Web UI in your browser...
python app.py

pause
