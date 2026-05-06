"""
北京邮电大学本部内部导航测试数据初始化脚本

策略：
- 仅优先使用高德可验证的海淀校区 POI 作为建筑/设施锚点
- 对返回结果做校区范围与语义过滤
- 不再为不可靠设施写入手工估点
- 只写入高德步行路径返回的真实折线边，不再回退为直线连接
"""
import os
import json
import time
import math
import sqlite3
import urllib.request
import urllib.parse
import ssl
import urllib.error
import socket

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "travel.db")
AMAP_KEY = os.getenv("AMAP_WEB_SERVICE_KEY", "5373684f183274b8b2834f1474a929f4")

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

SPOT_NAME = "北京邮电大学（本部）"
SPOT_CITY = "北京"
SPOT_CATEGORY = "文化教育"
SPOT_TYPE = "campus"
SPOT_ADDRESS = "北京市海淀区西土城路10号"
SPOT_DESCRIPTION = "北京邮电大学本部校园内部导航测试数据，优先采用高德海淀校区 POI 和步行折线构建。"
SPOT_TAGS = '["学府", "校园", "导航测试"]'

CAMPUS_CENTER = (116.358104, 39.961554)
CAMPUS_MAX_DISTANCE_M = 900
CAMPUS_TEXT_TOKENS = ["北京邮电大学", "北邮", "海淀校区", "西土城路10号"]

ENTRANCES = [
    {"name": "西门", "query": None, "fallback": (116.355180, 39.961040), "accept": ["西门"]},
    {"name": "南门", "query": None, "fallback": (116.358520, 39.958060), "accept": ["南门"]},
    {"name": "东门", "query": None, "fallback": (116.360920, 39.961930), "accept": ["东门"]},
    {"name": "北门", "query": None, "fallback": (116.356860, 39.964990), "accept": ["北门"]},
]

