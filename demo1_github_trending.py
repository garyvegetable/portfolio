#!/usr/bin/env python3
"""
GitHub Trending 爬虫 - 采集编程语言排行榜数据
输出: JSON + CSV 格式
"""
import requests
import json
import csv
import time
from datetime import datetime

def scrape_github_trending(language="python", limit=20):
    """采集 GitHub Trending 指定语言的热门项目"""
    url = f"https://api.github.com/search/repositories"
    params = {
        "q": f"language:{language} created:>2024-01-01",
        "sort": "stars",
        "order": "desc",
        "per_page": limit
    }
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GaryPortfolio-Scraper"
    }
    
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    
    results = []
    for item in data.get("items", []):
        results.append({
            "rank": len(results) + 1,
            "name": item["full_name"],
            "description": item.get("description") or "",
            "language": item.get("language") or language,
            "stars": item["stargazers_count"],
            "forks": item["forks_count"],
            "url": item["html_url"],
            "created": item["created_at"][:10],
        })
    return results

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_csv(data, path):
    if not data:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    print("=== GitHub Trending 爬虫 ===")
    
    languages = ["python", "javascript", "go"]
    all_data = {}
    
    for lang in languages:
        print(f"采集 {lang} 热门项目...")
        try:
            results = scrape_github_trending(language=lang, limit=10)
            all_data[lang] = results
            print(f"  获取 {len(results)} 个项目")
            time.sleep(3)  # 避免触发限流
        except Exception as e:
            print(f"  失败: {e}")
            all_data[lang] = []
    
    # 保存结果
    save_json(all_data, "/home/peachy/.openclaw/workspace/portfolio/demo1_github_trending.json")
    print("\n=== Python Top 5 ===")
    for p in all_data.get("python", [])[:5]:
        print(f"  #{p['rank']} {p['name']} ⭐{p['stars']} - {p['description'][:50]}")
    
    print(f"\n数据已保存: demo1_github_trending.json")
