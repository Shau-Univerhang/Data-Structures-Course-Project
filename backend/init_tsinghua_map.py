"""
清华大学校园内部地图数据初始化脚本
通过高德 Web Service API 采集真实 POI 坐标和步行路径，写入数据库
"""
import sys
import os
import json
import time
import math
import sqlite3
import urllib.request
import ssl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

AMAP_KEY = os.getenv("AMAP_WEB_SERVICE_KEY", "5373684f183274b8b2834f1474a929f4")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "travel.db")

# 禁用 SSL 验证（仅用于本地开发脚本）
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


def amap_get(url, params):
    import urllib.parse
    full_url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full_url)
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_poi(keyword, city="北京", limit=1):
    data = amap_get("https://restapi.amap.com/v3/place/text", {
        "key": AMAP_KEY,
        "keywords": keyword,
        "city": city,
        "citylimit": "true",
        "offset": limit,
        "output": "json",
    })
    if data.get("status") == "1" and data.get("pois"):
        return data["pois"]
    return []


def walking_route(origin, dest):
    """返回 (distance_m, duration_s, polyline_points[])"""
    data = amap_get("https://restapi.amap.com/v3/direction/walking", {
        "key": AMAP_KEY,
        "origin": f"{origin[0]},{origin[1]}",
        "destination": f"{dest[0]},{dest[1]}",
        "output": "json",
    })
    if data.get("status") != "1":
        return None
    paths = data.get("route", {}).get("paths", [])
    if not paths:
        return None
    path = paths[0]
    distance = int(path.get("distance", 0))
    duration = int(path.get("duration", 0))
    points = []
    for step in path.get("steps", []):
        poly = step.get("polyline", "")
        for pt in poly.split(";"):
            parts = pt.strip().split(",")
            if len(parts) == 2:
                points.append((float(parts[0]), float(parts[1])))
    return distance, duration, points