BUILDINGS = [
    {"name": "主楼", "query": "北京邮电大学海淀校区主楼", "source": "text", "accept": ["主楼"], "floor_count": 6, "type": "teaching", "description": "校园核心教学楼，室内导航样例楼。"},
    {"name": "教一楼", "query": "北京邮电大学海淀校区教一楼", "source": "text", "accept": ["教一楼", "教1楼"], "floor_count": 5, "type": "teaching", "description": "本科教学楼。"},
    {"name": "教二楼", "query": "北京邮电大学海淀校区教二楼", "source": "text", "accept": ["教二楼", "教2楼"], "floor_count": 5, "type": "teaching", "description": "本科教学楼。"},
    {"name": "图书馆", "query": "北京邮电大学海淀校区图书馆", "source": "text", "accept": ["图书馆"], "fallback": (116.357811, 39.962780), "floor_count": 6, "type": "attraction", "description": "校园图书馆。"},
    {"name": "科研楼", "query": "北京邮电大学海淀校区研究生院", "source": "text", "accept": ["研究生院", "科研"], "fallback": (116.357977, 39.961872), "floor_count": 6, "type": "office", "description": "科研与实验办公楼。"},
    {"name": "综合实验楼", "query": "北京邮电大学海淀校区教三楼", "source": "text", "accept": ["教三楼", "计算机科学", "光信息"], "fallback": (116.356244, 39.960464), "floor_count": 6, "type": "office", "description": "实验教学与科研楼。"},
    {"name": "学生活动中心", "query": "北京邮电大学海淀校区学生活动中心", "source": "text", "accept": ["学生活动中心"], "fallback": (116.357355, 39.964001), "floor_count": 4, "type": "office", "description": "社团活动与报告厅。"},
    {"name": "学生发展中心", "query": "北京邮电大学海淀校区学生发展中心", "source": "text", "accept": ["学生发展中心"], "fallback": (116.357830, 39.963428), "floor_count": 4, "type": "office", "description": "学生事务与服务大厅。"},
    {"name": "体育馆", "query": "北京邮电大学海淀校区体育馆", "source": "text", "accept": ["体育馆"], "fallback": (116.359571, 39.962011), "floor_count": 3, "type": "attraction", "description": "综合体育馆。"},
    {"name": "运动场", "query": "北京邮电大学海淀校区体育场", "source": "text", "accept": ["体育场", "运动场"], "fallback": (116.360235, 39.960652), "floor_count": 1, "type": "attraction", "description": "校园操场与室外运动区。"},
    {"name": "科学会堂", "query": "北京邮电大学海淀校区科学会堂", "source": "text", "accept": ["科学会堂"], "fallback": (116.359073, 39.961265), "floor_count": 3, "type": "attraction", "description": "会议与报告活动场所。"},
    {"name": "游泳馆", "query": "北京邮电大学海淀校区游泳馆", "source": "text", "accept": ["游泳馆"], "fallback": (116.360698, 39.961875), "floor_count": 2, "type": "attraction", "description": "校内游泳馆。"},
    {"name": "青年教师公寓", "query": "北京邮电大学海淀校区青年教师公寓", "source": "text", "accept": ["青年教师公寓"], "fallback": (116.359986, 39.964615), "floor_count": 12, "type": "dorm", "description": "北邮校内公寓楼。"},
    {"name": "行政楼", "query": "北京邮电大学行政楼", "source": "around", "accept": ["行政楼"], "fallback": (116.357940, 39.962097), "floor_count": 5, "type": "office", "description": "学校行政办公楼。"},
    {"name": "信通楼", "query": "教学楼", "source": "around", "accept": ["信通楼"], "floor_count": 5, "type": "teaching", "description": "信息通信相关教学楼。"},
    {"name": "电子工程学院", "query": "北京邮电大学海淀校区电子工程学院", "source": "text", "accept": ["电子工程学院"], "floor_count": 6, "type": "teaching", "description": "电子工程学院教学科研楼。"},
    {"name": "人文学院", "query": "北京邮电大学海淀校区人文学院", "source": "text", "accept": ["人文学院"], "floor_count": 5, "type": "teaching", "description": "人文学院教学楼。"},
    {"name": "数字媒体与设计艺术学院", "query": "北京邮电大学海淀校区数字媒体与设计艺术学院", "source": "around", "accept": ["数字媒体与设计艺术学院"], "floor_count": 5, "type": "teaching", "description": "数字媒体与设计艺术学院教学楼。"},
    {"name": "网络技术研究院", "query": "北京邮电大学海淀校区网络技术研究院", "source": "text", "accept": ["网络技术研究院"], "floor_count": 5, "type": "office", "description": "网络技术科研机构。"},
    {"name": "网络空间安全学院", "query": "北京邮电大学海淀校区网络空间安全学院", "source": "text", "accept": ["网络空间安全学院"], "fallback": (116.357982, 39.961866), "floor_count": 5, "type": "teaching", "description": "网络空间安全学院教学科研楼。"},
    {"name": "时光广场", "query": "北京邮电大学海淀校区时光广场", "source": "text", "accept": ["时光广场"], "fallback": (116.357399, 39.962373), "floor_count": 1, "type": "attraction", "description": "校园中心广场。"},
    {"name": "北家属区", "query": "宿舍", "source": "around", "accept": ["北京邮电大学社区北家属区"], "floor_count": 10, "type": "dorm", "description": "北邮北侧宿舍与家属区。"},
    {"name": "学生会", "query": "北京邮电大学海淀校区学生会", "source": "text", "accept": ["学生会"], "floor_count": 2, "type": "office", "description": "学生组织活动点。"},
    {"name": "学生勤工助学中心", "query": "北京邮电大学学生勤工助学中心", "source": "text", "accept": ["学生勤工助学中心"], "floor_count": 2, "type": "office", "description": "学生事务服务点。"},
    {"name": "体育部", "query": "北京邮电大学海淀校区体育部", "source": "text", "accept": ["体育部"], "floor_count": 2, "type": "office", "description": "体育教学与管理办公点。"},
    {"name": "明光楼", "query": "北京邮电大学海淀校区明光楼", "source": "text", "accept": ["明光楼"], "fallback": (116.360987, 39.958568), "floor_count": 6, "type": "teaching", "description": "校园南侧楼宇。"},
    {"name": "马克思主义学院", "query": "北京邮电大学海淀校区马克思主义学院", "source": "text", "accept": ["马克思主义学院"], "fallback": (116.361105, 39.958384), "floor_count": 5, "type": "teaching", "description": "学院教学办公楼。"},
    {"name": "现代邮政学院", "query": "北京邮电大学海淀校区现代邮政学院", "source": "text", "accept": ["现代邮政学院"], "fallback": (116.356240, 39.960464), "floor_count": 5, "type": "teaching", "description": "学院教学楼。"},
    {"name": "信息与通信工程学院", "query": "北京邮电大学海淀校区信息与通信工程学院", "source": "text", "accept": ["信息与通信工程学院"], "fallback": (116.358034, 39.960532), "floor_count": 5, "type": "teaching", "description": "信息与通信工程学院楼。"},
    {"name": "保卫处", "query": "北京邮电大学海淀校区保卫处", "source": "text", "accept": ["保卫处"], "fallback": (116.360713, 39.963256), "floor_count": 2, "type": "office", "description": "校内安保管理办公点。"},
    {"name": "热力中心", "query": "北京邮电大学海淀校区热力中心", "source": "text", "accept": ["热力中心"], "fallback": (116.358404, 39.964192), "floor_count": 2, "type": "office", "description": "校园后勤能源服务点。"},
    {"name": "学生工作基地", "query": "北京邮电大学海淀校区学生工作基地", "source": "text", "accept": ["学生工作基地"], "fallback": (116.356586, 39.962814), "floor_count": 2, "type": "office", "description": "学生事务与辅导支持点。"},
]

