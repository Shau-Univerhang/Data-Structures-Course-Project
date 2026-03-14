@echo off
chcp 936 >nul
title Travel System

cd /d "%~dp0"

echo [1/4] Starting backend...
start "Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn main:app --port 8000"

echo [2/4] Starting frontend...
start "Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo [3/4] Waiting...
timeout /t 8 /nobreak >nul

echo [4/4] Done!
echo.
echo ========================
echo Open: http://localhost:5173
echo ========================
echo.

start http://localhost:5173
pause