def haversine(lng1, lat1, lng2, lat2):
    R = 6371000
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    dφ = math.radians(lat2 - lat1)
    dλ = math.radians(lng2 - lng1)
    a = math.sin(dφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(dλ/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# ==================== 清华大学 POI 定义 ====================
# 格式：(名称, node_type, amap_query, (lng, lat) 备用坐标, 建筑/设施类型)

TSINGHUA_SPOT_ID = 9   # 数据库中清华大学的 scenic_spots.id

ENTRANCES = [
    # (name, amap_query, fallback_lng, fallback_lat)
    ("正门（大礼堂南侧）", "清华大学大礼堂", 116.324430, 40.003693),
    ("西门",             "清华大学西门",   116.315855, 40.000686),
    ("东南门",           "清华大学东南门公交站", 116.332874, 39.997548),
    ("北门",             "清华大学荷清苑", 116.323551, 40.012299),
]

BUILDINGS = [
    # (name, amap_query, fallback_lng, fallback_lat, floor_count, description, building_type)
    ("大礼堂",     "清华大学大礼堂",     116.324430, 40.003693, 3,  "清华大学标志性建筑，建于1917年", "attraction"),
    ("图书馆",     "清华大学图书馆北馆", 116.323995, 40.005630, 5,  "清华大学图书馆，藏书丰富",        "attraction"),
    ("新清华学堂", "清华大学新清华学堂", 116.329039, 40.001695, 4,  "多功能演出场馆",                 "attraction"),
    ("艺术博物馆", "清华大学艺术博物馆", 116.335592, 40.001971, 4,  "展示中国传统艺术与现代设计",       "attraction"),
    ("科学馆",     "清华大学科学馆",     116.323923, 40.002859, 3,  "清华早期建筑，百年历史",           "attraction"),
    ("同方部",     "清华大学同方部",     116.325289, 40.002669, 3,  "综合楼，设有银行、商店",           "office"),
    ("第三教学楼", "清华大学第三教室楼三段", 116.328622, 40.003077, 6, "主要教学区",                 "teaching"),
    ("第六教学楼", "清华大学第六教学楼A区", 116.330175, 40.002741, 6, "主要教学区",                  "teaching"),
    ("主楼后厅",   "清华大学主楼后厅",   116.332496, 40.002047, 10, "行政主楼区域",                  "office"),
    ("材料学院",   "清华大学材料学院",   116.333914, 39.998506, 5,  "材料科学与工程系",               "teaching"),
    ("机械创新楼", "清华大学机械创新设计实验室", 116.331192, 39.998013, 6, "机械工程系实验楼",         "teaching"),
    ("信息化技术中心", "清华大学信息化技术中心", 116.330575, 39.996925, 5, "信息技术服务楼",            "office"),
    ("化学馆",     "清华大学化工电大楼", 116.335918, 40.003071, 5,  "化工系教学楼",                  "teaching"),
    ("汽车研究所", "清华大学汽车研究所", 116.334496, 40.008451, 4,  "汽车工程研究院",                "teaching"),
    ("学生服务中心", "清华大学学生服务中心", 116.328014, 40.009977, 3, "学生事务办理中心",             "office"),
    ("照澜院",     "清华大学照澜院",     116.324680, 40.000104, 3,  "教职工住宅区",                  "office"),
    ("公共安全研究院", "清华大学公共安全研究院", 116.335338, 40.003825, 6, "公共安全与应急管理研究",    "teaching"),
    ("写作中心",   "清华大学写作与沟通教学中心", 116.332189, 39.998241, 4, "写作与沟通课程楼",          "teaching"),
    ("李兆基科技楼", "李兆基科技大楼公交站", 116.329798, 39.997416, 12, "综合科研大楼",               "teaching"),
    ("清芬园",     "清华大学清芬园",     116.328177, 40.005680, 2,  "休憩庭院区",                   "attraction"),
    ("丁香园",     "清华大学丁香园",     116.327175, 40.008134, 2,  "休憩庭院区",                   "attraction"),
    ("听涛园",     "清华大学听涛园",     116.326997, 40.006353, 2,  "水景休憩庭院",                 "attraction"),
]

FACILITIES = [
    # (name, amap_query, fallback_lng, fallback_lat, fac_type, description)
    ("校医院",       "清华大学医院",         116.318162, 40.002805, "clinic",     "综合校医院，提供医疗保健服务"),
    ("观畴园餐厅",   "清华大学观畴园餐厅",    116.322438, 40.006900, "canteen",    "大型学生食堂"),
    ("紫荆园餐厅",   "清华大学紫荆园餐厅",    116.328676, 40.011629, "canteen",    "北区主要学生食堂"),
    ("桃李园餐厅",   "清华大学桃李园餐厅",    116.326059, 40.010939, "canteen",    "学生食堂"),
    ("西区体育馆",   "清华大学西区体育馆",    116.321251, 40.005045, "sports",     "综合体育馆，含篮球馆"),
    ("北体育馆",     "清华大学北体育馆",      116.332802, 40.007688, "sports",     "北区体育馆"),
    ("游泳馆",       "清华大学游泳馆",        116.331217, 40.007603, "sports",     "室内游泳馆"),
    ("紫荆操场",     "清华大学紫荆操场",      116.329488, 40.009990, "sports",     "田径运动场"),
    ("综合体育中心", "清华大学综合体育中心",  116.332370, 40.004464, "sports",     "综合运动设施中心"),
    ("便利店",       "清华大学易捷便利店",    116.315855, 40.000686, "shop",       "校园便利店"),
    ("停车场（西）", "清华大学停车场",        116.320525, 40.005041, "parking",    "校内停车区"),
    ("学生部",       "清华大学学生部",        116.329325, 39.997175, "office",     "学生事务管理部门"),
]


def resolve_location(amap_query, fallback_lng, fallback_lat):
    """优先查高德，返回 (lng, lat)"""
    pois = search_poi(amap_query)
    if pois:
        loc = pois[0].get("location", "")
        if loc:
            parts = loc.split(",")
            if len(parts) == 2:
                try:
                    return float(parts[0]), float(parts[1])
                except ValueError:
                    pass
    return fallback_lng, fallback_lat


def clear_tsinghua_data(conn):
    c = conn.cursor()
    # 先查出现有所有 road_node ids（用于级联删除 road_edges）
    c.execute("SELECT id FROM road_nodes WHERE spot_id=?", (TSINGHUA_SPOT_ID,))
    node_ids = [r[0] for r in c.fetchall()]
    if node_ids:
        placeholders = ",".join("?" * len(node_ids))
        c.execute(f"DELETE FROM road_edges WHERE from_node_id IN ({placeholders}) OR to_node_id IN ({placeholders})",
                  node_ids + node_ids)
    c.execute("DELETE FROM road_nodes WHERE spot_id=?", (TSINGHUA_SPOT_ID,))
    c.execute("DELETE FROM buildings WHERE spot_id=?", (TSINGHUA_SPOT_ID,))
    c.execute("DELETE FROM facilities WHERE spot_id=?", (TSINGHUA_SPOT_ID,))
    conn.commit()
    print(f"已清除清华大学旧数据")


def insert_buildings(conn, building_rows):
    c = conn.cursor()
    ids = []
    for name, lng, lat, floors, desc, btype in building_rows:
        c.execute(
            "INSERT INTO buildings (spot_id, name, type, location_lng, location_lat, floor_count, description) VALUES (?,?,?,?,?,?,?)",
            (TSINGHUA_SPOT_ID, name, btype, lng, lat, floors, desc)
        )
        ids.append(c.lastrowid)
    conn.commit()
    return ids


def insert_facilities(conn, fac_rows):
    c = conn.cursor()
    ids = []
    for name, lng, lat, ftype, desc in fac_rows:
        c.execute(
            "INSERT INTO facilities (spot_id, name, type, location_lng, location_lat, description) VALUES (?,?,?,?,?,?)",
            (TSINGHUA_SPOT_ID, name, ftype, lng, lat, desc)
        )
        ids.append(c.lastrowid)
    conn.commit()
    return ids


def insert_node(conn, name, lng, lat, node_type, ref_id=None):
    c = conn.cursor()
    c.execute(
        "INSERT INTO road_nodes (spot_id, name, location_lng, location_lat, node_type, ref_id) VALUES (?,?,?,?,?,?)",
        (TSINGHUA_SPOT_ID, name, lng, lat, node_type, ref_id)
    )
    conn.commit()
    return c.lastrowid


def insert_edge(conn, from_id, to_id, distance, duration, road_type="walk", bidirectional=True):
    ideal_speed = {"walk": 1.4, "bike": 4.0, "shuttle": 3.0}[road_type]
    congestion = 1.0
    c = conn.cursor()
    c.execute(
        "INSERT INTO road_edges (spot_id, from_node_id, to_node_id, distance, ideal_speed, congestion_factor, road_type, is_bidirectional) VALUES (?,?,?,?,?,?,?,?)",
        (TSINGHUA_SPOT_ID, from_id, to_id, distance, ideal_speed, congestion, road_type, bidirectional)
    )
    conn.commit()
    return c.lastrowid


def build_intermediate_nodes(conn, from_node_id, to_node_id, poly_points, road_type="walk"):
    """
    把高德返回的折线中间点拆成路口节点写库，并连接成边链
    如果折线超过 2 点，按段插入中间节点；否则直接连接两端
    """
    if len(poly_points) < 2:
        return

    prev_id = from_node_id
    prev_lng, prev_lat = poly_points[0]

    for i, (lng, lat) in enumerate(poly_points[1:], 1):
        dist = haversine(prev_lng, prev_lat, lng, lat)
        if dist < 5:   # 过滤 < 5m 的重复点
            continue

        if i == len(poly_points) - 1:
            cur_id = to_node_id
        else:
            # 中间折点节点
            cur_id = insert_node(conn, f"路口_{from_node_id}_{i}", lng, lat, "crossing")

        insert_edge(conn, prev_id, cur_id, int(dist), int(dist / 1.4), road_type)

        prev_id = cur_id
        prev_lng, prev_lat = lng, lat


def main():
    conn = sqlite3.connect(DB_PATH)
    print(f"数据库：{DB_PATH}")

    clear_tsinghua_data(conn)

    # -------- 1. 采集并写入 buildings / facilities --------
    print("\n[1/4] 采集建筑 POI 坐标...")
    building_rows = []
    for name, query, flng, flat, floors, desc, btype in BUILDINGS:
        lng, lat = resolve_location(query, flng, flat)
        building_rows.append((name, lng, lat, floors, desc, btype))
        print(f"  建筑: {name}  ({lng:.6f}, {lat:.6f})")
        time.sleep(0.15)

    building_ids = insert_buildings(conn, building_rows)
    print(f"  -> 插入 {len(building_ids)} 条 buildings")

    print("\n[2/4] 采集设施 POI 坐标...")
    fac_rows = []
    for name, query, flng, flat, ftype, desc in FACILITIES:
        lng, lat = resolve_location(query, flng, flat)
        fac_rows.append((name, lng, lat, ftype, desc))
        print(f"  设施: {name}  ({lng:.6f}, {lat:.6f})")
        time.sleep(0.15)

    fac_ids = insert_facilities(conn, fac_rows)
    print(f"  -> 插入 {len(fac_ids)} 条 facilities")

    # -------- 2. 写入 road_nodes（入口 + 建筑 + 设施）--------
    print("\n[3/4] 写入道路节点...")

    entrance_node_ids = []
    for name, query, flng, flat in ENTRANCES:
        lng, lat = resolve_location(query, flng, flat)
        nid = insert_node(conn, name, lng, lat, "entrance")
        entrance_node_ids.append((name, nid, lng, lat))
        print(f"  入口: {name} id={nid} ({lng:.6f}, {lat:.6f})")
        time.sleep(0.15)

    building_node_ids = []
    for (name, lng, lat, _, _, _), bid in zip(building_rows, building_ids):
        nid = insert_node(conn, name, lng, lat, "building", ref_id=bid)
        building_node_ids.append((name, nid, lng, lat))

    facility_node_ids = []
    for (name, lng, lat, _, _), fid in zip(fac_rows, fac_ids):
        nid = insert_node(conn, name, lng, lat, "facility", ref_id=fid)
        facility_node_ids.append((name, nid, lng, lat))

    total_nodes = len(entrance_node_ids) + len(building_node_ids) + len(facility_node_ids)
    print(f"  -> 共 {total_nodes} 个锚点节点")

    # -------- 3. 连接道路边（调高德步行接口，折线拆节点）--------
    print("\n[4/4] 构建步行路网（调用高德步行路径接口）...")

    all_anchor_nodes = entrance_node_ids + building_node_ids + facility_node_ids

    # 定义我们想连接的节点对（即校园内合理相邻的路段）
    # 格式：(from_name, to_name)
    # 以名称匹配 all_anchor_nodes 中的记录
    ROUTE_PAIRS = [
        # 入口 -> 核心区
        ("正门（大礼堂南侧）", "大礼堂"),
        ("正门（大礼堂南侧）", "科学馆"),
        ("正门（大礼堂南侧）", "同方部"),
        ("西门",             "校医院"),
        ("西门",             "停车场（西）"),
        ("西门",             "西区体育馆"),
        ("东南门",           "李兆基科技楼"),
        ("东南门",           "照澜院"),
        ("东南门",           "信息化技术中心"),
        ("北门",             "紫荆园餐厅"),
        ("北门",             "桃李园餐厅"),
        ("北门",             "紫荆操场"),
        # 核心区内部
        ("大礼堂",     "图书馆"),
        ("大礼堂",     "科学馆"),
        ("大礼堂",     "同方部"),
        ("大礼堂",     "新清华学堂"),
        ("图书馆",     "观畴园餐厅"),
        ("图书馆",     "听涛园"),
        ("图书馆",     "清芬园"),
        ("图书馆",     "第三教学楼"),
        ("听涛园",     "丁香园"),
        ("丁香园",     "学生服务中心"),
        ("丁香园",     "紫荆园餐厅"),
        ("清芬园",     "第三教学楼"),
        ("清芬园",     "游泳馆"),
        ("第三教学楼", "第六教学楼"),
        ("第三教学楼", "新清华学堂"),
        ("第六教学楼", "主楼后厅"),
        ("第六教学楼", "综合体育中心"),
        ("主楼后厅",   "艺术博物馆"),
        ("主楼后厅",   "材料学院"),
        ("主楼后厅",   "化学馆"),
        ("材料学院",   "公共安全研究院"),
        ("材料学院",   "汽车研究所"),
        ("化学馆",     "公共安全研究院"),
        ("信息化技术中心", "机械创新楼"),
        ("信息化技术中心", "写作中心"),
        ("机械创新楼", "综合体育中心"),
        ("写作中心",   "李兆基科技楼"),
        ("写作中心",   "学生部"),
        ("综合体育中心", "北体育馆"),
        ("综合体育中心", "游泳馆"),
        ("北体育馆",   "紫荆操场"),
        ("游泳馆",     "学生服务中心"),
        ("学生服务中心", "紫荆操场"),
        ("紫荆园餐厅", "桃李园餐厅"),
        ("桃李园餐厅", "学生服务中心"),
        ("科学馆",     "校医院"),
        ("校医院",     "西区体育馆"),
        ("西区体育馆", "观畴园餐厅"),
        ("同方部",     "新清华学堂"),
        ("新清华学堂", "李兆基科技楼"),
        ("照澜院",     "新清华学堂"),
        ("便利店",     "西门"),
        ("便利店",     "校医院"),
        ("停车场（西）", "西区体育馆"),
        ("停车场（西）", "观畴园餐厅"),
        ("汽车研究所", "北体育馆"),
        # 补充跨区联通，减少绕路
        ("正门（大礼堂南侧）", "图书馆"),
        ("正门（大礼堂南侧）", "新清华学堂"),
        ("西门", "观畴园餐厅"),
        ("西门", "图书馆"),
        ("东南门", "写作中心"),
        ("东南门", "机械创新楼"),
        ("北门", "学生服务中心"),
        ("北门", "北体育馆"),
        ("图书馆", "第六教学楼"),
        ("图书馆", "综合体育中心"),
        ("第三教学楼", "主楼后厅"),
        ("第六教学楼", "李兆基科技楼"),
        ("主楼后厅", "综合体育中心"),
        ("综合体育中心", "材料学院"),
        ("综合体育中心", "化学馆"),
        ("学生服务中心", "北体育馆"),
        ("学生服务中心", "桃李园餐厅"),
        ("李兆基科技楼", "机械创新楼"),
        ("李兆基科技楼", "材料学院"),
        ("化学馆", "汽车研究所"),
        ("公共安全研究院", "汽车研究所"),
    ]

    BIKE_ROUTE_PAIRS = [
        ("西门", "校医院"),
        ("校医院", "图书馆"),
        ("图书馆", "第三教学楼"),
        ("第三教学楼", "第六教学楼"),
        ("第六教学楼", "主楼后厅"),
        ("主楼后厅", "综合体育中心"),
        ("综合体育中心", "北体育馆"),
        ("北体育馆", "紫荆操场"),
        ("东南门", "李兆基科技楼"),
        ("李兆基科技楼", "材料学院"),
        ("材料学院", "汽车研究所"),
        ("图书馆", "观畴园餐厅"),
        ("观畴园餐厅", "西区体育馆"),
        ("学生服务中心", "紫荆园餐厅"),
    ]

    SHUTTLE_ROUTE_PAIRS = [
        ("西门", "大礼堂"),
        ("大礼堂", "新清华学堂"),
        ("新清华学堂", "综合体育中心"),
        ("综合体育中心", "材料学院"),
        ("材料学院", "汽车研究所"),
        ("综合体育中心", "北体育馆"),
        ("北体育馆", "北门"),
        ("东南门", "李兆基科技楼"),
        ("李兆基科技楼", "综合体育中心"),
    ]

    name_to_node = {n: (nid, lng, lat) for n, nid, lng, lat in all_anchor_nodes}
    edge_count = 0

    for from_name, to_name in ROUTE_PAIRS:
        fn = name_to_node.get(from_name)
        tn = name_to_node.get(to_name)
        if not fn or not tn:
            print(f"  [跳过] 找不到节点: {from_name} or {to_name}")
            continue

        from_id, flng, flat = fn
        to_id, tlng, tlat = tn

        try:
            result = walking_route((flng, flat), (tlng, tlat))
        except Exception as e:
            print(f"  [失败] {from_name} -> {to_name}: {e}")
            time.sleep(0.3)
            continue

        if not result:
            # 无路径时用直线距离兜底
            dist = int(haversine(flng, flat, tlng, tlat))
            dur = int(dist / 1.4)
            insert_edge(conn, from_id, to_id, dist, dur, "walk")
            edge_count += 1
            print(f"  [直线] {from_name} -> {to_name}  {dist}m")
        else:
            dist, dur, poly = result
            if len(poly) > 2:
                build_intermediate_nodes(conn, from_id, to_id, poly, "walk")
            else:
                insert_edge(conn, from_id, to_id, dist, dur, "walk")
            edge_count += 1
            print(f"  [路网] {from_name} -> {to_name}  {dist}m {dur}s  折点={len(poly)}")

        time.sleep(0.2)

    def add_direct_mode_edges(pairs, road_type, speed):
        added = 0
        for from_name, to_name in pairs:
            fn = name_to_node.get(from_name)
            tn = name_to_node.get(to_name)
            if not fn or not tn:
                continue
            from_id, flng, flat = fn
            to_id, tlng, tlat = tn
            dist = int(haversine(flng, flat, tlng, tlat))
            duration = int(dist / speed)
            insert_edge(conn, from_id, to_id, dist, duration, road_type)
            added += 1
        print(f"  -> 新增 {road_type} 边 {added} 条")

    print("\n[4.1/4] 补充骑行主路...")
    add_direct_mode_edges(BIKE_ROUTE_PAIRS, "bike", 4.0)

    print("\n[4.2/4] 补充接驳车主路...")
    add_direct_mode_edges(SHUTTLE_ROUTE_PAIRS, "shuttle", 3.0)

    # 统计
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM road_nodes WHERE spot_id=?", (TSINGHUA_SPOT_ID,))
    node_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM road_edges WHERE spot_id=?", (TSINGHUA_SPOT_ID,))
    db_edge_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM buildings WHERE spot_id=?", (TSINGHUA_SPOT_ID,))
    bcount = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM facilities WHERE spot_id=?", (TSINGHUA_SPOT_ID,))
    fcount = cur.fetchone()[0]

    conn.close()
    print(f"""
=== 清华大学地图数据初始化完成 ===
建筑 (buildings):  {bcount}
设施 (facilities): {fcount}
路网节点 (road_nodes): {node_count}
路网边 (road_edges):   {db_edge_count}
""")


if __name__ == "__main__":
    main()