FACILITIES = [
    {"name": "学一食堂", "query": "学生食堂", "source": "around", "accept": ["学生食堂"], "type": "canteen", "description": "主食堂。", "require_campus": True},
    {"name": "学五食堂", "query": "综合食堂", "source": "around", "accept": ["综合食堂"], "type": "canteen", "description": "宿舍区附近食堂。", "require_campus": True},
    {"name": "校园超市", "query": "超市", "source": "around", "accept": ["邮电大学店", "北京邮电大学店"], "type": "supermarket", "description": "生活服务超市。", "require_campus": True},
    {"name": "麦当劳（校内）", "query": "麦当劳", "source": "around", "accept": ["北京邮电大学"], "type": "shop", "description": "校园内餐饮点。", "require_campus": True},
    {"name": "医务室", "query": "北京邮电大学海淀校区社区卫生服务中心", "source": "text", "accept": ["卫生服务中心", "校医院"], "type": "clinic", "description": "校园基础医疗服务。", "require_campus": True},
    {"name": "发热门诊", "query": "北京邮电大学社区卫生服务中心发热门诊", "source": "text", "accept": ["发热门诊"], "type": "clinic", "description": "校内门诊服务点。", "require_campus": True},
    {"name": "瑞幸咖啡", "query": "咖啡", "source": "around", "accept": ["北京邮电大学店"], "type": "cafe", "description": "校内咖啡点。", "require_campus": True},
    {"name": "邮储ATM", "query": "ATM", "source": "around", "accept": ["邮电大学支行"], "fallback": (116.355443, 39.961977), "type": "bank", "description": "校内自助取款点。", "require_campus": True},
    {"name": "快递站", "query": "快递", "source": "around", "accept": ["北京邮电大学快递邮驿站"], "type": "express", "description": "校内快递收发点。", "require_campus": True},
    {"name": "篮球场", "query": "篮球场", "source": "around", "accept": ["北京邮电大学海淀校区篮球场"], "type": "sports", "description": "校内篮球场。", "require_campus": True},
    {"name": "排球场", "query": "排球场", "source": "around", "accept": ["北京邮电大学海淀校区排球场"], "fallback": (116.360007, 39.962575), "type": "sports", "description": "校内排球场。", "require_campus": True},
    {"name": "好邻居便利店", "query": "便利店", "source": "around", "accept": ["海淀校区北京邮电大学店"], "fallback": (116.356618, 39.959250), "type": "supermarket", "description": "校园便利店。", "require_campus": True},
    {"name": "物美多点便利店", "query": "北京邮电大学海淀校区物美多点便利店", "source": "text", "accept": ["物美多点便利店", "邮电大学店"], "type": "supermarket", "description": "校内北侧便利店。", "require_campus": True},
    {"name": "沪咖鲜果咖啡", "query": "咖啡", "source": "around", "accept": ["邮电大学店"], "fallback": (116.357176, 39.960004), "type": "cafe", "description": "校园南侧咖啡点。", "require_campus": True},
    {"name": "民族餐厅", "query": "餐厅", "source": "around", "accept": ["北邮民族餐厅"], "type": "restaurant", "description": "综合餐厅楼内餐饮点。", "require_campus": True},
    {"name": "楼上楼茶餐厅", "query": "餐厅", "source": "around", "accept": ["楼上楼茶餐厅"], "type": "restaurant", "description": "学生餐厅楼内餐饮点。", "require_campus": True},
    {"name": "教工餐厅", "query": "北京邮电大学海淀校区教工餐厅", "source": "text", "accept": ["教工餐厅"], "type": "restaurant", "description": "校内教工餐厅。", "require_campus": True},
]

