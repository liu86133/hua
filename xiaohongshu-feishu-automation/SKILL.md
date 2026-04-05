---
name: xiaohongshu-feishu-automation
description: 小红书运营自动化 - 爬取笔记、AI改写、一键发布到飞书多维表格
metadata:
  openclaw:
    emoji: "📕"
---

# 小红书运营自动化系统

飞书多维表格触发 → 小红书笔记爬取 → AI内容创作 → 一键发布

## 触发条件

当飞书多维表格「原文链接」字段填入小红书笔记URL时触发

## 飞书表格字段

| 字段名 | 操作 |
|--------|------|
| 原文链接 | 用户填入/自动爬取 |
| 原文标题 | 爬取原始标题 |
| 原文图片 | 爬取原始图片素材 |
| 原文正文 | 爬取原始正文内容 |
| 原文发布时间 | 爬取笔记发布时间 |
| 原文点赞数 | 爬取点赞数(纯数字) |
| 评论需求 | 提取评论中的用户需求 |
| 阅读数量 | 爬取阅读量(纯数字) |
| 仿写标题 | AI生成5-10个热门标题 |
| 修改图片 | AI优化后的图片 |
| 仿写正文 | AI生成原创正文 |
| 一键发布 | 复选框触发发布 |

## 步骤

### 步骤1：小红书内容爬取

使用浏览器自动化访问小红书链接：

```python
# scripts/xhs_scraper.py
from playwright.sync_api import sync_playwright

def scrape_xiaohongshu(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        
        # 提取标题
        title = page.locator(".note-content .title").inner_text()
        
        # 提取正文
        content = page.locator(".note-content .desc").inner_text()
        
        # 提取图片
        images = page.locator(".note-content .img-wrapper img").all_inner_texts()
        
        # 提取点赞数
        likes = page.locator(".like-wrapper .count").inner_text()
        
        # 提取评论需求
        comments = page.locator(".comment-list .comment-item").all_inner_texts()
        
        browser.close()
        return {
            "title": title,
            "content": content,
            "images": images,
            "likes": likes,
            "comments": comments
        }
```

### 步骤2：AI内容创作

#### 生成仿写标题

```bash
# 调用豆包API生成爆款标题
curl -X POST "https://ark.cn-beijing.volces.com/api/v3/chat/completions" \
  -H "Authorization: Bearer $DOUBAO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-pro-4k",
    "messages": [{
      "role": "user",
      "content": "你是小红书爆款标题专家，基于以下信息生成5-10个高点击率标题：\n原文标题：{title}\n原文正文：{content}\n用户评论需求：{comments}\n要求：每个标题15-30字，融入痛点/数字/情绪/悬念元素，保留核心主题。"
    }]
  }'
```

#### 生成仿写正文

```bash
# 调用豆包API生成原创正文
curl -X POST "https://ark.cn-beijing.volces.com/api/v3/chat/completions" \
  -H "Authorization: Bearer $DOUBAO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-pro-4k",
    "messages": [{
      "role": "user", 
      "content": "你是小红书爆款文案专家，基于以下信息生成1-3篇原创正文：\n原文正文：{content}\n用户评论需求：{comments}\n要求：100%原创，开头抓眼球，中间干货/情绪，结尾引导互动，加入话题标签#，语气亲切自然。"
    }]
  }'
```

### 步骤3：一键发布

当「一键发布」复选框勾选时：

1. 浏览器自动化登录小红书
2. 进入发布页面
3. 上传「修改图片」
4. 填入「仿写标题」和「仿写正文」
5. 添加话题标签
6. 点击发布
7. 同步结果到飞书表格

## 配置要求

- Playwright 浏览器自动化
- 豆包API Key (DOUBAO_API_KEY)
- 飞书多维表格权限
- 小红书账号cookies

## 使用示例

```
用户：在飞书表格填入 https://www.xiaohongshu.com/explore/xxx
Bot： 自动爬取 → AI创作 → 更新表格
用户：勾选「一键发布」
Bot： 自动发布到小红书 → 同步结果
```
