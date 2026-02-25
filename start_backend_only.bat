@echo off
TITLE LifeOS Backend - Direct Start
COLOR 0A

echo ========================================================
echo   Starting LifeOS Backend (Direct Mode)
echo ========================================================
echo.

cd /d "%~dp0backend-cortex"

echo [INFO] Current directory: %CD%
echo [INFO] Starting backend...
echo.

python main.py

pause