ROUTE_PAIRS = [
    ("西门", "主楼"),
    ("西门", "教一楼"),
    ("西门", "医务室"),
    ("西门", "发热门诊"),
    ("西门", "综合实验楼"),
    ("西门", "好邻居便利店"),
    ("西门", "邮储ATM"),
    ("西门", "信通楼"),
    ("西门", "行政楼"),
    ("南门", "学一食堂"),
    ("南门", "学生发展中心"),
    ("南门", "沪咖鲜果咖啡"),
    ("南门", "民族餐厅"),
    ("南门", "教工餐厅"),
    ("南门", "医务室"),
    ("南门", "学生工作基地"),
    ("南门", "马克思主义学院"),
    ("南门", "明光楼"),
    ("东门", "体育馆"),
    ("东门", "游泳馆"),
    ("东门", "科学会堂"),
    ("东门", "排球场"),
    ("东门", "篮球场"),
    ("东门", "保卫处"),
    ("东门", "时光广场"),
    ("东门", "明光楼"),
    ("北门", "学生活动中心"),
    ("北门", "图书馆"),
    ("北门", "青年教师公寓"),
    ("北门", "快递站"),
    ("北门", "北家属区"),
    ("北门", "物美多点便利店"),
    ("北门", "热力中心"),
    ("北门", "学生发展中心"),
    ("主楼", "教二楼"),
    ("主楼", "图书馆"),
    ("主楼", "综合实验楼"),
    ("主楼", "学一食堂"),
    ("主楼", "学生发展中心"),
    ("主楼", "科学会堂"),
    ("主楼", "邮储ATM"),
    ("主楼", "行政楼"),
    ("主楼", "信通楼"),
    ("主楼", "电子工程学院"),
    ("主楼", "人文学院"),
    ("主楼", "数字媒体与设计艺术学院"),
    ("主楼", "时光广场"),
    ("主楼", "学生勤工助学中心"),
    ("主楼", "学生工作基地"),
    ("主楼", "信息与通信工程学院"),
    ("主楼", "网络空间安全学院"),
    ("主楼", "体育馆"),
    ("教二楼", "科研楼"),
    ("教二楼", "信通楼"),
    ("教二楼", "现代邮政学院"),
    ("科研楼", "图书馆"),
    ("科研楼", "学生发展中心"),
    ("科研楼", "网络技术研究院"),
    ("综合实验楼", "电子工程学院"),
    ("综合实验楼", "数字媒体与设计艺术学院"),
    ("综合实验楼", "人文学院"),
    ("综合实验楼", "现代邮政学院"),
    ("综合实验楼", "学生会"),
    ("综合实验楼", "学生工作基地"),
    ("综合实验楼", "发热门诊"),
    ("学生活动中心", "学生发展中心"),
    ("学生活动中心", "学五食堂"),
    ("学生活动中心", "时光广场"),
    ("学生活动中心", "青年教师公寓"),
    ("学生活动中心", "学生会"),
    ("学生活动中心", "快递站"),
    ("学生活动中心", "热力中心"),
    ("学生活动中心", "物美多点便利店"),
    ("学生活动中心", "图书馆"),
    ("学五食堂", "校园超市"),
    ("学五食堂", "麦当劳（校内）"),
    ("学五食堂", "瑞幸咖啡"),
    ("学五食堂", "楼上楼茶餐厅"),
    ("学五食堂", "教工餐厅"),
    ("学五食堂", "物美多点便利店"),
    ("学五食堂", "学生活动中心"),
    ("体育馆", "运动场"),
    ("体育馆", "游泳馆"),
    ("体育馆", "篮球场"),
    ("体育馆", "排球场"),
    ("体育馆", "体育部"),
    ("体育馆", "保卫处"),
    ("体育馆", "科学会堂"),
    ("科学会堂", "图书馆"),
    ("科学会堂", "时光广场"),
    ("科学会堂", "保卫处"),
    ("校园超市", "麦当劳（校内）"),
    ("校园超市", "瑞幸咖啡"),
    ("校园超市", "楼上楼茶餐厅"),
    ("校园超市", "教工餐厅"),
    ("校园超市", "学一食堂"),
    ("瑞幸咖啡", "快递站"),
    ("瑞幸咖啡", "时光广场"),
    ("瑞幸咖啡", "学生会"),
    ("青年教师公寓", "北家属区"),
    ("青年教师公寓", "物美多点便利店"),
    ("青年教师公寓", "快递站"),
    ("北家属区", "物美多点便利店"),
    ("北家属区", "快递站"),
    ("明光楼", "马克思主义学院"),
    ("明光楼", "沪咖鲜果咖啡"),
    ("明光楼", "好邻居便利店"),
    ("明光楼", "保卫处"),
    ("学生勤工助学中心", "学生会"),
    ("学生勤工助学中心", "时光广场"),
    ("学生勤工助学中心", "学生工作基地"),
    ("学生会", "快递站"),
    ("学生会", "物美多点便利店"),
    ("学生会", "学生发展中心"),
    ("现代邮政学院", "信息与通信工程学院"),
    ("信息与通信工程学院", "信通楼"),
    ("网络空间安全学院", "信通楼"),
    ("保卫处", "热力中心"),
    ("医务室", "发热门诊"),
]


