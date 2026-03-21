#!/usr/bin/env python3
"""
Sync city spot and food cards from Mafengwo mobile recommendations.

This script:
1. fetches the "最热景点" and "美食推荐" sections for each configured city,
2. downloads the referenced images into the project-level images directory,
3. updates/inserts ScenicSpot and Restaurant rows in the local SQLite database.
"""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
IMAGES_ROOT = PROJECT_ROOT / "images"

sys.path.insert(0, str(BACKEND_ROOT))

from models.database import Restaurant, ScenicSpot, SessionLocal  # noqa: E402

USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 "
    "Mobile/15E148 Safari/604.1"
)
REQUEST_HEADERS = {"User-Agent": USER_AGENT}

TARGET_MIN_SPOTS = 6


@dataclass(frozen=True)
class CityConfig:
    name: str
    slug: str
    mddid: str


@dataclass
class CardItem:
    name: str
    href: str
    image_url: str
    review_count: int

    @property
    def ref_id(self) -> str:
        matches = re.findall(r"(\d+)", self.href or "")
        return matches[-1] if matches else "0"


CITY_CONFIGS = [
    CityConfig("\u5317\u4eac", "beijing", "10065"),
    CityConfig("\u4e0a\u6d77", "shanghai", "10099"),
    CityConfig("\u897f\u5b89", "xian", "10195"),
    CityConfig("\u6210\u90fd", "chengdu", "10035"),
    CityConfig("\u676d\u5dde", "hangzhou", "10156"),
    CityConfig("\u91cd\u5e86", "chongqing", "10208"),
    CityConfig("\u9752\u5c9b", "qingdao", "10444"),
    CityConfig("\u5e7f\u5dde", "guangzhou", "10088"),
    CityConfig("\u82cf\u5dde", "suzhou", "10207"),
    CityConfig("\u53a6\u95e8", "xiamen", "10132"),
    CityConfig("\u5357\u4eac", "nanjing", "10684"),
    CityConfig("\u6b66\u6c49", "wuhan", "10133"),
    CityConfig("\u957f\u6c99", "changsha", "10466"),
    CityConfig("\u6df1\u5733", "shenzhen", "10198"),
    CityConfig("\u4e09\u4e9a", "sanya", "10030"),
    CityConfig("\u6842\u6797", "guilin", "10095"),
    CityConfig("\u5f20\u5bb6\u754c", "zhangjiajie", "10267"),
    CityConfig("\u9ec4\u5c71", "huangshan", "10440"),
    CityConfig("\u4e5d\u5be8\u6c9f", "jiuzhaigou", "10136"),
    CityConfig("\u5927\u7406", "dali", "10487"),
    CityConfig("\u4e3d\u6c5f", "lijiang", "10186"),
]

