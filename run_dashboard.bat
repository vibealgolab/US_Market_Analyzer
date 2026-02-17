@echo off
TITLE US Market Analyzer - Premium Dashboard
SETLOCAL EnableDelayedExpansion

cls
COLOR 0B
echo ===================================================
echo     Launching US Market Analyzer Dashboard
echo ===================================================
echo.
echo Mode: Premium Next.js (Turbo)
echo Status: Initializing...
echo.

cd /d "%~dp0web"
start "US Market Dashboard (Next.js)" cmd /c "npm run dev"

echo Waiting for dashboard to initialize...
timeout /t 5 /nobreak > nul
start "" "http://localhost:3000"

echo.
echo ===================================================
echo   System is launching in a separate window.
echo   You can close this command prompt.
echo ===================================================
timeout /t 5
exit