def amap_get(url, params):
    full_url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full_url)
    last_error = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=25) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            last_error = exc
            if attempt == 4:
                raise
            time.sleep(0.8 * (attempt + 1))
    raise last_error


def search_poi(keyword, city="北京", limit=8):
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


def around_poi(keyword, limit=8):
    data = amap_get("https://restapi.amap.com/v3/place/around", {
        "key": AMAP_KEY,
        "location": f"{CAMPUS_CENTER[0]},{CAMPUS_CENTER[1]}",
        "keywords": keyword,
        "radius": 1000,
        "sortrule": "distance",
        "offset": limit,
        "output": "json",
    })
    if data.get("status") == "1" and data.get("pois"):
        return data["pois"]
    return []


def geocode_address(address, city="北京"):
    data = amap_get("https://restapi.amap.com/v3/geocode/geo", {
        "key": AMAP_KEY,
        "address": address,
        "city": city,
        "output": "json",
    })
    if data.get("status") == "1" and data.get("geocodes"):
        return data["geocodes"]
    return []


def haversine(lng1, lat1, lng2, lat2):
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlng / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def is_candidate_valid(poi, accept_tokens, require_campus=False):
    loc = poi.get("location", "")
    if not loc:
        return False
    try:
        lng, lat = map(float, loc.split(","))
    except Exception:
        return False
    if haversine(CAMPUS_CENTER[0], CAMPUS_CENTER[1], lng, lat) > CAMPUS_MAX_DISTANCE_M:
        return False
    text = f"{poi.get('name', '')} {poi.get('address', '')}"
    if require_campus and not any(token in text for token in CAMPUS_TEXT_TOKENS):
        return False
    return any(token in text for token in accept_tokens)


def resolve_location(spec):
    if not spec.get("query"):
        return spec.get("fallback")
    require_campus = spec.get("require_campus", False)
    if spec.get("source") == "around":
        pois = around_poi(spec["query"])
        valid = [poi for poi in pois if is_candidate_valid(poi, spec["accept"], require_campus=require_campus)]
        if not valid:
            return spec.get("fallback")
        lng, lat = map(float, valid[0]["location"].split(","))
        return lng, lat
    if spec.get("source") == "geo":
        geocodes = geocode_address(spec["query"])
        for geo in geocodes:
            loc = geo.get("location", "")
            try:
                lng, lat = map(float, loc.split(","))
            except Exception:
                continue
            if haversine(CAMPUS_CENTER[0], CAMPUS_CENTER[1], lng, lat) <= CAMPUS_MAX_DISTANCE_M:
                return lng, lat
        return spec.get("fallback")
    pois = search_poi(spec["query"])
    valid = [poi for poi in pois if is_candidate_valid(poi, spec["accept"], require_campus=require_campus)]
    if not valid:
        return spec.get("fallback")
    lng, lat = map(float, valid[0]["location"].split(","))
    return lng, lat


