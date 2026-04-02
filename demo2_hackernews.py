#!/usr/bin/env python3
"""
Hacker News 新闻采集 - 采集实时科技热点
输出: JSON 格式
"""
import requests
from datetime import datetime
import json

def scrape_hackernews(top_n=20):
    """采集 Hacker News Top stories"""
    # 获取 Top Stories IDs
    resp = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json",
        timeout=15
    )
    story_ids = resp.json()[:top_n]
    
    stories = []
    for rank, story_id in enumerate(story_ids, 1):
        try:
            item_resp = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                timeout=10
            )
            item = item_resp.json()
            
            if item and item.get("type") == "story":
                stories.append({
                    "rank": rank,
                    "title": item.get("title", ""),
                    "url": item.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                    "score": item.get("score", 0),
                    "by": item.get("by", ""),
                    "comments": item.get("descendants", 0),
                    "time": datetime.fromtimestamp(item.get("time", 0)).strftime("%Y-%m-%d %H:%M"),
                })
        except Exception as e:
            print(f"  Story {story_id} failed: {e}")
    
    return stories

if __name__ == "__main__":
    print("=== Hacker News 爬虫 ===")
    stories = scrape_hackernews(15)
    
    print(f"\n获取 {len(stories)} 条热门新闻:\n")
    for s in stories[:10]:
        print(f"  #{s['rank']} [{s['score']}👍] {s['title'][:60]}")
        print(f"        by {s['by']} | {s['comments']} comments")
    
    # 按分数排序
    by_score = sorted(stories, key=lambda x: x["score"], reverse=True)[:5]
    print(f"\n=== 热度 Top 5 ===")
    for s in by_score:
        print(f"  [{s['score']}👍] {s['title'][:60]}")
    
    output = {
        "source": "Hacker News",
        "url": "https://news.ycombinator.com",
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": len(stories),
        "stories": stories
    }
    
    with open("/home/peachy/.openclaw/workspace/portfolio/demo2_hackernews.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据已保存: demo2_hackernews.json")
