# 邮游世界 - 日记模块工作流程文档

## 概述

本文档详细描述邮游世界应用中日记模块的完整工作流程，包括数据流、API接口、状态管理和页面交互。

## 技术栈

- **前端**: Vue 3 + Pinia + Vue Router
- **后端**: FastAPI + SQLAlchemy
- **数据库**: SQLite
- **状态管理**: Pinia (全局状态)

---

## 数据库结构

### 日记表 (travel_diaries)

| 字段                    | 类型          | 说明                          |
| --------------------- | ----------- | --------------------------- |
| id                    | Integer     | 主键，自增                       |
| user_id               | Integer     | 外键，关联 users.id              |
| trip_id               | Integer     | 外键，关联 trips.id              |
| title                 | String(200) | 日记标题                        |
| content               | Text        | 日记内容                        |
| content_compressed    | BLOB        | 压缩后的内容                      |
| compression_algorithm | String(20)  | 压缩算法                        |
| diary_type            | String(20)  | 类型: travel/food/photo/notes |
| is_public             | Boolean     | 是否公开                        |
| images                | JSON        | 图片列表                        |
| videos                | JSON        | 视频列表                        |
| view_count            | Integer     | 浏览量                         |
| avg_rating            | Float       | 平均评分                        |
| rating_count          | Integer     | 评分人数                        |
| status                | String(20)  | 状态: published/draft         |
| created_at            | String      | 创建时间                        |
| updated_at            | String      | 更新时间                        |

### 关联表

- **diary_ratings**: 日记评分表
- **diary_comments**: 日记评论表

---

## 全局状态管理 (Pinia)

### Store: diary.js

#### State

```javascript
{
  currentUser: { id, username, avatar_url },  // 当前登录用户
  diaryList: [],                              // 用户的日记列表
  diaryStats: {                               // 日记统计
    total: 0,
    byType: { travel: 0, food: 0, photo: 0, notes: 0 }
  }
}
```

#### Actions

| 方法                      | 说明                      |
| ----------------------- | ----------------------- |
| `loadUserFromStorage()` | 从 localStorage 加载用户     |
| `setCurrentUser(user)`  | 设置当前用户并保存到 localStorage |
| `fetchDiaries()`        | 从服务器获取日记列表              |
| `createDiary(data)`     | 创建新日记并添加到列表             |
| `addDiary(diary)`       | 添加日记到列表（本地）             |
| `updateDiary(id, data)` | 更新日记                    |
| `removeDiary(id)`       | 删除日记                    |
| `clearData()`           | 清空数据（退出登录）              |

#### Getters

| 属性           | 说明    |
| ------------ | ----- |
| `hasDiaries` | 是否有日记 |
| `diaryCount` | 日记总数  |

---

## 页面工作流程

### 1. 登录流程

```
用户登录成功
    ↓
后端返回用户信息 { id, username, avatar_url }
    ↓
diaryStore.setCurrentUser(user)  // 保存到全局状态和 localStorage
    ↓
跳转到 Diary 或 Profile 页面
```

### 2. Diary 页面 (/diary)

#### 页面加载流程

```
进入 Diary 页面
    ↓
onMounted 触发
    ↓
diaryStore.loadUserFromStorage()  // 检查登录状态
    ↓
如果未登录 → 跳转到登录页
    ↓
如果已登录 → diaryStore.fetchDiaries()  // 从服务器获取日记列表
    ↓
更新 diaryStore.diaryList
    ↓
页面显示日记列表 (使用 computed(() => diaryStore.diaryList))
```

#### 创建日记流程

```
用户点击"写日记"按钮
    ↓
打开 SmartDiaryEditor 组件
    ↓
用户输入标题和内容
    ↓
点击"发布"按钮
    ↓
handlePublish() 调用
    ↓
diaryStore.createDiary({
    title,
    content,
    diary_type,
    is_public
})
    ↓
发送 POST 请求: /api/diaries?user_id={currentUser.id}
    ↓
后端保存日记到数据库，关联 user_id
    ↓
返回新创建的日记数据
    ↓
diaryStore.addDiary(newDiary)  // 添加到全局列表
    ↓
自动更新页面显示
    ↓
关闭编辑器弹窗
    ↓
显示"发布成功"提示
```

#### 从详情页返回刷新

```
用户在日记详情页
    ↓
点击返回按钮
    ↓
路由变化: /diary/123 → /diary
    ↓
watch(() => route.path) 监听到变化
    ↓
如果新路径是 '/diary'
    ↓
自动调用 diaryStore.fetchDiaries() 刷新数据
```

### 3. Profile 页面 (/profile)

#### 页面加载流程

```
进入 Profile 页面
    ↓
onMounted 触发
    ↓
diaryStore.loadUserFromStorage()  // 检查登录状态
    ↓
如果未登录 → 跳转到登录页
    ↓
如果已登录
    ↓
diaryStore.fetchDiaries()  // 获取日记列表
    ↓
显示用户信息: computed(() => diaryStore.currentUser)
    ↓
显示日记数量: computed(() => diaryStore.diaryCount)
    ↓
调用 fetchStats() 获取其他统计数据
```

#### 点击"我的日记"

```
用户点击"我的日记"菜单项
    ↓
goDiary() 调用 router.push('/diary')
    ↓
跳转到 Diary 页面
    ↓
Diary 页面使用相同的 diaryStore.diaryList
    ↓
显示与 Profile 页面同步的日记数据
```

### 4. 日记详情页 (/diary/:id)

#### 页面加载流程

```
进入详情页 /diary/123
    ↓
从路由参数获取 diaryId
    ↓
loadDiary() 调用
    ↓
发送 GET 请求: /api/diaries/123
    ↓
后端返回日记详情
    ↓
显示日记内容
    ↓
发送 POST 请求: /api/diaries/123/view  // 增加浏览量
```

