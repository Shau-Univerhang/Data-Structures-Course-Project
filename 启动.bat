@echo off
echo ========================================
echo    邮游世界 - 启动脚本
echo ========================================
echo.

cd /d "%~dp0backend"
echo [1/2] 启动后端服务器...
start "Backend" cmd /k "python -m uvicorn main:app --port 8000"

cd /d "%~dp0frontend"
echo [2/2] 启动前端服务器...
start "Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo    启动完成！
echo ========================================
echo 前端: http://localhost:5173
echo 后端: http://localhost:8000
echo.
pause
