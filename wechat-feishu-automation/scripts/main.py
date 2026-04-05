#!/usr/bin/env python3
"""
微信公众号爬虫主程序
支持飞书同步、Excel导出、去重检查
"""

import argparse
import json
import os
import sys
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from wechat_scraper import WechatScraper, scrape_wechat_article


class WechatFeishuCrawler:
    """微信公众号飞书同步爬虫"""
    
    def __init__(self, headless: bool = True, feishu_token: str = None):
        """
        初始化爬虫
        
        Args:
            headless: 是否无头模式
            feishu_token: 飞书 Access Token
        """
        self.headless = headless
        self.feishu_token = feishu_token
        self.results: List[Dict[str, Any]] = []
        self.output_dir = Path("./output")
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[wechat_crawler] 初始化完成 (headless={headless})")
    
    def crawl(self, url: str, no_feishu: bool = False, feishu_table_id: str = None) -> Dict[str, Any]:
        """
        爬取单篇文章
        
        Args:
            url: 文章链接
            no_feishu: 是否跳过飞书同步
            feishu_table_id: 飞书表格ID
            
        Returns:
            dict: 爬取结果
        """
        print(f"\n{'='*50}")
        print(f"[wechat_crawler] 开始爬取: {url}")
        print(f"[wechat_crawler] 飞书同步: {'禁用' if no_feishu else '启用'}")
        print(f"{'='*50}")
        
        result = {
            "url": url,
            "status": "failed",
            "data": None,
            "feishu_synced": False,
            "error": ""
        }
        
        try:
            # 爬取文章
            with WechatScraper(headless=self.headless) as scraper:
                article_data = scraper.scrape(url)
            
            if article_data["status"] == "failed":
                result["error"] = article_data.get("error", "爬取失败")
                return result
            
            result["data"] = article_data
            result["status"] = "success"
            
            # 检查去重
            if feishu_table_id and not no_feishu:
                if self._check_duplicate(url, feishu_table_id):
                    print(f"[wechat_crawler] 文章已存在，跳过: {url}")
                    result["status"] = "duplicate"
                    return result
            
            # 保存 Excel
            excel_path = self._save_to_excel([article_data])
            print(f"[wechat_crawler] Excel 已保存: {excel_path}")
            
            # 同步飞书
            if not no_feishu:
                feishu_result = self._sync_to_feishu(article_data, feishu_table_id)
                result["feishu_synced"] = feishu_result
                if feishu_result:
                    print(f"[wechat_crawler] 飞书同步成功")
                else:
                    print(f"[wechat_crawler] 飞书同步失败")
            
            self.results.append(result)
            
        except Exception as e:
            result["error"] = str(e)
            print(f"[wechat_crawler] 爬取出错: {e}", file=sys.stderr)
        
        return result
    
    def crawl_batch(self, urls: List[str], no_feishu: bool = False, feishu_table_id: str = None) -> List[Dict[str, Any]]:
        """
        批量爬取
        
        Args:
            urls: 文章链接列表
            no_feishu: 是否跳过飞书同步
            feishu_table_id: 飞书表格ID
            
        Returns:
            list: 爬取结果列表
        """
        print(f"\n{'='*50}")
        print(f"[wechat_crawler] 开始批量爬取，共 {len(urls)} 篇文章")
        print(f"{'='*50}")
        
        results = []
        for i, url in enumerate(urls, 1):
            print(f"\n>>> [{i}/{len(urls)}] 正在爬取...")
            result = self.crawl(url, no_feishu, feishu_table_id)
            results.append(result)
            
            # 间隔 3 秒，避免请求过快
            if i < len(urls):
                import time
                time.sleep(3)
        
        # 统计
        success_count = sum(1 for r in results if r["status"] == "success")
        failed_count = sum(1 for r in results if r["status"] == "failed")
        duplicate_count = sum(1 for r in results if r["status"] == "duplicate")
        
        print(f"\n{'='*50}")
        print(f"[wechat_crawler] 批量爬取完成")
        print(f"[wechat_crawler] 成功: {success_count}, 失败: {failed_count}, 重复: {duplicate_count}")
        print(f"{'='*50}")
        
        return results
    
    def _check_duplicate(self, url: str, feishu_table_id: str) -> bool:
        """
        检查文章是否已存在
        
        Args:
            url: 文章链接
            feishu_table_id: 飞书表格ID
            
        Returns:
            bool: 是否已存在
        """
        # TODO: 实现飞书表格去重检查
        # 需要调用飞书多维表格 API
        print(f"[wechat_crawler] 去重检查: {url}")
        return False
    
    def _sync_to_feishu(self, article_data: Dict[str, Any], feishu_table_id: str = None) -> bool:
        """
        同步数据到飞书多维表格
        
        Args:
            article_data: 文章数据
            feishu_table_id: 飞书表格ID
            
        Returns:
            bool: 是否同步成功
        """
        if not feishu_table_id:
            print(f"[wechat_crawler] 未指定飞书表格，跳过同步")
            return False
        
        # TODO: 实现飞书多维表格 API 同步
        # 需要：
        # 1. 获取 Access Token
        # 2. 获取表格记录
        # 3. 批量创建记录
        
        print(f"[wechat_crawler] 准备同步到飞书...")
        print(f"[wechat_crawler] 标题: {article_data.get('title', 'N/A')}")
        print(f"[wechat_crawler] 作者: {article_data.get('author', 'N/A')}")
        print(f"[wechat_crawler] 链接: {article_data.get('original_url', 'N/A')}")
        
        # 占位：实际需要调用飞书 API
        return False
    
    def _save_to_excel(self, articles: List[Dict[str, Any]], filename: str = None) -> str:
        """
        保存数据到 Excel
        
        Args:
            articles: 文章列表
            filename: 文件名
            
        Returns:
            str: 保存路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wechat_articles_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        # CSV 格式保存
        fieldnames = [
            "标题", "作者", "发布时间", "正文", 
            "封面图", "原文链接", "采集时间"
        ]
        
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for article in articles:
                writer.writerow({
                    "标题": article.get("title", ""),
                    "作者": article.get("author", ""),
                    "发布时间": article.get("publish_time", ""),
                    "正文": article.get("content", ""),
                    "封面图": article.get("cover_image", ""),
                    "原文链接": article.get("original_url", ""),
                    "采集时间": article.get("scrape_time", "")
                })
        
        return str(filepath)
    
    def export_json(self, filename: str = None) -> str:
        """
        导出结果为 JSON
        
        Args:
            filename: 文件名
            
        Returns:
            str: 保存路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wechat_export_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"[wechat_crawler] JSON 已导出: {filepath}")
        return str(filepath)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="微信公众号文章爬虫 - 支持飞书同步",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py "https://mp.weixin.qq.com/s/xxx"
  python main.py "https://mp.weixin.qq.com/s/xxx" --headed
  python main.py "https://mp.weixin.qq.com/s/xxx" --no-feishu
  python main.py -f urls.txt
  python main.py "https://mp.weixin.qq.com/s/xxx" --feishu-table-id xxxxxx
        """
    )
    
    parser.add_argument(
        "url",
        nargs="?",
        help="微信公众号文章链接"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="批量爬取，指定包含链接的文件路径"
    )
    
    parser.add_argument(
        "--headed",
        action="store_true",
        help="有头模式（显示浏览器窗口）"
    )
    
    parser.add_argument(
        "--no-feishu",
        action="store_true",
        help="不同步飞书，只导出 Excel"
    )
    
    parser.add_argument(
        "--feishu-table-id",
        help="飞书多维表格 ID"
    )
    
    parser.add_argument(
        "--output",
        default="./output",
        help="输出目录 (默认: ./output)"
    )
    
    parser.add_argument(
        "--json",
        help="导出 JSON 文件名"
    )
    
    args = parser.parse_args()
    
    # 参数校验
    if not args.url and not args.file:
        parser.print_help()
        print("\n错误: 请提供文章链接或链接文件")
        sys.exit(1)
    
    # 初始化爬虫
    crawler = WechatFeishuCrawler(
        headless=not args.headed,
        feishu_token=os.getenv("FEISHU_ACCESS_TOKEN")
    )
    
    # 设置输出目录
    crawler.output_dir = Path(args.output)
    crawler.output_dir.mkdir(parents=True, exist_ok=True)
    
    # 执行爬取
    if args.url:
        # 单篇爬取
        result = crawler.crawl(
            url=args.url,
            no_feishu=args.no_feishu,
            feishu_table_id=args.feishu_table_id
        )
        
        if result["status"] == "success":
            print(f"\n✓ 爬取成功!")
            print(f"  标题: {result['data']['title']}")
            print(f"  作者: {result['data']['author']}")
            print(f"  飞书同步: {'成功' if result['feishu_synced'] else '失败/跳过'}")
        else:
            print(f"\n✗ 爬取失败: {result['error']}")
    
    elif args.file:
        # 批量爬取
        if not os.path.exists(args.file):
            print(f"错误: 文件不存在: {args.file}")
            sys.exit(1)
        
        with open(args.file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        results = crawler.crawl_batch(
            urls=urls,
            no_feishu=args.no_feishu,
            feishu_table_id=args.feishu_table_id
        )
    
    # 导出 JSON
    if args.json:
        crawler.export_json(args.json)
    
    print(f"\n[wechat_crawler] 完成!")


if __name__ == "__main__":
    main()
