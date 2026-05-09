"""
北京邮电大学本部内部导航数据初始化脚本

数据来源：仓库根目录 export.geojson（Overpass Turbo 导出）
输出：
- backend/data/map_data.json
- backend/data/poi_data.json

处理流程：
1. 提取北邮校园范围内的路网与 POI（WGS84）
2. 构建路网节点/边，并为建筑、设施、入口生成锚点节点
3. 通过高德坐标转换 API 批量转为 GCJ-02
4. 写入 JSON 并重建数据库中的北邮内部导航数据
"""
import json
import math
import os
import sqlite3
import ssl
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / "data"
DB_PATH = DATA_DIR / "travel.db"
EXPORT_GEOJSON_PATH = PROJECT_ROOT / "export.geojson"
MAP_DATA_PATH = DATA_DIR / "map_data.json"
POI_DATA_PATH = DATA_DIR / "poi_data.json"

AMAP_KEY = os.getenv("AMAP_WEB_SERVICE_KEY", "5373684f183274b8b2834f1474a929f4")

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

SPOT_NAME = "北京邮电大学（本部）"
SPOT_CITY = "北京"
SPOT_CATEGORY = "文化教育"
SPOT_TYPE = "campus"
SPOT_ADDRESS = "北京市海淀区西土城路10号"
SPOT_DESCRIPTION = "北京邮电大学本部校园内部导航数据，基于 OSM 导出的路网与设施数据构建。"
SPOT_TAGS = '["学府", "校园", "OSM路网"]'


ALLOWED_HIGHWAYS = {
    "footway",
    "service",
    "path",
    "pedestrian",
    "steps",
    "residential",
    "living_street",
    "cycleway",
}

ROAD_TYPE_CONFIG = {
    "walk": {"ideal_speed": 1.4, "congestion_factor": 0.95},
    "bike": {"ideal_speed": 4.8, "congestion_factor": 0.88},
}

FACILITY_DESCRIPTIONS = {
    "canteen": "校内食堂",
    "restaurant": "校内餐饮点",
    "cafe": "校内咖啡点",
    "clinic": "校内医疗服务点",
    "toilet": "校内卫生间",
    "supermarket": "校内商超便利点",
    "shop": "校内商店",
    "express": "校内快递服务点",
    "bank": "校内金融服务点",
    "sports": "校内运动设施",
    "parking": "校内停车设施",
    "library": "校内图书服务点",
}

NAME_ALIASES = {
    "北邮体育馆": "体育馆",
    "综合食堂(新食堂)": "学五食堂",
    "综合食堂": "学五食堂",
    "学苑风味餐厅(矮食堂)": "学一食堂",
    "校医院（北京邮电大学社区卫生服务中心）": "医务室",
    "行政办公楼": "行政楼",
}

EXCLUDED_NAME_TOKENS = ["北京交通大学", "北京师范大学", "北师大"]


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


def haversine(lng1, lat1, lng2, lat2):
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlng / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def out_of_china(lng, lat):
    return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)


def transform_lat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
    return ret


def transform_lng(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
    return ret


def wgs84_to_gcj02(lng, lat):
    if out_of_china(lng, lat):
        return lng, lat
    a = 6378245.0
    ee = 0.00669342162296594323
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * math.pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * math.pi)
    return lng + dlng, lat + dlat


def point_key(lng, lat, precision=7):
    return f"{round(lng, precision):.{precision}f},{round(lat, precision):.{precision}f}"


def get_feature_name(props):
    for key in ("name:zh", "name", "loc_name", "official_name", "brand:zh", "brand"):
        value = props.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def geometry_rank(geometry_type):
    return {"Polygon": 3, "MultiPolygon": 3, "Point": 2, "LineString": 1}.get(geometry_type, 0)


def get_polygon_shell(geometry):
    if geometry["type"] == "Polygon":
        return geometry["coordinates"][0]
    if geometry["type"] == "MultiPolygon":
        polygons = [poly[0] for poly in geometry["coordinates"] if poly and poly[0]]
        if not polygons:
            return []
        return max(polygons, key=polygon_area_estimate)
    return []


