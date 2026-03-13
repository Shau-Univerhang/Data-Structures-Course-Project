# 邮游世界 - 快速启动

## Windows 用户

### 方法1: 一键启动（推荐）
双击 `启动.bat` 即可同时启动前端和后端

### 方法2: 手动启动

```bash
# 1. 启动后端
cd backend
python -m uvicorn main:app --port 8000

# 2. 启动前端（新终端）
cd frontend
npm run dev
```

## Mac/Linux 用户

```bash
# 启动
chmod +x 启动.sh
./启动.sh
```

## 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 | http://localhost:8000 |
| API文档 | http://localhost:8000/docs |

## 技术栈

- 前端: Vue 3 + Vite
- 后端: FastAPI + SQLite
- 数据库: SQLite (内含)

## 常见问题

### 端口被占用
- 修改后端端口: `python -m uvicorn main:app --port 8001`
- 修改前端端口: 修改 `frontend/vite.config.js` 中的端口

### 依赖安装
```bash
# 前端依赖
cd frontend
npm install

# 后端依赖
cd backend
pip install -r requirements.txt
```

---
Enjoy your trip! 🌍✈️