SPOT_ALIASES = {
    "\u6545\u5bab": ["\u6545\u5bab\u535a\u7269\u9662"],
    "\u516b\u8fbe\u5cad\u957f\u57ce": ["\u957f\u57ce-\u516b\u8fbe\u5cad", "\u957f\u57ce"],
    "\u5929\u575b": ["\u5929\u575b\u516c\u56ed"],
    "\u4e0a\u6d77\u57ce\u968d\u5e99\u65c5\u6e38\u533a": ["\u8c6b\u56ed", "\u57ce\u968d\u5e99"],
    "\u897f\u5b89\u57ce\u5899": ["\u53e4\u57ce\u5899", "\u57ce\u5899"],
    "\u79e6\u59cb\u7687\u5e1d\u9675\u535a\u7269\u9662\u5175\u9a6c\u4fd1": [
        "\u79e6\u59cb\u7687\u5175\u9a6c\u4fd1",
        "\u5175\u9a6c\u4fd1",
    ],
    "\u6210\u90fd\u5927\u718a\u732b\u7e41\u80b2\u7814\u7a76\u57fa\u5730": [
        "\u5927\u718a\u732b\u7e41\u80b2\u7814\u7a76\u57fa\u5730",
        "\u718a\u732b\u57fa\u5730",
    ],
    "\u676d\u5dde\u897f\u6e56\u98ce\u666f\u540d\u80dc\u533a": ["\u897f\u6e56"],
    "\u6d2a\u5d16\u6d1e\u6c11\u4fd7\u98ce\u8c8c\u533a": ["\u6d2a\u5d16\u6d1e"],
    "\u78c1\u5668\u53e3\u53e4\u9547": ["\u78c1\u5668\u53e3"],
    "\u6c99\u9762\u5c9b": ["\u6c99\u9762"],
    "\u82cf\u5dde\u535a\u7269\u9986\u672c\u9986": ["\u82cf\u5dde\u535a\u7269\u9986"],
    "\u592b\u5b50\u5e99\u79e6\u6dee\u98ce\u5149\u5e26": ["\u592b\u5b50\u5e99"],
    "\u4e1c\u6e56\u751f\u6001\u65c5\u6e38\u98ce\u666f\u533a": ["\u4e1c\u6e56"],
    "\u8717\u652f\u6d32\u5c9b\u65c5\u6e38\u98ce\u666f\u533a": ["\u8717\u652f\u6d32\u5c9b"],
    "\u5f20\u5bb6\u754c\u56fd\u5bb6\u68ee\u6797\u516c\u56ed": ["\u5f20\u5bb6\u754c"],
    "\u5929\u95e8\u5c71\u56fd\u5bb6\u68ee\u6797\u516c\u56ed": ["\u5929\u95e8\u5c71"],
    "\u9ec4\u5c71\u98ce\u666f\u533a": ["\u9ec4\u5c71"],
    "\u4e5d\u5be8\u6c9f\u98ce\u666f\u533a": ["\u4e5d\u5be8\u6c9f"],
    "\u6cf8\u6cbd\u6e56\u56fd\u5bb6\u7ea7\u98ce\u666f\u540d\u80dc\u533a": ["\u6cf8\u6cbd\u6e56"],
}

FOOD_NAME_OVERRIDES = {
    ("\u4e0a\u6d77", "\u6c64\u5305"): "\u5357\u7fd4\u6c64\u5305",
    ("\u91cd\u5e86", "\u706b\u9505"): "\u91cd\u5e86\u706b\u9505",
    ("\u9752\u5c9b", "\u70e7\u70e4"): "\u6d77\u9c9c\u70e7\u70e4",
    ("\u9752\u5c9b", "\u9c85\u9c7c"): "\u9c85\u9c7c\u6c34\u997a",
    ("\u5e7f\u5dde", "\u6c64"): "\u8001\u706b\u6c64",
    ("\u5e7f\u5dde", "\u53c9\u70e7"): "\u871c\u6c41\u53c9\u70e7",
    ("\u6842\u6797", "\u917f"): "\u6842\u6797\u917f\u83dc",
    ("\u957f\u6c99", "\u6768\u88d5\u5174"): "\u6768\u88d5\u5174\u9762\u6761",
}

FOOD_ALIASES = {
    "\u751f\u714e": ["\u751f\u714e\u5305"],
    "\u5357\u7fd4\u6c64\u5305": ["\u5c0f\u7b3c\u5305", "\u6c64\u5305"],
    "\u7ea2\u70e7\u8089": ["\u672c\u5e2e\u7ea2\u70e7\u8089"],
    "\u91cd\u5e86\u706b\u9505": ["\u706b\u9505"],
    "\u8089\u5939\u998d": ["\u8089\u5939\u998d"],
    "\u897f\u6e56\u918b\u9c7c": ["\u897f\u6e56\u918b\u9c7c"],
    "\u9e2d\u8840\u7c89\u4e1d\u6c64": ["\u9e2d\u8840\u7c89\u4e1d\u6c64"],
    "\u70ed\u5e72\u9762": ["\u70ed\u5e72\u9762"],
    "\u81ed\u8c46\u8150": ["\u81ed\u8c46\u8150"],
    "\u6842\u6797\u7c73\u7c89": ["\u6842\u6797\u7c73\u7c89"],
    "\u4e09\u4e0b\u9505": ["\u4e09\u4e0b\u9505"],
    "\u6bdb\u8c46\u8150": ["\u6bdb\u8c46\u8150"],
    "\u9170\u9cdc\u9c7c": ["\u81ed\u9cdc\u9c7c"],
    "\u9165\u6cb9\u8336": ["\u9165\u6cb9\u8336"],
    "\u9e21\u8c46\u51c9\u7c89": ["\u9e21\u8c46\u51c9\u7c89"],
}