def polygon_area_estimate(coords):
    if len(coords) < 3:
        return 0.0
    area = 0.0
    for i in range(len(coords) - 1):
        x1, y1 = coords[i]
        x2, y2 = coords[i + 1]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def polygon_centroid(coords):
    points = coords[:-1] if len(coords) > 1 and coords[0] == coords[-1] else coords
    if not points:
        return 0.0, 0.0
    lng = sum(pt[0] for pt in points) / len(points)
    lat = sum(pt[1] for pt in points) / len(points)
    return lng, lat


def representative_point(feature):
    geometry = feature.get("geometry") or {}
    gtype = geometry.get("type")
    if gtype == "Point":
        lng, lat = geometry["coordinates"]
        return lng, lat
    if gtype == "LineString":
        coords = geometry["coordinates"]
        if not coords:
            return None
        mid = len(coords) // 2
        lng, lat = coords[mid]
        return lng, lat
    if gtype in {"Polygon", "MultiPolygon"}:
        shell = get_polygon_shell(geometry)
        if not shell:
            return None
        return polygon_centroid(shell)
    return None


def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    n = len(polygon)
    if n < 3:
        return False
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        if ((y1 > y) != (y2 > y)):
            cross = (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-12) + x1
            if x < cross:
                inside = not inside
    return inside


def polygon_bounds(polygon):
    lngs = [pt[0] for pt in polygon]
    lats = [pt[1] for pt in polygon]
    return min(lngs), min(lats), max(lngs), max(lats)


def point_in_campus(point, campus_polygon, campus_bounds):
    lng, lat = point
    min_lng, min_lat, max_lng, max_lat = campus_bounds
    if lng < min_lng or lng > max_lng or lat < min_lat or lat > max_lat:
        return False
    return point_in_polygon(point, campus_polygon)


def clip_linestring_to_campus(coords, campus_polygon, campus_bounds):
    segments = []
    current = []
    for lng, lat in coords:
        pt = (lng, lat)
        if point_in_campus(pt, campus_polygon, campus_bounds):
            if not current or current[-1] != pt:
                current.append(pt)
        else:
            if len(current) >= 2:
                segments.append(current)
            current = []
    if len(current) >= 2:
        segments.append(current)
    return segments


def road_types_for_highway(highway):
    if highway == "steps":
        return ["walk"]
    return ["walk", "bike"]


def classify_building(props, name):
    if "building" not in props:
        return None
    amenity = props.get("amenity")
    shop = str(props.get("shop", "")).lower()
    if amenity in {"hospital", "restaurant", "fast_food", "cafe", "toilets", "post_office", "parking", "parking_space", "parking_entrance", "bicycle_parking", "charging_station", "library", "bank", "atm"}:
        return None
    if amenity == "university" and (name == "北京邮电大学" or props.get("short_name") == "北邮"):
        return None
    if shop:
        return None

    building_tag = str(props.get("building", "")).lower()
    text = name or ""
    if any(token in text for token in EXCLUDED_NAME_TOKENS):
        return None
    if building_tag in {"dormitory", "apartments"} or any(token in text for token in ["公寓", "宿舍", "学1楼", "学2楼", "学3楼", "学4楼", "学5楼", "学6楼", "学7楼", "学8楼", "学9楼", "学10楼"]):
        return "dorm"
    if any(token in text for token in ["图书馆", "体育馆", "体育场", "运动场", "游泳馆", "会堂", "礼堂", "广场", "酒店", "馆"]):
        return "attraction"
    if any(token in text for token in ["行政", "后勤", "保卫", "服务中心", "幼儿园"]):
        return "office"
    return "teaching"


def classify_facility(props, name):
    amenity = str(props.get("amenity", "")).lower()
    shop = str(props.get("shop", "")).lower()
    leisure = str(props.get("leisure", "")).lower()
    text = name or ""

    if amenity in {"restaurant", "fast_food"}:
        return "canteen" if "食堂" in text else "restaurant"
    if amenity == "cafe" or "咖啡" in text:
        return "cafe"
    if amenity == "hospital":
        return "clinic"
    if amenity == "toilets":
        return "toilet"
    if amenity == "post_office":
        return "express"
    if amenity in {"bank", "atm"}:
        return "bank"
    if amenity in {"parking", "parking_space", "parking_entrance", "bicycle_parking", "charging_station"}:
        return "parking"
    if amenity == "library":
        return "library"
    if shop in {"supermarket", "convenience"}:
        return "supermarket"
    if shop:
        return "shop"
    if leisure in {"stadium", "fitness_centre", "fitness_station"}:
        return "sports"
    if any(token in text for token in ["快递", "邮驿站"]):
        return "express"
    if any(token in text for token in ["超市", "便利店"]):
        return "supermarket"
    if any(token in text for token in ["球场", "体育"]):
        return "sports"
    return None


