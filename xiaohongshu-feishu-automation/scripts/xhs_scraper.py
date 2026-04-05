#!/usr/bin/env python3
"""
小红书笔记爬虫脚本
使用 Playwright 自动化提取小红书笔记内容
"""

import json
import sys
import re
from playwright.sync_api import sync_playwright

def scrape_xiaohongshu(url: str, output_path: str = None) -> dict:
    """
    爬取小红书笔记内容
    
    Args:
        url: 小红书笔记链接
        output_path: 可选，保存JSON结果的文件路径
    
    Returns:
        dict: 包含笔记信息的字典
    """
    result = {
        "url": url,
        "title": "",
        "content": "",
        "images": [],
        "publish_time": "",
        "likes": 0,
        "comments": [],
        "views": 0
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        try:
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)
            
            # 提取标题
            try:
                # 尝试多种选择器
                selectors = [
                    ".note-content .title",
                    ".detail-desc",
                    "h1.title",
                    ".intro",
                ]
                for sel in selectors:
                    if page.locator(sel).count() > 0:
                        result["title"] = page.locator(sel).first.inner_text()
                        break
            except Exception:
                result["title"] = "标题提取失败"
            
            # 提取正文
            try:
                content_selectors = [
                    ".note-content .desc",
                    ".content",
                    ".desc",
                ]
                for sel in content_selectors:
                    if page.locator(sel).count() > 0:
                        result["content"] = page.locator(sel).first.inner_text()
                        break
            except Exception:
                result["content"] = "正文提取失败"
            
            # 提取图片
            try:
                img_selectors = [".note-content img", ".img-wrapper img", "img"]
                for sel in img_selectors:
                    imgs = page.locator(sel).all()
                    if imgs:
                        result["images"] = [img.get_attribute("src") for img in imgs if img.get_attribute("src")]
                        break
            except Exception:
                pass
            
            # 提取点赞数
            try:
                like_selectors = [".like-wrapper .count", ".like .count", "[class*=like]"]
                for sel in like_selectors:
                    if page.locator(sel).count() > 0:
                        likes_text = page.locator(sel).first.inner_text()
                        result["likes"] = int(re.sub(r'\D', '', likes_text))
                        break
            except Exception:
                pass
            
            # 提取评论需求
            try:
                comment_selectors = [".comment-list .comment-item", ".comments .item"]
                for sel in comment_selectors:
                    comments = page.locator(sel).all()
                    if comments:
                        result["comments"] = [c.inner_text() for c in comments[:20]]
                        break
            except Exception:
                pass
            
            # 提取阅读量
            try:
                view_selectors = [".count-wrapper .view", ".view .num"]
                for sel in view_selectors:
                    if page.locator(sel).count() > 0:
                        views_text = page.locator(sel).first.inner_text()
                        result["views"] = int(re.sub(r'\D', '', views_text))
                        break
            except Exception:
                pass
            
        except Exception as e:
            print(f"[xhs_scraper] 爬取失败: {e}", file=sys.stderr)
        
        finally:
            browser.close()
    
    # 保存结果
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"[xhs_scraper] 结果已保存到: {output_path}")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python xhs_scraper.py <小红书链接> [输出文件]")
        sys.exit(1)
    
    url = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = scrape_xiaohongshu(url, output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