COMMON_NAME_SUFFIXES = [
    "\u98ce\u666f\u540d\u80dc\u533a",
    "\u56fd\u5bb6\u7ea7\u98ce\u666f\u540d\u80dc\u533a",
    "\u751f\u6001\u65c5\u6e38\u98ce\u666f\u533a",
    "\u65c5\u6e38\u98ce\u666f\u533a",
    "\u98ce\u8c8c\u533a",
    "\u65c5\u6e38\u533a",
    "\u666f\u533a",
    "\u535a\u7269\u9662",
    "\u535a\u7269\u9986",
    "\u516c\u56ed",
    "\u672c\u9986",
]

SPOT_TAG_RULES = [
    ("\u535a\u7269", ["\u535a\u7269\u5c55\u89c8", "\u6587\u5316\u4f53\u9a8c"]),
    ("\u5927\u5b66", ["\u4eba\u6587\u6821\u56ed", "\u62cd\u7167\u51fa\u7247"]),
    ("\u53e4\u57ce", ["\u53e4\u97f5\u8857\u533a", "\u57ce\u5e02\u6563\u6b65"]),
    ("\u53e4\u9547", ["\u6c5f\u5357\u98ce\u60c5", "\u6162\u6e38\u4f53\u9a8c"]),
    ("\u957f\u57ce", ["\u5fc5\u6253\u5361", "\u5730\u6807\u666f\u70b9"]),
    ("\u5e7f\u573a", ["\u57ce\u5e02\u5730\u6807", "\u5f00\u9614\u89c6\u91ce"]),
    ("\u5854", ["\u57ce\u5e02\u5730\u6807", "\u767b\u9ad8\u89c2\u666f"]),
    ("\u6e56", ["\u5c71\u6c34\u98ce\u5149", "\u4f11\u95f2\u6563\u5fc3"]),
    ("\u6d77", ["\u6d77\u6ee8\u98ce\u5149", "\u5ea6\u5047\u653e\u677e"]),
    ("\u5c71", ["\u81ea\u7136\u98ce\u5149", "\u5f92\u6b65\u89c2\u666f"]),
]

FOOD_CUISINE_RULES = [
    ("\u706b\u9505", "\u706b\u9505"),
    ("\u8336", "\u996e\u54c1"),
    ("\u9152", "\u996e\u54c1"),
    ("\u6c64", "\u5c0f\u5403"),
    ("\u7c89", "\u5c0f\u5403"),
    ("\u9762", "\u5c0f\u5403"),
    ("\u5305", "\u5c0f\u5403"),
    ("\u997a", "\u5c0f\u5403"),
    ("\u7c89\u4e1d", "\u5c0f\u5403"),
    ("\u7c73\u7ebf", "\u6ec7\u83dc"),
    ("\u7c73\u7c89", "\u5c0f\u5403"),
    ("\u70e7\u9e45", "\u7ca4\u83dc"),
    ("\u53c9\u70e7", "\u7ca4\u83dc"),
    ("\u9e2d", "\u7279\u8272\u83dc"),
    ("\u725b\u8089", "\u7279\u8272\u83dc"),
    ("\u867e", "\u7279\u8272\u83dc"),
    ("\u9c7c", "\u7279\u8272\u83dc"),
]

CITY_DEFAULT_CUISINES = {
    "\u5317\u4eac": "\u4eac\u83dc",
    "\u4e0a\u6d77": "\u672c\u5e2e\u83dc",
    "\u897f\u5b89": "\u9655\u83dc",
    "\u6210\u90fd": "\u5ddd\u83dc",
    "\u676d\u5dde": "\u6d59\u83dc",
    "\u91cd\u5e86": "\u5ddd\u6e1d\u83dc",
    "\u9752\u5c9b": "\u9c81\u83dc",
    "\u5e7f\u5dde": "\u7ca4\u83dc",
    "\u82cf\u5dde": "\u82cf\u83dc",
    "\u53a6\u95e8": "\u95fd\u5357\u83dc",
    "\u5357\u4eac": "\u82cf\u83dc",
    "\u6b66\u6c49": "\u9102\u83dc",
    "\u957f\u6c99": "\u6e58\u83dc",
    "\u6df1\u5733": "\u7ca4\u83dc",
    "\u4e09\u4e9a": "\u743c\u83dc",
    "\u6842\u6797": "\u6842\u83dc",
    "\u5f20\u5bb6\u754c": "\u6e58\u83dc",
    "\u9ec4\u5c71": "\u5fbd\u83dc",
    "\u4e5d\u5be8\u6c9f": "\u85cf\u65cf\u98ce\u5473",
    "\u5927\u7406": "\u6ec7\u83dc",
    "\u4e3d\u6c5f": "\u6ec7\u83dc",
}