def normalize_poi_name(name, kind, category, source_tags):
    normalized = (name or "").strip()
    if normalized in NAME_ALIASES:
        return NAME_ALIASES[normalized]
    if category == "library" and not normalized:
        return "图书馆"
    if category == "bank" and normalized.startswith("ATM"):
        return "邮储ATM"
    if normalized == "北邮体育馆":
        return "体育馆"
    return normalized


def build_poi_description(kind, category, name):
    if kind == "building":
        return f"校内建筑：{name}"
    return facility_description(category)


def should_skip_poi(name):
    return any(token in (name or "") for token in EXCLUDED_NAME_TOKENS)


def build_source_tags(props):
    keys = [
        "building", "building:levels", "amenity", "shop", "leisure", "opening_hours",
        "name", "name:zh", "loc_name", "brand", "brand:zh", "official_name",
    ]
    return {key: props[key] for key in keys if key in props}


def facility_description(category):
    return FACILITY_DESCRIPTIONS.get(category, "校内设施")


def generated_poi_name(kind, category, counter):
    counter[category] = counter.get(category, 0) + 1
    base = {
        "toilet": "卫生间",
        "parking": "停车点",
        "bank": "ATM",
        "library": "图书馆",
        "shop": "商店",
        "supermarket": "便利店",
        "sports": "运动设施",
        "cafe": "咖啡点",
        "restaurant": "餐饮点",
        "canteen": "食堂",
        "express": "快递点",
        "clinic": "医疗点",
    }.get(category, "设施")
    if category == "library":
        return base
    return f"{base}{counter[category]}"


def extract_campus_polygon(features):
    candidates = []
    for feature in features:
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        if geometry.get("type") not in {"Polygon", "MultiPolygon"}:
            continue
        if props.get("amenity") != "university":
            continue
        name = get_feature_name(props)
        if "北京邮电大学" not in name and props.get("short_name") != "北邮":
            continue
        shell = get_polygon_shell(geometry)
        if shell:
            candidates.append(shell)
    if not candidates:
        raise RuntimeError("未在 export.geojson 中找到北京邮电大学校园边界")
    return max(candidates, key=polygon_area_estimate)


def extract_road_graph(features, campus_polygon, campus_bounds):
    nodes = []
    edges = []
    node_id_by_key = {}
    edge_keys = set()
    next_node_id = 1

    def ensure_node(lng, lat, node_type="crossing", name=None, ref_poi_id=None):
        nonlocal next_node_id
        key = point_key(lng, lat, precision=7)
        node_id = node_id_by_key.get(key)
        if node_id:
            return node_id
        node_id = next_node_id
        next_node_id += 1
        nodes.append({
            "id": node_id,
            "name": name or f"路口_{node_id}",
            "lat": lat,
            "lng": lng,
            "node_type": node_type,
            "ref_poi_id": ref_poi_id,
        })
        node_id_by_key[key] = node_id
        return node_id

    for feature in features:
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        if geometry.get("type") != "LineString":
            continue
        highway = str(props.get("highway", "")).lower()
        if highway not in ALLOWED_HIGHWAYS:
            continue

        segments = clip_linestring_to_campus(geometry.get("coordinates", []), campus_polygon, campus_bounds)
        if not segments:
            continue

        is_bidirectional = str(props.get("oneway", "")).lower() not in {"yes", "1", "true"}
        road_types = road_types_for_highway(highway)

        for segment in segments:
            node_ids = [ensure_node(lng, lat) for lng, lat in segment]
            for index in range(len(segment) - 1):
                from_lng, from_lat = segment[index]
                to_lng, to_lat = segment[index + 1]
                from_id = node_ids[index]
                to_id = node_ids[index + 1]
                if from_id == to_id:
                    continue
                distance = round(haversine(from_lng, from_lat, to_lng, to_lat), 2)
                if distance < 1:
                    continue
                for road_type in road_types:
                    key = (min(from_id, to_id), max(from_id, to_id), road_type, is_bidirectional)
                    if key in edge_keys:
                        continue
                    edge_keys.add(key)
                    config = ROAD_TYPE_CONFIG[road_type]
                    edges.append({
                        "from_node_id": from_id,
                        "to_node_id": to_id,
                        "distance": distance,
                        "road_type": road_type,
                        "is_bidirectional": is_bidirectional,
                        "ideal_speed": config["ideal_speed"],
                        "congestion_factor": config["congestion_factor"],
                    })

    return nodes, edges, next_node_id


