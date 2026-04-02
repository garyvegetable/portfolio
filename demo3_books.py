#!/usr/bin/env python3
"""
Books.toscrape 电商数据采集 - 演示 Playwright 动态渲染能力
输出: JSON + CSV
"""
import json
import csv
import asyncio
from datetime import datetime

async def scrape_books():
    """用 Playwright 采集书籍数据（JS渲染页面）"""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Playwright not installed, using requests fallback")
        return await scrape_books_requests()
    
    books = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 采集前3页
        for page_num in range(1, 4):
            url = f"http://books.toscrape.com/catalogue/category/books_1/page-{page_num}.html"
            print(f"  采集: {url}")
            await page.goto(url, wait_until="networkidle")
            
            # 等待书籍卡片加载
            await page.wait_for_selector("article.product_pod", timeout=10)
            
            # 提取数据
            items = await page.query_selector_all("article.product_pod")
            for item in items:
                title_elem = await item.query_selector("h3 a")
                price_elem = await item.query_selector(".price_color")
                rating_elem = await item.query_selector(".star-rating")
                img_elem = await item.query_selector("img")
                
                title = await title_elem.get_attribute("title") if title_elem else ""
                price = await price_elem.inner_text() if price_elem else ""
                rating = await rating_elem.get_attribute("class") if rating_elem else ""
                img = await img_elem.get_attribute("src") if img_elem else ""
                
                books.append({
                    "title": title,
                    "price": price.strip(),
                    "rating": rating.replace("star-rating ", "").strip(),
                    "image": "http://books.toscrape.com/" + img if img else "",
                    "page": page_num,
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
        
        await browser.close()
    
    return books

async def scrape_books_requests():
    """Fallback: 用 requests + BeautifulSoup"""
    import requests
    from bs4 import BeautifulSoup
    
    books = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; GaryPortfolio/1.0)"}
    
    for page_num in range(1, 4):
        url = f"http://books.toscrape.com/catalogue/category/books_1/page-{page_num}.html"
        print(f"  采集: {url}")
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        items = soup.select("article.product_pod")
        for item in items:
            title = item.select_one("h3 a")["title"]
            price = item.select_one(".price_color").text.strip()
            rating = item.select_one(".star-rating")["class"]
            books.append({
                "title": title,
                "price": price,
                "rating": " ".join(rating),
                "page": page_num,
            })
    
    return books

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
    print("=== 电商数据采集 (Playwright 动态渲染) ===")
    books = asyncio.run(scrape_books())
    
    print(f"\n共采集 {len(books)} 本书:")
    for b in books[:8]:
        print(f"  [{b['rating']}] {b['title'][:50]} - {b['price']}")
    
    save_json(books, "/home/peachy/.openclaw/workspace/portfolio/demo3_books.json")
    save_csv(books, "/home/peachy/.openclaw/workspace/portfolio/demo3_books.csv")
    print(f"\n数据已保存: demo3_books.json + demo3_books.csv")
