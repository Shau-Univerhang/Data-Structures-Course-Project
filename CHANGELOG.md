# 更新日志

## 2026-03-17

### 轮播组件重构

1. **高级堆叠式（Stacked）布局**
   - 数据驱动偏移算法：根据 activeIndex 动态计算每个卡片的 translateX、scale、zIndex、opacity
   - 位移：translateX = diff * 120px（产生重叠感）
   - 缩放：scale = 1 - Math.abs(diff) * 0.15
   - 层级：zIndex = 100 - Math.abs(diff)
   - 透明度：非中心卡片 opacity = 0.5

2. **悬停即切换（Hover-to-Swap）**
   - 鼠标悬停卡片时立即切换到该卡片
   - 平滑过渡动画，active 卡片保持在容器水平居中

3. **动态进度条**
   - 底部线性进度指示器，与卡片数量同步
   - 自动播放：每 5 秒切换，进度条从 0% 匀速增长到 100%
   - 交互联动：鼠标悬停在卡片上时进度条暂停，离开后继续

4. **视觉与动效**
   - 贝塞尔曲线：transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)
   - 沉浸式背景：背景图与 activeIndex 同步，添加 blur(20px) brightness(0.5)
   - 卡片保持 3:4 纵横比，底部渐变蒙层

### 图片资源重构

1. **爬虫脚本（scripts/scrapers/）**
   - spots_scrape_baidu.py - 百度景点图片爬虫
   - foods_scrape_xiachufang.py - 下厨房美食图片爬虫
   - cities_unsplash_downloader.py - Unsplash 城市图片下载器

2. **景点图片目录重构**
   - 从扁平结构改为按城市分类：images/spots/{city}/{city}_{spot}.jpg
   - 更新了 16 个城市的景点图片

3. **前端优化**
   - 更新 City.vue 景点图片映射
   - 更新 SpotRecommend.vue 景点图片映射

4. **后端优化**
   - 更新 spots.py API 图片映射逻辑
   - 添加 SPOT_IMAGES 和 CITY_IMAGES 映射表

5. **清理冗余文件**
   - 删除旧版扁平结构图片
   - 删除废弃脚本（scrape_mafengwo.py, download_all_images.py 等）
   - 删除 下载图片.bat

---
## 2026-03-14

### 功能优化

1. **图片资源修复**
   - 修复前端图片引用错误（杭州、南京、长沙、深圳、三亚等城市图片）
   - 重新生成 45 张城市和景点真实图片
   - 更新 City.vue 和 Home.vue 图片映射

2. **旅游日记模块重构**
   - 主界面添加 4 个可视化模板按钮（行程攻略、美食探索、摄影大片、随笔感悟）
   - 添加"发现精彩日记"轮播展示区
   - 空状态友好设计：飞机图标 + 引导提示 + 立即开始按钮
   - 弹窗内添加便捷输入按钮（+行程、+美食、+住宿、+贴士、+评分）
   - 支持 4 种日记类型：travel/food/photo/notes

3. **小红书导入功能优化**
   - 修复行程创建用户 ID 问题
   - 添加行程详情跳转链接
   - 完善创建成功提示信息

4. **数据库扩展**
   - travel_diaries 表新增 diary_type 字段
   - travel_diaries 表新增 is_public 字段
   - 新增 /api/diaries/public 接口获取公开日记

5. **示例数据丰富**
   - 添加 3 个示例行程（北京三日游、杭州西湖游、成都美食之旅）
   - 每个行程包含详细每日安排
   - 添加 4 篇公开日记示例

### 代码清理

- 清理 39 个临时脚本文件
- 优化项目目录结构

---

## 2026-03-13

### 新增功能

1. **热门目的地模块**
   - 城市数量扩充到18个
   - 城市图片修正

2. **景点推荐**
   - API路径修复

3. **路线规划**
   - 地图框架添加

4. **美食推荐**
   - 城市/菜系筛选
   - 详情弹窗
   - 评论功能

5. **启动脚本**
   - Windows启动脚本
   - 快速开始文档

---

## 初始版本

- 后端：FastAPI + SQLite
- 前端：Vue 3 + Element Plus
- 核心算法：Dijkstra、TSP、TopK、模糊查找