def walking_route(origin, dest):
    try:
        data = amap_get("https://restapi.amap.com/v3/direction/walking", {
            "key": AMAP_KEY,
            "origin": f"{origin[0]},{origin[1]}",
            "destination": f"{dest[0]},{dest[1]}",
            "output": "json",
        })
    except Exception:
        return None
    if data.get("status") != "1":
        return None
    paths = data.get("route", {}).get("paths", [])
    if not paths:
        return None
    points = []
    for step in paths[0].get("steps", []):
        for pt in step.get("polyline", "").split(";"):
            parts = pt.strip().split(",")
            if len(parts) == 2:
                points.append((float(parts[0]), float(parts[1])))
    return points if len(points) >= 2 else None


def ensure_spot(conn):
    c = conn.cursor()
    c.execute("SELECT id FROM scenic_spots WHERE name=? AND city=?", (SPOT_NAME, SPOT_CITY))
    row = c.fetchone()
    if row:
        c.execute(
            "UPDATE scenic_spots SET category=?, type=?, address=?, description=?, tags=?, location_lng=?, location_lat=? WHERE id=?",
            (SPOT_CATEGORY, SPOT_TYPE, SPOT_ADDRESS, SPOT_DESCRIPTION, SPOT_TAGS, CAMPUS_CENTER[0], CAMPUS_CENTER[1], row[0]),
        )
        conn.commit()
        return row[0]
    c.execute(
        """
        INSERT INTO scenic_spots
        (name, description, location_lat, location_lng, address, city, category, type, rating, heat_score, review_count, favorites_count, open_time, ticket_price, need_booking, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            SPOT_NAME,
            SPOT_DESCRIPTION,
            CAMPUS_CENTER[1],
            CAMPUS_CENTER[0],
            SPOT_ADDRESS,
            SPOT_CITY,
            SPOT_CATEGORY,
            SPOT_TYPE,
            4.8,
            8600,
            0,
            0,
            "全天开放",
            "免费",
            0,
            SPOT_TAGS,
        ),
    )
    conn.commit()
    return c.lastrowid


def clear_existing_map(conn, spot_id):
    c = conn.cursor()
    c.execute("SELECT id FROM road_nodes WHERE spot_id=?", (spot_id,))
    node_ids = [r[0] for r in c.fetchall()]
    if node_ids:
        placeholders = ",".join("?" for _ in node_ids)
        c.execute(f"DELETE FROM road_edges WHERE from_node_id IN ({placeholders}) OR to_node_id IN ({placeholders})", node_ids + node_ids)
    c.execute("DELETE FROM road_nodes WHERE spot_id=?", (spot_id,))
    c.execute("DELETE FROM buildings WHERE spot_id=?", (spot_id,))
    c.execute("DELETE FROM facilities WHERE spot_id=?", (spot_id,))
    conn.commit()


def insert_building(conn, spot_id, spec, lng, lat):
    c = conn.cursor()
    c.execute(
        "INSERT INTO buildings (spot_id, name, type, location_lng, location_lat, floor_count, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (spot_id, spec["name"], spec["type"], lng, lat, spec["floor_count"], spec["description"]),
    )
    conn.commit()
    return c.lastrowid


def insert_facility(conn, spot_id, spec, lng, lat):
    c = conn.cursor()
    c.execute(
        "INSERT INTO facilities (spot_id, name, type, location_lng, location_lat, description) VALUES (?, ?, ?, ?, ?, ?)",
        (spot_id, spec["name"], spec["type"], lng, lat, spec["description"]),
    )
    conn.commit()
    return c.lastrowid


def insert_node(conn, spot_id, name, lng, lat, node_type, ref_id=None):
    c = conn.cursor()
    c.execute(
        "INSERT INTO road_nodes (spot_id, name, location_lng, location_lat, node_type, ref_id) VALUES (?, ?, ?, ?, ?, ?)",
        (spot_id, name, lng, lat, node_type, ref_id),
    )
    conn.commit()
    return c.lastrowid


def insert_edge(conn, spot_id, from_id, to_id, distance):
    c = conn.cursor()
    c.execute(
        "INSERT INTO road_edges (spot_id, from_node_id, to_node_id, distance, ideal_speed, congestion_factor, road_type, is_bidirectional) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (spot_id, from_id, to_id, distance, 1.4, 0.9, "walk", 1),
    )
    c.execute(
        "INSERT INTO road_edges (spot_id, from_node_id, to_node_id, distance, ideal_speed, congestion_factor, road_type, is_bidirectional) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (spot_id, from_id, to_id, distance, 4.2, 0.85, "bike", 1),
    )
    conn.commit()


def build_intermediate_nodes(conn, spot_id, from_node_id, to_node_id, points, created_crossings):
    prev_id = from_node_id
    prev_lng, prev_lat = points[0]
    for i, (lng, lat) in enumerate(points[1:], 1):
        dist = haversine(prev_lng, prev_lat, lng, lat)
        if dist < 5:
            continue
        if i == len(points) - 1:
            cur_id = to_node_id
        else:
            key = (round(lng, 6), round(lat, 6))
            cur_id = created_crossings.get(key)
            if not cur_id:
                cur_id = insert_node(conn, spot_id, f"路口_{len(created_crossings)+1}", lng, lat, "crossing")
                created_crossings[key] = cur_id
        insert_edge(conn, spot_id, prev_id, cur_id, int(dist))
        prev_id = cur_id
        prev_lng, prev_lat = lng, lat


def main():
    conn = sqlite3.connect(DB_PATH)
    spot_id = ensure_spot(conn)
    clear_existing_map(conn, spot_id)

    anchors = {}

    for spec in ENTRANCES:
        point = resolve_location(spec)
        if not point:
            continue
        lng, lat = point
        node_id = insert_node(conn, spot_id, spec["name"], lng, lat, "entrance")
        anchors[spec["name"]] = {"id": node_id, "lng": lng, "lat": lat}
        print(f"入口: {spec['name']} -> ({lng:.6f}, {lat:.6f})")

    for spec in BUILDINGS:
        point = resolve_location(spec)
        if not point:
            print(f"跳过建筑: {spec['name']}")
            continue
        lng, lat = point
        ref_id = insert_building(conn, spot_id, spec, lng, lat)
        node_id = insert_node(conn, spot_id, spec["name"], lng, lat, "building", ref_id)
        anchors[spec["name"]] = {"id": node_id, "lng": lng, "lat": lat}
        print(f"建筑: {spec['name']} -> ({lng:.6f}, {lat:.6f})")
        time.sleep(0.05)

    for spec in FACILITIES:
        point = resolve_location(spec)
        if not point:
            print(f"跳过设施: {spec['name']}")
            continue
        lng, lat = point
        ref_id = insert_facility(conn, spot_id, spec, lng, lat)
        node_id = insert_node(conn, spot_id, spec["name"], lng, lat, "facility", ref_id)
        anchors[spec["name"]] = {"id": node_id, "lng": lng, "lat": lat}
        print(f"设施: {spec['name']} -> ({lng:.6f}, {lat:.6f})")
        time.sleep(0.05)

    created_crossings = {}
    for from_name, to_name in ROUTE_PAIRS:
        if from_name not in anchors or to_name not in anchors:
            continue
        origin = anchors[from_name]
        dest = anchors[to_name]
        points = walking_route((origin["lng"], origin["lat"]), (dest["lng"], dest["lat"]))
        if not points:
            print(f"跳过无折线路径: {from_name} -> {to_name}")
            continue
        points[0] = (origin["lng"], origin["lat"])
        points[-1] = (dest["lng"], dest["lat"])
        build_intermediate_nodes(conn, spot_id, origin["id"], dest["id"], points, created_crossings)
        print(f"路径: {from_name} -> {to_name}, 折点={max(len(points)-2, 0)}")
        time.sleep(0.05)

    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM buildings WHERE spot_id=?", (spot_id,))
    print('buildings', c.fetchone()[0])
    c.execute("SELECT COUNT(*) FROM facilities WHERE spot_id=?", (spot_id,))
    print('facilities', c.fetchone()[0])
    c.execute("SELECT COUNT(*) FROM road_nodes WHERE spot_id=? AND node_type='crossing'", (spot_id,))
    print('crossings', c.fetchone()[0])
    c.execute("SELECT COUNT(*) FROM road_edges WHERE spot_id=?", (spot_id,))
    print('edges', c.fetchone()[0])
    conn.close()


if __name__ == "__main__":
    main()
