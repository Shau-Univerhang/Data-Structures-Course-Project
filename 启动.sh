#!/bin/bash
echo "========================================"
echo "   邮游世界 - 启动脚本"
echo "========================================"
echo ""

# Start backend
echo "[1/2] 启动后端服务器..."
cd backend
python -m uvicorn main:app --port 8000 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
echo "[2/2] 启动前端服务器..."
cd ../frontend
npm run dev &

echo ""
echo "========================================"
echo "   启动完成！"
echo "========================================"
echo "前端: http://localhost:5173"
echo "后端: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服务"

# Wait for interrupt
trap "kill $BACKEND_PID; exit" INT
wait
