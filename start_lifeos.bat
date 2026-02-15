
@echo off
TITLE LifeOS v7.1 Launch System
COLOR 0A

echo ========================================================
echo   LifeOS v7.1 - Cortex & Body Activation Protocol
echo ========================================================
echo.

echo [1/4] Terminating Ghost Processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
echo       - Port 8000 (Backend) Cleared.
echo       - Port 3000 (Frontend) Cleared.
echo.

echo [2/4] Awakening Cortex (Backend)...
start "LifeOS Cortex (Do Not Close)" cmd /k "cd backend-cortex && ..\.venv\Scripts\activate && python main.py"
timeout /t 5 >nul
echo       - Cortex Signal Active.
echo.

echo [3/4] Materializing Body (Frontend)...
start "LifeOS Body (Do Not Close)" cmd /k "cd frontend-body && npm run dev"
echo       - Body Synthesis Initiated.
echo.

echo [4/4] Establishing Neural Link...
timeout /t 8 >nul
start http://localhost:3000
echo.

echo ========================================================
echo   SYSTEM ONLINE.
echo   - Backend: http://127.0.0.1:8000
echo   - Frontend: http://localhost:3000
echo.
echo   Keep the popup windows open. Minimizing them is fine.
echo ========================================================
pause