---

## API 接口列表

### 日记相关

| 方法   | 路径                          | 说明        |
| ---- | --------------------------- | --------- |
| GET  | `/api/diaries?user_id={id}` | 获取用户的日记列表 |
| POST | `/api/diaries?user_id={id}` | 创建新日记     |
| GET  | `/api/diaries/{id}`         | 获取日记详情    |
| POST | `/api/diaries/{id}/view`    | 增加浏览量     |
| GET  | `/api/diaries/public`       | 获取公开日记    |

### 评论相关

| 方法     | 路径                                                    | 说明     |
| ------ | ----------------------------------------------------- | ------ |
| GET    | `/api/diaries/{id}/comments`                          | 获取日记评论 |
| POST   | `/api/diaries/{id}/comments?user_id={id}`             | 发表评论   |
| POST   | `/api/diaries/{id}/comments/{commentId}/like`         | 点赞评论   |
| DELETE | `/api/diaries/{id}/comments/{commentId}?user_id={id}` | 删除评论   |

### 评分相关

| 方法   | 路径                                      | 说明     |
| ---- | --------------------------------------- | ------ |
| GET  | `/api/diaries/{id}/rating?user_id={id}` | 获取评分信息 |
| POST | `/api/diaries/{id}/rating?user_id={id}` | 提交评分   |

---

## 数据同步机制

### 全局状态共享

```
┌─────────────────┐     ┌─────────────────┐
│   Profile 页面   │     │   Diary 页面    │
│                 │     │                 │
│  diaryStore.    │◄───►│  diaryStore.    │
│  diaryList      │     │  diaryList      │
│                 │     │                 │
│  diaryStore.    │◄───►│  diaryStore.    │
│  diaryCount     │     │  currentUser    │
└─────────────────┘     └─────────────────┘
          │                       │
          └───────────┬───────────┘
                      │
              ┌───────▼────────┐
              │  Pinia Store   │
              │  (diary.js)    │
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │   后端 API     │
              │  (FastAPI)     │
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │   SQLite DB    │
              │  (travel.db)   │
              └────────────────┘
```

### 同步触发时机

1. **页面加载时**: `onMounted` 调用 `fetchDiaries()`
2. **创建日记后**: `createDiary()` 内部调用 `addDiary()`
3. **路由变化时**: `watch(route.path)` 检测到返回 `/diary`
4. **手动刷新**: 用户可以下拉刷新或点击刷新按钮

---

## 关键修复记录

### 修复1: API 端口统一

**问题**: 前端代码中混用 `localhost:8000` 和 `localhost:8080`

**修复**: 统一所有 API 请求到 `localhost:8000`

### 修复2: user_id 传递方式

**问题**: 前端把 `user_id` 放在 body 中，后端从 Query 参数获取

**修复**: 

```javascript
// 修复前
fetch('/api/diaries', {
  body: JSON.stringify({ user_id: xxx, ... })
})

// 修复后
fetch(`/api/diaries?user_id=${userId}`, {
  body: JSON.stringify({ ... })  // 不包含 user_id
})
```

### 修复3: 引入 Pinia 全局状态

**问题**: Diary 和 Profile 页面各自管理状态，数据不同步

**修复**: 创建 `diary.js` Store，统一管理用户和日记数据

### 修复4: 删除 Mock 数据

**问题**: 评论和评分使用静态 Mock 数据

**修复**: 删除所有 Mock 数据逻辑，只使用真实 API 数据

---

## 使用说明

### 用户操作流程

1. **登录**: 输入账号密码，登录成功后用户信息保存到全局状态
2. **查看日记**: 进入 Diary 页面，自动加载用户的日记列表
3. **创建日记**: 点击"写日记"，输入内容后发布，自动刷新列表
4. **查看详情**: 点击日记卡片，进入详情页查看完整内容
5. **返回列表**: 点击返回按钮，自动刷新日记列表
6. **Profile 查看**: 进入 Profile 页面，显示日记数量统计

### 开发者注意事项

1. **必须登录**: 所有日记操作都需要登录状态
2. **全局状态**: 修改日记数据时，使用 `diaryStore` 的方法
3. **API 端口**: 确保所有请求使用 `localhost:8000`
4. **user_id**: 通过 Query 参数传递，不要放在 body 中
5. **数据同步**: 创建/修改日记后，全局状态会自动更新

---

## 文件结构

```
frontend/
├── src/
│   ├── stores/
│   │   ├── diary.js          # 日记全局状态
│   │   └── trip.js           # 行程全局状态
│   ├── views/
│   │   ├── Diary.vue         # 日记列表页
│   │   ├── DiaryDetail.vue   # 日记详情页
│   │   └── Profile.vue       # 个人中心页
│   └── components/
│       ├── SmartDiaryEditor.vue  # 日记编辑器
│       └── CommentsRatings.vue   # 评论评分组件
│
backend/
├── models/
│   └── database.py           # 数据库模型
├── routers/
│   ├── diary.py              # 日记 API
│   └── diary_api.py          # 评论评分 API
└── data/
    └── travel.db             # SQLite 数据库文件
```

---

## 总结

通过引入 Pinia 全局状态管理，日记模块实现了：

1. **数据共享**: Diary 和 Profile 页面共享同一份日记数据
2. **实时同步**: 创建日记后，所有页面自动更新
3. **持久化**: 数据保存到 SQLite 数据库，不会丢失
4. **用户隔离**: 每个用户只能看到自己的日记
5. **统一接口**: 所有 API 使用相同的端口和格式

现在用户可以正常创建、查看、管理自己的日记，数据在两个页面间完全同步。