def normalize_name(value: str) -> str:
    normalized = re.sub(r"[\s\-\u2014\u00b7\u2022\(\)\uff08\uff09\u3010\u3011\[\]\uff0c,\u3002/\u3001]", "", value or "")
    normalized = normalized.lower()
    variants = [normalized]
    for suffix in COMMON_NAME_SUFFIXES:
        if normalized.endswith(suffix):
            variants.append(normalized[: -len(suffix)])
    result = max(variants, key=len)
    return result


def build_name_variants(name: str, aliases: Optional[Iterable[str]] = None) -> set[str]:
    variants = {normalize_name(name)}
    if aliases:
        variants.update(normalize_name(alias) for alias in aliases)
    variants = {value for value in variants if value}
    expanded = set(variants)
    for value in list(variants):
        for suffix in COMMON_NAME_SUFFIXES:
            if value.endswith(suffix):
                trimmed = value[: -len(suffix)]
                if len(trimmed) >= 4:
                    expanded.add(trimmed)
    return {value for value in expanded if value}


def find_matching_spot(city_spots: list[ScenicSpot], target_name: str) -> Optional[ScenicSpot]:
    aliases = SPOT_ALIASES.get(target_name, [])
    target_variants = build_name_variants(target_name, aliases)
    for spot in city_spots:
        spot_variants = build_name_variants(spot.name)
        if target_variants & spot_variants:
            return spot
        if any(
            len(left) >= 2 and len(right) >= 2 and (left in right or right in left)
            for left in target_variants
            for right in spot_variants
        ):
            return spot
    return None


def find_matching_food(city_foods: list[Restaurant], target_name: str) -> Optional[Restaurant]:
    aliases = FOOD_ALIASES.get(target_name, [])
    target_variants = build_name_variants(target_name, aliases)
    for food in city_foods:
        food_variants = build_name_variants(food.name)
        if target_variants & food_variants:
            return food
        if any(
            len(left) >= 2 and len(right) >= 2 and (left in right or right in left)
            for left in target_variants
            for right in food_variants
        ):
            return food
    return None


def infer_spot_category(name: str) -> str:
    if any(keyword in name for keyword in ["\u535a\u7269\u9986", "\u535a\u7269\u9662", "\u7eaa\u5ff5\u9986"]):
        return "\u535a\u7269\u5c55\u89c8"
    if any(keyword in name for keyword in ["\u5927\u5b66", "\u4e66\u9662"]):
        return "\u4eba\u6587\u6821\u56ed"
    if any(keyword in name for keyword in ["\u5e7f\u573a", "\u5854", "\u6559\u5802", "\u8def", "\u8857"]):
        return "\u5730\u6807\u5efa\u7b51"
    if any(keyword in name for keyword in ["\u6545\u5bab", "\u7960", "\u53e4\u57ce", "\u53e4\u9547", "\u57ce\u5899", "\u5bab"]):
        return "\u5386\u53f2\u53e4\u8ff9"
    return "\u98ce\u666f\u540d\u80dc"


def infer_spot_tags(name: str, city: str) -> list[str]:
    for keyword, tags in SPOT_TAG_RULES:
        if keyword in name:
            return list(tags)
    if city in {"\u4e09\u4e9a", "\u53a6\u95e8", "\u9752\u5c9b"}:
        return ["\u6d77\u6ee8\u98ce\u5149", "\u65c5\u884c\u62cd\u7167"]
    return ["\u9a6c\u8702\u7a9d\u70ed\u95e8", "\u57ce\u5e02\u5fc5\u6253\u5361"]


def infer_food_cuisine(city: str, name: str) -> str:
    for keyword, cuisine in FOOD_CUISINE_RULES:
        if keyword in name:
            return cuisine
    return CITY_DEFAULT_CUISINES.get(city, "\u7279\u8272\u7f8e\u98df")


