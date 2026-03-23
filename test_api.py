#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API返回数据
"""
import requests
import json

def test_api():
    url = "http://localhost:8000/api/spots/recommend?city=北京"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        print(f"Total: {data.get('total')}")
        print(f"Spots count: {len(data.get('spots', []))}")
        print("\n前15个景点:")
        for i, spot in enumerate(data.get('spots', [])[:15]):
            print(f"  {i+1}. {spot['name']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
