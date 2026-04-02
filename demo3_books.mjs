#!/usr/bin/env node
/**
 * 电商数据采集 - Playwright 动态渲染演示
 * 目标: books.toscrape.com (专门用于爬虫练习的安全站点)
 */
import { chromium } from '/home/peachy/.openclaw/workspace/node_modules/playwright/index.mjs';
import { writeFileSync } from 'fs';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

const allBooks = [];

console.log('=== 电商数据采集 (Playwright 动态渲染) ===');

for (let pageNum = 1; pageNum <= 3; pageNum++) {
    const url = `http://books.toscrape.com/catalogue/category/books_1/page-${pageNum}.html`;
    console.log(`  采集: ${url}`);
    
    await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 });
    
    // 等待书籍卡片
    await page.waitForSelector('article.product_pod', { timeout: 10000 }).catch(() => {});
    
    // 提取书籍数据
    const books = await page.evaluate(() => {
        const items = document.querySelectorAll('article.product_pod');
        return Array.from(items).map(item => {
            const title = item.querySelector('h3 a')?.getAttribute('title') || '';
            const price = item.querySelector('.price_color')?.textContent?.trim() || '';
            const rating = item.querySelector('.star-rating')?.className?.replace('star-rating', '').trim() || '';
            const img = item.querySelector('img')?.getAttribute('src') || '';
            return { title, price, rating: rating.replace('star-rating', '').trim(), image: img };
        });
    });
    
    console.log(`    获取 ${books.length} 本书`);
    allBooks.push(...books.map(b => ({ ...b, page: pageNum })));
}

await browser.close();

console.log(`\n共采集 ${allBooks.length} 本书`);
console.log('\n示例数据:');
allBooks.slice(0, 6).forEach(b => {
    console.log(`  [${b.rating}] ${b.title.substring(0, 50)} - ${b.price}`);
});

// 保存 JSON
writeFileSync('/home/peachy/.openclaw/workspace/portfolio/demo3_books.json', 
    JSON.stringify({ source: 'books.toscrape.com', total: allBooks.length, books: allBooks }, null, 2));
console.log('\n数据已保存: demo3_books.json');
