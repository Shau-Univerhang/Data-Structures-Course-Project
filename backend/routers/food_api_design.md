# FastAPI 后端接口设计 - 附近美食模块

## 接口概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/spots/restaurants/nearby` | 获取景点附近美食（已存在，需完善） |
| GET | `/api/spots/restaurants/mock` | Mock 数据接口（开发测试用） |

---

## 1. 获取景点附近美食

### 请求

```http
GET /api/spots/restaurants/nearby?spot_id={spot_id}&sort_by={sort_by}&keyword={keyword}&cuisine={cuisine}&top_k={top_k}
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `spot_id` | int | 是 | 景点ID |
| `sort_by` | string | 否 | 排序方式：`distance`(默认) / `rating` / `popularity` |
| `keyword` | string | 否 | 搜索关键词（模糊匹配名称、菜系、标签） |
| `cuisine` | string | 否 | 菜系过滤，如"北京菜"、"川菜" |
| `top_k` | int | 否 | 返回数量，默认 10，最大 20 |

### 响应格式

```json
{
  "spot_id": 1,
  "spot_name": "故宫博物院",
  "sort_by": "distance",
  "keyword": "烤鸭",
  "cuisine": null,
  "top_k": 10,
  "total_candidates": 25,
  "matched_count": 3,
  "cuisine_options": ["北京菜", "北京小吃", "涮羊肉", "咖啡甜品"],
  "restaurants": [
    {
      "id": 203,
      "name": "四季民福烤鸭店(故宫店)",
      "cuisine_type": "北京菜",
      "location_lat": 39.9150,
      "location_lng": 116.4010,
      "rating": 4.8,
      "heat_score": 14500,
      "price_range": "¥¥¥¥",
      "open_time": "10:30-22:00",
      "images": [],
      "tags": ["观景烤鸭", "故宫景观", "排队王"],
      "distance_m": 600,
      "match_score": 1.0,
      "matched_fields": ["name", "tags"],
      "address": "北京市东城区南池子大街"
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 餐厅唯一标识 |
| `name` | string | 餐厅名称 |
| `cuisine_type` | string | 菜系分类 |
| `location_lat` / `location_lng` | float | WGS-84 坐标 |
| `rating` | float | 评分 0-5 |
| `heat_score` | int | 热度/评论数 |
| `price_range` | string | 价格区间 ¥-¥¥¥¥¥ |
| `open_time` | string | 营业时间 |
| `images` | array | 图片URL列表 |
| `tags` | array | 特色标签 |
| `distance_m` | float | 与景点的直线距离（米） |
| `match_score` | float | 搜索匹配度 0-1 |
| `matched_fields` | array | 匹配到的字段名 |
| `address` | string | 详细地址 |

---

## 2. Mock 数据接口（开发测试）

### 请求

```http
GET /api/spots/restaurants/mock?spot_name={spot_name}&sort_by={sort_by}&keyword={keyword}&top_k={top_k}
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `spot_name` | string | 是 | 景点名称，如"故宫博物院" |
| `sort_by` | string | 否 | 排序方式，默认 `distance` |
| `keyword` | string | 否 | 搜索关键词 |
| `top_k` | int | 否 | 返回数量，默认 10 |

### 响应格式

与上方 `/nearby` 接口一致。

---

## 3. 后端实现要点

### 3.1 数据来源优先级

```
1. 高德地图 POI 搜索（线上环境首选）
   - API: https://restapi.amap.com/v3/place/around
   - 参数: keywords=美食, types=050000, radius=3000

2. 数据库 Restaurant 表（已录入数据）

3. Mock 数据（开发/离线环境兜底）
```

### 3.2 排序算法

后端使用 `top_k_restaurants_by_sort()` 部分排序算法（时间复杂度 O(n log k)）：

```python
def _restaurant_sort_tuple(restaurant: dict, sort_by: str = 'distance') -> tuple:
    distance = float(restaurant.get('distance_m') or float('inf'))
    rating = float(restaurant.get('rating') or 0)
    heat_score = float(restaurant.get('heat_score') or 0)
    match_score = float(restaurant.get('match_score') or 0)
    restaurant_id = int(restaurant.get('id') or 0)

    if sort_by == 'popularity':
        return (heat_score, rating, -distance, match_score, -restaurant_id)
    if sort_by == 'rating':
        return (rating, heat_score, -distance, match_score, -restaurant_id)
    return (-distance, rating, heat_score, match_score, -restaurant_id)
```

### 3.3 模糊搜索

使用 `fuzzy_search_restaurants()` 基于编辑距离的模糊匹配，支持多字段搜索：
- 餐厅名称 (`name`)
- 菜系类型 (`cuisine_type`)
- 标签 (`tags`)

---

## 4. 数据库模型（已存在）

```python
class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    cuisine_type = Column(String(50))
    location_lat = Column(Float)
    location_lng = Column(Float)
    rating = Column(Float, default=0)
    heat_score = Column(Integer, default=0)
    price_range = Column(String(20))
    open_time = Column(String(100))
    images = Column(Text)  # JSON
    tags = Column(Text)    # JSON
    spot_id = Column(Integer, ForeignKey("scenic_spots.id"))
    address = Column(String(200))
```

---

## 5. 环境变量配置

```bash
# .env
AMAP_WEB_SERVICE_KEY=你的高德Web服务Key
```

> 注意：高德 JSAPI Key 与 Web服务 Key 不同，周边搜索需使用 Web服务 Key。
