# 邮游世界 - 个性化旅游推荐系统

## 项目简介

邮游世界是一个基于大语言模型和自研算法的个性化旅游规划系统，为用户提供智能行程规划、景点推荐、路线规划等功能。

## 系统功能

### 1. 首页轮播
- 高级堆叠式（Stacked）布局，数据驱动偏移算法
- 悬停即切换（Hover-to-Swap）交互
- 动态进度条，自动播放与手动切换联动
- 沉浸式背景，高斯模糊效果

### 2. 旅游推荐
- 基于热度、评价和个人兴趣推荐目的地
- 支持名称、类别、关键字查询

### 3. 路线规划
- 最优路径：规划起点到单个或多个目标点的最优线路
- 多种策略：最短距离、最短时间、步行/自行车/电瓶车
- 可视化：提供地图展示和路径输出的图形界面
- 室内导航

### 4. 场所查询
- 查找景区/校园内附近的设施（超市、卫生间）
- 支持按类别过滤和距离排序

### 5. 旅游日记
- 记录与管理：支持文字、图片、视频记录
- 检索与评价：支持全文检索、精确查询及基于热度/评价的推荐

### 6. 美食推荐
- 按热度、评价、距离和菜系推荐美食
- 支持模糊查询

### 7. AI助手
- 使用AIGC算法生成旅游动画
- 智能解析小红书行程链接

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | FastAPI + Python |
| 前端 | Vue 3 + Element Plus |
| 数据库 | SQLite |
| AI | MiniMax API |

## 核心算法

| 算法 | 说明 | 时间复杂度 |
|------|------|-----------|
| Dijkstra | 最短路径算法 | O((V+E)logV) |
| TSP | 旅行商问题求解（贪心+贪心优化） | O(n²) |
| TopK | 部分排序推荐 | O(nlogk) |
| 模糊查找 | 支持拼音首字母、通配符 | O(n) |
| Gzip | 无损压缩 | - |

## 图片资源获取

### 爬虫脚本

项目提供多个专用爬虫脚本：

| 脚本 | 说明 |
|------|------|
| scripts/scrapers/spots_scrape_baidu.py | 百度景点图片爬虫 |
| scripts/scrapers/foods_scrape_xiachufang.py | 下厨房美食图片爬虫 |
| scripts/scrapers/cities_unsplash_downloader.py | Unsplash 城市图片下载器 |

### Unsplash API 图片爬取

本项目使用 Unsplash Official API 获取城市和美食的高清图片。

#### 1. 获取 API Key

1. 访问 [Unsplash Developers](https://unsplash.com/developers)
2. 注册/登录账号
3. 点击 "Your Apps" → "New Application"
4. 填写基本信息并同意条款
5. 获取 **Access Key**

#### 2. 使用图片下载脚本

```bash
# 安装依赖（如需要）
pip install requests

# 运行脚本
python unsplash_downloader.py --key YOUR_ACCESS_KEY

# 参数说明
# --key     Unsplash API Access Key (必填)
# --type    下载类型: city / food / all (默认: all)
# --output  输出目录 (默认: ./downloads)
# --count   每个关键字下载数量 (默认: 1)

# 示例
python unsplash_downloader.py --key abc123xyz --type city
```

#### 3. 图片命名规范

- 城市图片：`cities/城市名拼音.jpg` (如 beijing.jpg, shanghai.jpg)
- 美食图片：`foods/美食名拼音.jpg` (如 beijing-duck.jpg)
- 景点图片：`spots/{城市拼音}/{城市拼音}_{景点拼音}.jpg`

#### 4. 在项目中使用

下载的图片放入 `frontend/public/images/` 目录，前端代码通过相对路径引用：

```javascript
const destinations = [
  { name: '北京', image: '/images/cities/beijing.jpg' },
  // ...
]
```

## 数据规模

- 景区数量: ≥200个
- 道路边数: ≥200条
- 服务设施: ≥10种
- 建筑数量: ≥20个/景区

## 项目结构

```
├── backend/           # FastAPI后端
│   ├── main.py       # 主程序
│   ├── routers/      # API路由
│   ├── algorithms/   # 核心算法
│   └── data/         # SQLite数据库
├── frontend/         # Vue 3前端
│   ├── src/
│   │   ├── views/   # 页面组件
│   │   ├── components/
│   │   └── router/
│   └── package.json
├── scripts/          # 爬虫脚本
│   └── scrapers/     # 图片爬虫
├── images/           # 图片资源
│   ├── cities/       # 城市图片
│   ├── spots/        # 景点图片（按城市分类）
│   └── foods/        # 美食图片
├── unsplash_downloader.py  # Unsplash图片下载脚本
└── README.md
```

## 快速启动

### Windows
双击 `启动.bat` 即可启动前后端

### 手动启动
```bash
# 后端
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --port 8000

# 前端
cd frontend
npm install
npm run dev
```

## 访问地址

- 前端：http://localhost:5173
- 后端：http://localhost:8000
- API文档：http://localhost:8000/docs

## 课程设计信息

- **课程**：数据结构
- **学校**：北京邮电大学

---

*Enjoy your trip! 🌍✈️*