def append_poi(container, index_map, poi):
    name = (poi.get("name") or "").strip()
    if name:
        key = (poi["kind"], poi["category"], name)
    else:
        key = (poi["kind"], poi["category"], point_key(poi["lng"], poi["lat"], precision=6))
    existing_idx = index_map.get(key)
    if existing_idx is None:
        index_map[key] = len(container)
        container.append(poi)
        return

    existing = container[existing_idx]
    if geometry_rank(poi["geometry_type"]) > geometry_rank(existing["geometry_type"]):
        container[existing_idx] = poi


def extract_pois(features, campus_polygon, campus_bounds):
    pois = []
    poi_index = {}
    generated_counter = {}

    for feature in features:
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        gtype = geometry.get("type")
        if gtype not in {"Point", "Polygon", "MultiPolygon"}:
            continue

        point = representative_point(feature)
        if not point or not point_in_campus(point, campus_polygon, campus_bounds):
            continue

        lng, lat = point
        name = get_feature_name(props)
        if should_skip_poi(name):
            continue
        feature_id = feature.get("id") or props.get("@id") or ""
        source_tags = build_source_tags(props)

        building_category = classify_building(props, name)
        facility_category = classify_facility(props, name)

        if building_category and name:
            normalized_name = normalize_poi_name(name, "building", building_category, source_tags)
            append_poi(pois, poi_index, {
                "name": normalized_name,
                "kind": "building",
                "category": building_category,
                "lat": lat,
                "lng": lng,
                "description": build_poi_description("building", building_category, normalized_name),
                "source_osm_id": feature_id,
                "source_tags": source_tags,
                "geometry_type": gtype,
            })
            continue

        if facility_category:
            display_name = normalize_poi_name(name or generated_poi_name("facility", facility_category, generated_counter), "facility", facility_category, source_tags)
            append_poi(pois, poi_index, {
                "name": display_name,
                "kind": "facility",
                "category": facility_category,
                "lat": lat,
                "lng": lng,
                "description": build_poi_description("facility", facility_category, display_name),
                "source_osm_id": feature_id,
                "source_tags": source_tags,
                "geometry_type": gtype,
            })

    for idx, poi in enumerate(pois, start=1):
        poi["id"] = idx
        poi.pop("geometry_type", None)

    return pois


def nearest_walk_node(point, nodes, edges):
    walk_node_ids = set()
    for edge in edges:
        if edge["road_type"] == "walk":
            walk_node_ids.add(edge["from_node_id"])
            walk_node_ids.add(edge["to_node_id"])
    candidates = [node for node in nodes if node["id"] in walk_node_ids]
    if not candidates:
        raise RuntimeError("未提取到可步行路网节点")
    lng, lat = point
    return min(candidates, key=lambda node: haversine(lng, lat, node["lng"], node["lat"]))


def build_map_and_poi_data(features):
    campus_polygon = extract_campus_polygon(features)
    campus_bounds = polygon_bounds(campus_polygon)
    campus_center_lng, campus_center_lat = polygon_centroid(campus_polygon)

    nodes, edges, next_node_id = extract_road_graph(features, campus_polygon, campus_bounds)
    pois = extract_pois(features, campus_polygon, campus_bounds)

    for poi in pois:
        nearest_node = nearest_walk_node((poi["lng"], poi["lat"]), nodes, edges)
        node_id = next_node_id
        next_node_id += 1
        nodes.append({
            "id": node_id,
            "name": poi["name"],
            "lat": poi["lat"],
            "lng": poi["lng"],
            "node_type": poi["kind"],
            "ref_poi_id": poi["id"],
        })
        poi["node_id"] = node_id
        distance = round(haversine(poi["lng"], poi["lat"], nearest_node["lng"], nearest_node["lat"]), 2)
        if distance >= 1:
            edges.append({
                "from_node_id": node_id,
                "to_node_id": nearest_node["id"],
                "distance": distance,
                "road_type": "walk",
                "is_bidirectional": True,
                "ideal_speed": ROAD_TYPE_CONFIG["walk"]["ideal_speed"],
                "congestion_factor": ROAD_TYPE_CONFIG["walk"]["congestion_factor"],
            })
            edges.append({
                "from_node_id": node_id,
                "to_node_id": nearest_node["id"],
                "distance": distance,
                "road_type": "bike",
                "is_bidirectional": True,
                "ideal_speed": ROAD_TYPE_CONFIG["bike"]["ideal_speed"],
                "congestion_factor": ROAD_TYPE_CONFIG["bike"]["congestion_factor"],
            })

    map_data = {
        "crs": "WGS84",
        "source_crs": "WGS84",
        "spot": {
            "name": SPOT_NAME,
            "center": {"lng": campus_center_lng, "lat": campus_center_lat},
        },
        "nodes": nodes,
        "edges": edges,
    }
    return map_data, pois