def infer_food_tags(name: str) -> list[str]:
    tags = ["\u9a6c\u8702\u7a9d\u63a8\u8350", "\u672c\u5730\u7279\u8272"]
    if any(keyword in name for keyword in ["\u70b8", "\u7c89", "\u9762", "\u5305", "\u997a", "\u7c89\u4e1d", "\u996d"]):
        tags[1] = "\u5fc5\u5403\u5c0f\u5403"
    if any(keyword in name for keyword in ["\u706b\u9505", "\u70e4\u9e45", "\u53c9\u70e7", "\u9c7c", "\u9e2d", "\u725b\u8089"]):
        tags.append("\u62db\u724c\u786c\u83dc")
    return tags


def infer_food_price(name: str) -> str:
    if any(keyword in name for keyword in ["\u706b\u9505", "\u70e4\u9e45", "\u53c9\u70e7", "\u9c7c", "\u9e2d", "\u725b\u8089", "\u867e"]):
        return "\u00a540-120"
    if any(keyword in name for keyword in ["\u9152", "\u8336", "\u51b0", "\u70b8", "\u7c89", "\u9762", "\u5305", "\u997a", "\u7c89\u4e1d", "\u7c73\u7c89", "\u7c73\u7ebf"]):
        return "\u00a510-35"
    return "\u00a520-60"


def build_spot_description(city: str, name: str) -> str:
    category = infer_spot_category(name)
    return f"{name}\u662f{city}\u7684\u4eba\u6c14{category}\uff0c\u9002\u5408\u7b2c\u4e00\u6b21\u5230\u8bbf\u65f6\u4f18\u5148\u5b89\u6392\u6253\u5361\u3002"


def build_food_description(city: str, name: str) -> str:
    return f"{name}\u662f{city}\u9887\u53d7\u6b22\u8fce\u7684\u7279\u8272\u7f8e\u98df\uff0c\u9002\u5408\u65c5\u884c\u9014\u4e2d\u6253\u5361\u54c1\u5c1d\u3002"


def download_image(session: requests.Session, url: str, destination: Path) -> None:
    if destination.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    response = session.get(url, headers=REQUEST_HEADERS, timeout=30)
    response.raise_for_status()
    destination.write_bytes(response.content)


