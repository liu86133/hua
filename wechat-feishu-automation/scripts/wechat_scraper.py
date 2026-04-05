#!/usr/bin/env python3
"""
微信公众号文章爬虫
基于 Playwright 的微信公众号文章采集工具
"""

import json
import re
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright, Page, Browser


class WechatScraper:
    """微信公众号文章爬虫类"""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        初始化爬虫
        
        Args:
            headless: 是否无头模式运行
            timeout: 超时时间(毫秒)
        """
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        print(f"[wechat_scraper] 初始化爬虫 (headless={headless}, timeout={timeout}ms)")
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    def start(self):
        """启动浏览器"""
        print(f"[wechat_scraper] 启动浏览器...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        )
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        self.page = context.new_page()
        print(f"[wechat_scraper] 浏览器启动成功")
    
    def close(self):
        """关闭浏览器"""
        print(f"[wechat_scraper] 关闭浏览器...")
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        print(f"[wechat_scraper] 浏览器已关闭")
    
    def scrape(self, url: str) -> Dict[str, Any]:
        """
        爬取单篇文章
        
        Args:
            url: 文章链接
            
        Returns:
            dict: 包含文章信息的字典
        """
        result = {
            "title": "",
            "author": "",
            "publish_time": "",
            "content": "",
            "cover_image": "",
            "original_url": url,
            "scrape_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "failed",
            "error": ""
        }
        
        try:
            print(f"[wechat_scraper] 开始爬取: {url}")
            self.page.goto(url, timeout=self.timeout, wait_until="networkidle")
            
            # 等待页面加载
            self.page.wait_for_selector("#js_name", timeout=10000)
            
            # 提取公众号名称
            result["author"] = self._extract_author()
            print(f"[wechat_scraper] 提取作者: {result['author']}")
            
            # 提取标题
            result["title"] = self._extract_title()
            print(f"[wechat_scraper] 提取标题: {result['title']}")
            
            # 提取发布时间
            result["publish_time"] = self._extract_publish_time()
            print(f"[wechat_scraper] 提取发布时间: {result['publish_time']}")
            
            # 提取封面图
            result["cover_image"] = self._extract_cover_image()
            print(f"[wechat_scraper] 提取封面图: {result['cover_image'][:50]}..." if result["cover_image"] else "[wechat_scraper] 无封面图")
            
            # 提取正文
            result["content"] = self._extract_content()
            print(f"[wechat_scraper] 提取正文长度: {len(result['content'])} 字符")
            
            # 清洗正文
            result["content"] = self._clean_content(result["content"])
            print(f"[wechat_scraper] 清洗后正文长度: {len(result['content'])} 字符")
            
            result["status"] = "success"
            print(f"[wechat_scraper] 爬取成功!")
            
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "failed"
            print(f"[wechat_scraper] 爬取失败: {e}", file=sys.stderr)
        
        return result
    
    def _extract_author(self) -> str:
        """提取公众号名称"""
        try:
            author = self.page.locator("#js_name").inner_text()
            return author.strip()
        except Exception:
            return ""
    
    def _extract_title(self) -> str:
        """提取文章标题"""
        try:
            # 尝试多种选择器
            selectors = [
                "#activity-name",
                ".rich_media_title",
                "h1.title",
                "h1"
            ]
            for selector in selectors:
                if self.page.locator(selector).count() > 0:
                    return self.page.locator(selector).first.inner_text().strip()
            return ""
        except Exception:
            return ""
    
    def _extract_publish_time(self) -> str:
        """提取发布时间"""
        try:
            selectors = [
                "#publish_time",
                "#js_time_source",
                ".rich_media_meta rich_media_meta_text"
            ]
            for selector in selectors:
                if self.page.locator(selector).count() > 0:
                    time_text = self.page.locator(selector).first.inner_text().strip()
                    return self._parse_time(time_text)
            return ""
        except Exception:
            return ""
    
    def _parse_time(self, time_text: str) -> str:
        """解析时间文本"""
        # 匹配常见时间格式
        patterns = [
            r'(\d{4})[年\-\/](\d{1,2})[月\-\/](\d{1,2})',
            r'(\d{4})(\d{2})(\d{2})'
        ]
        for pattern in patterns:
            match = re.search(pattern, time_text)
            if match:
                groups = match.groups()
                return f"{groups[0]}-{groups[1].zfill(2)}-{groups[2].zfill(2)}"
        return time_text
    
    def _extract_cover_image(self) -> str:
        """提取封面图"""
        try:
            # 尝试从 meta 标签获取
            cover = self.page.locator('meta[property="og:image"]').get_attribute("content")
            if cover:
                return cover
            
            # 尝试从页面元素获取
            selectors = [
                "#js_cover",
                ".rich_media_title img",
                ".cover_img"
            ]
            for selector in selectors:
                if self.page.locator(selector).count() > 0:
                    img_src = self.page.locator(selector).first.get_attribute("src")
                    if img_src:
                        return img_src
            return ""
        except Exception:
            return ""
    
    def _extract_content(self) -> str:
        """提取正文内容"""
        try:
            selectors = [
                "#js_content",
                "#img-content",
                ".rich_media_content",
                ".article-content"
            ]
            for selector in selectors:
                if self.page.locator(selector).count() > 0:
                    return self.page.locator(selector).first.inner_html()
            return ""
        except Exception:
            return ""
    
    def _clean_content(self, html_content: str) -> str:
        """
        清洗正文内容
        
        去除：
        - 广告内容
        - 关注引导
        - 多余换行
        - 冗余标签
        """
        import html
        
        # HTML 转文本
        text = html_content
        
        # 移除 script 和 style 标签
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # 移除注释
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        
        # 移除关注引导类内容
        follow_patterns = [
            r'长按.*?识别.*?二维码',
            r'扫码.*?关注',
            r'关注.*?公众号',
            r'点击.*?关注',
            r'请.*?关注',
            r'转发.*?朋友圈',
            r'点亮.*?在看',
            r'喜欢.*?作者',
            r'设为.*?星标',
            r'阅读.*?原文',
            r'点击.*?链接',
            r'广告',
            r'商务合作',
        ]
        for pattern in follow_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # 移除多余空行和空格
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = text.strip()
        
        return text
    
    def is_article_exists(self, url: str, feishu_table_id: str = None) -> bool:
        """
        检查文章是否已存在于飞书表格
        
        Args:
            url: 文章链接
            feishu_table_id: 飞书表格ID
            
        Returns:
            bool: 是否已存在
        """
        if not feishu_table_id:
            return False
        
        # TODO: 实现飞书表格去重检查
        # 需要调用飞书多维表格 API 查询是否存在该链接
        return False


def scrape_wechat_article(url: str, headless: bool = True, output_path: str = None) -> dict:
    """
    爬取微信公众号文章的便捷函数
    
    Args:
        url: 文章链接
        headless: 是否无头模式
        output_path: 可选，保存JSON结果的文件路径
        
    Returns:
        dict: 包含文章信息的字典
    """
    with WechatScraper(headless=headless) as scraper:
        result = scraper.scrape(url)
        
        if output_path and result["status"] == "success":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"[wechat_scraper] 结果已保存到: {output_path}")
        
        return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python wechat_scraper.py <文章链接> [--headed]")
        print("示例: python wechat_scraper.py https://mp.weixin.qq.com/s/xxx")
        sys.exit(1)
    
    url = sys.argv[1]
    headless = "--headed" not in sys.argv
    
    result = scrape_wechat_article(url, headless=headless)
    print(json.dumps(result, ensure_ascii=False, indent=2))