def batch_convert_coordinates(points):
    unique_points = []
    seen = set()
    for lng, lat in points:
        key = point_key(lng, lat, precision=7)
        if key not in seen:
            seen.add(key)
            unique_points.append((lng, lat))

    converted = {}
    batch_size = 40
    use_local_fallback = False
    for start in range(0, len(unique_points), batch_size):
        batch = unique_points[start:start + batch_size]
        if use_local_fallback:
            for lng, lat in batch:
                converted[point_key(lng, lat, precision=7)] = wgs84_to_gcj02(lng, lat)
            continue

        locations = ";".join(f"{lng},{lat}" for lng, lat in batch)
        data = amap_get("https://restapi.amap.com/v3/assistant/coordinate/convert", {
            "key": AMAP_KEY,
            "locations": locations,
            "coordsys": "gps",
            "output": "json",
        })
        if data.get("status") != "1" or not data.get("locations"):
            if data.get("infocode") == "10021":
                use_local_fallback = True
                for lng, lat in batch:
                    converted[point_key(lng, lat, precision=7)] = wgs84_to_gcj02(lng, lat)
                continue
            raise RuntimeError(f"高德坐标转换失败: {data}")
        parts = data["locations"].split(";")
        if len(parts) != len(batch):
            raise RuntimeError("高德坐标转换返回数量与请求数量不一致")
        for original, raw in zip(batch, parts):
            lng, lat = map(float, raw.split(","))
            converted[point_key(original[0], original[1], precision=7)] = (lng, lat)
        time.sleep(0.05)
    return converted


def apply_gcj02_conversion(map_data, poi_data):
    raw_points = []
    for node in map_data["nodes"]:
        raw_points.append((node["lng"], node["lat"]))
    for poi in poi_data:
        raw_points.append((poi["lng"], poi["lat"]))
    center = map_data["spot"]["center"]
    raw_points.append((center["lng"], center["lat"]))

    converted = batch_convert_coordinates(raw_points)

    for node in map_data["nodes"]:
        lng, lat = converted[point_key(node["lng"], node["lat"], precision=7)]
        node["lng"] = lng
        node["lat"] = lat

    for poi in poi_data:
        lng, lat = converted[point_key(poi["lng"], poi["lat"], precision=7)]
        poi["lng"] = lng
        poi["lat"] = lat

    center_lng, center_lat = converted[point_key(center["lng"], center["lat"], precision=7)]
    map_data["spot"]["center"] = {"lng": center_lng, "lat": center_lat}
    map_data["crs"] = "GCJ-02"


