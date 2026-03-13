@echo off
chcp 65001 >nul
title 邮游世界 - 启动器
color 0A

echo =========================================
echo        邮游世界 - 个性化旅游系统
echo =========================================
echo.

cd /d "%~dp0"

echo [1/4] 检查依赖...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python
    pause
    exit /b 1
)

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

echo [2/4] 启动后端服务...
start "邮游后端 (8000)" cmd /k "cd /d "%~dp0backend" && python -m uvicorn main:app --port 8000"

echo [3/4] 启动前端服务...
start "邮游前端 (5173)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo [4/4] 打开入口页面...
start "" "%~dp0index.html"

echo.
echo =========================================
echo ✅ 启动完成！
echo =========================================
echo.
echo 📍 访问地址：
echo    - 应用首页：http://localhost:5173
echo    - API文档：http://localhost:8000/docs
echo.
echo 💡 提示：
echo    - 首次启动会自动安装依赖
echo    - 如端口被占用请关闭其他应用
echo.
echo 按任意键打开管理界面...
pause >nul

start http://localhost:5173