def local_extension(url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        return suffix
    return ".jpg"


def fetch_city_cards(session: requests.Session, config: CityConfig) -> tuple[list[CardItem], list[CardItem]]:
    response = session.post(
        "https://m.mafengwo.cn/mdd/mdd/getPoiRecommends",
        data={"mddid": config.mddid},
        headers={**REQUEST_HEADERS, "Referer": f"https://m.mafengwo.cn/mdd/{config.mddid}"},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    html = payload.get("html", "")
    soup = BeautifulSoup(html, "html.parser")

    spots: list[CardItem] = []
    foods: list[CardItem] = []

    for section in soup.select("section.cityItem"):
        heading = section.find("h3")
        if not heading:
            continue
        title = heading.get_text(" ", strip=True)
        if "\u666f\u70b9" in title:
            bucket = spots
        elif "\u7f8e\u98df" in title:
            bucket = foods
        else:
            continue

        for item in section.select("li"):
            link = item.find("a", href=True)
            image = item.find("img")
            name_node = item.select_one(".t1")
            reviews = item.select_one(".t2 strong")
            if not link or not image or not name_node:
                continue
            image_url = image.get("data-original") or image.get("src")
            if not image_url:
                continue
            review_count = int(re.sub(r"\D", "", reviews.get_text(strip=True))) if reviews else 0
            bucket.append(
                CardItem(
                    name=name_node.get_text(strip=True),
                    href=link["href"],
                    image_url=image_url,
                    review_count=review_count,
                )
            )

    return spots[:4], foods[:4]


def main() -> None:
    session = requests.Session()
    db = SessionLocal()

    try:
        for config in CITY_CONFIGS:
            print(f"[sync] {config.name}")
            spots, foods = fetch_city_cards(session, config)

            city_spots = list(db.query(ScenicSpot).filter(ScenicSpot.city == config.name).all())
            city_spot_count = len(city_spots)
            inserted_spot = False

            for index, item in enumerate(spots):
                matched = find_matching_spot(city_spots, item.name)
                extension = local_extension(item.image_url)
                disk_path = IMAGES_ROOT / "spots" / config.slug / f"{config.slug}_{item.ref_id}{extension}"
                local_path = f"/images/spots/{config.slug}/{config.slug}_{item.ref_id}{extension}"
                download_image(session, item.image_url, disk_path)

                if matched:
                    matched.images = [local_path]
                    matched.review_count = max(matched.review_count or 0, item.review_count)
                    if not matched.tags:
                        matched.tags = infer_spot_tags(matched.name, config.name)
                    if not matched.description:
                        matched.description = build_spot_description(config.name, matched.name)
                    if not matched.category:
                        matched.category = infer_spot_category(matched.name)
                    continue

                if city_spot_count >= TARGET_MIN_SPOTS:
                    continue

                new_spot = ScenicSpot(
                    name=item.name,
                    description=build_spot_description(config.name, item.name),
                    address=f"{config.name}\u5e02",
                    city=config.name,
                    category=infer_spot_category(item.name),
                    type="scenic",
                    rating=max(4.5, 4.9 - index * 0.1),
                    heat_score=max(8000, min(9999, 9500 - index * 180 + item.review_count // 8)),
                    review_count=item.review_count,
                    open_time="\u4ee5\u666f\u533a\u5b9e\u9645\u516c\u544a\u4e3a\u51c6",
                    ticket_price="\u4ee5\u666f\u533a\u5b9e\u9645\u4fe1\u606f\u4e3a\u51c6",
                    images=[local_path],
                    tags=infer_spot_tags(item.name, config.name),
                )
                db.add(new_spot)
                db.flush()
                city_spots.append(new_spot)
                city_spot_count += 1
                inserted_spot = True

            if inserted_spot:
                db.commit()
                city_spots = list(db.query(ScenicSpot).filter(ScenicSpot.city == config.name).all())
            else:
                db.flush()

            primary_spot = (
                db.query(ScenicSpot)
                .filter(ScenicSpot.city == config.name)
                .order_by(ScenicSpot.heat_score.desc(), ScenicSpot.rating.desc(), ScenicSpot.id.asc())
                .first()
            )
            if not primary_spot:
                db.commit()
                continue

            city_foods = (
                db.query(Restaurant)
                .join(ScenicSpot, ScenicSpot.id == Restaurant.spot_id)
                .filter(ScenicSpot.city == config.name)
                .all()
            )

            for index, item in enumerate(foods):
                display_name = FOOD_NAME_OVERRIDES.get((config.name, item.name), item.name)
                matched = find_matching_food(city_foods, display_name)
                extension = local_extension(item.image_url)
                disk_path = IMAGES_ROOT / "foods" / f"{config.slug}_{item.ref_id}{extension}"
                local_path = f"/images/foods/{config.slug}_{item.ref_id}{extension}"
                download_image(session, item.image_url, disk_path)

                if matched:
                    matched.images = [local_path]
                    matched.rating = max(matched.rating or 0, 4.6 - index * 0.05)
                    matched.heat_score = max(matched.heat_score or 0, 9200 - index * 180)
                    if not matched.cuisine_type:
                        matched.cuisine_type = infer_food_cuisine(config.name, display_name)
                    if not matched.price_range:
                        matched.price_range = infer_food_price(display_name)
                    if not matched.tags:
                        matched.tags = infer_food_tags(display_name)
                    continue

                new_food = Restaurant(
                    spot_id=primary_spot.id,
                    name=display_name,
                    cuisine_type=infer_food_cuisine(config.name, display_name),
                    rating=max(4.5, 4.9 - index * 0.1),
                    heat_score=9300 - index * 180,
                    price_range=infer_food_price(display_name),
                    open_time="\u4ee5\u5546\u5bb6\u5b9e\u9645\u8425\u4e1a\u65f6\u95f4\u4e3a\u51c6",
                    images=[local_path],
                    tags=infer_food_tags(display_name),
                )
                db.add(new_food)
                db.flush()
                city_foods.append(new_food)

            db.commit()
            time.sleep(0.3)
    finally:
        db.close()


if __name__ == "__main__":
    main()