def ensure_spot(conn, center_lng, center_lat):
    c = conn.cursor()
    c.execute("SELECT id FROM scenic_spots WHERE name=? AND city=?", (SPOT_NAME, SPOT_CITY))
    row = c.fetchone()
    if row:
        c.execute(
            "UPDATE scenic_spots SET category=?, type=?, address=?, description=?, tags=?, location_lng=?, location_lat=? WHERE id=?",
            (SPOT_CATEGORY, SPOT_TYPE, SPOT_ADDRESS, SPOT_DESCRIPTION, SPOT_TAGS, center_lng, center_lat, row[0]),
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
            center_lat,
            center_lng,
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


def insert_building(conn, spot_id, poi):
    c = conn.cursor()
    floor_count = None
    raw_levels = poi.get("source_tags", {}).get("building:levels")
    if raw_levels:
        try:
            floor_count = int(float(raw_levels))
        except Exception:
            floor_count = None
    c.execute(
        "INSERT INTO buildings (spot_id, name, type, location_lng, location_lat, floor_count, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (spot_id, poi["name"], poi["category"], poi["lng"], poi["lat"], floor_count, poi["description"]),
    )
    conn.commit()
    return c.lastrowid


def insert_facility(conn, spot_id, poi):
    c = conn.cursor()
    c.execute(
        "INSERT INTO facilities (spot_id, name, type, location_lng, location_lat, description) VALUES (?, ?, ?, ?, ?, ?)",
        (spot_id, poi["name"], poi["category"], poi["lng"], poi["lat"], poi["description"]),
    )
    conn.commit()
    return c.lastrowid


def insert_node(conn, spot_id, node, ref_id_map):
    c = conn.cursor()
    ref_id = None
    if node["node_type"] in {"building", "facility"} and node.get("ref_poi_id"):
        ref_id = ref_id_map.get(node["ref_poi_id"])
    c.execute(
        "INSERT INTO road_nodes (spot_id, name, location_lng, location_lat, node_type, ref_id) VALUES (?, ?, ?, ?, ?, ?)",
        (spot_id, node["name"], node["lng"], node["lat"], node["node_type"], ref_id),
    )
    conn.commit()
    return c.lastrowid


def insert_edge(conn, spot_id, edge, node_id_map):
    c = conn.cursor()
    c.execute(
        "INSERT INTO road_edges (spot_id, from_node_id, to_node_id, distance, ideal_speed, congestion_factor, road_type, is_bidirectional) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            spot_id,
            node_id_map[edge["from_node_id"]],
            node_id_map[edge["to_node_id"]],
            edge["distance"],
            edge["ideal_speed"],
            edge["congestion_factor"],
            edge["road_type"],
            1 if edge.get("is_bidirectional", True) else 0,
        ),
    )
    conn.commit()


def write_json_outputs(map_data, poi_data):
    MAP_DATA_PATH.write_text(json.dumps(map_data, ensure_ascii=False, indent=2), encoding="utf-8")
    POI_DATA_PATH.write_text(json.dumps(poi_data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_into_database(map_data, poi_data):
    conn = sqlite3.connect(DB_PATH)
    try:
        center = map_data["spot"]["center"]
        spot_id = ensure_spot(conn, center["lng"], center["lat"])
        clear_existing_map(conn, spot_id)

        ref_id_map = {}
        for poi in poi_data:
            if poi["kind"] == "building":
                ref_id_map[poi["id"]] = insert_building(conn, spot_id, poi)
            elif poi["kind"] == "facility":
                ref_id_map[poi["id"]] = insert_facility(conn, spot_id, poi)

        node_id_map = {}
        for node in map_data["nodes"]:
            node_id_map[node["id"]] = insert_node(conn, spot_id, node, ref_id_map)

        for edge in map_data["edges"]:
            insert_edge(conn, spot_id, edge, node_id_map)

        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM buildings WHERE spot_id=?", (spot_id,))
        print("buildings", c.fetchone()[0])
        c.execute("SELECT COUNT(*) FROM facilities WHERE spot_id=?", (spot_id,))
        print("facilities", c.fetchone()[0])
        c.execute("SELECT COUNT(*) FROM road_nodes WHERE spot_id=?", (spot_id,))
        print("nodes", c.fetchone()[0])
        c.execute("SELECT COUNT(*) FROM road_edges WHERE spot_id=?", (spot_id,))
        print("edges", c.fetchone()[0])
    finally:
        conn.close()


def main():
    if not EXPORT_GEOJSON_PATH.exists():
        raise FileNotFoundError(f"未找到文件: {EXPORT_GEOJSON_PATH}")

    geojson = json.loads(EXPORT_GEOJSON_PATH.read_text(encoding="utf-8"))
    features = geojson.get("features", [])
    map_data, poi_data = build_map_and_poi_data(features)
    apply_gcj02_conversion(map_data, poi_data)
    write_json_outputs(map_data, poi_data)
    load_into_database(map_data, poi_data)
    print(f"map json -> {MAP_DATA_PATH}")
    print(f"poi json -> {POI_DATA_PATH}")


if __name__ == "__main__":
    main()
