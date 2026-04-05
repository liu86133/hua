---
name: wechat-feishu-automation
description: 微信公众号文章爬虫 - 自动采集并同步到飞书多维表格
metadata:
  openclaw:
    emoji: "📰"
---

# 微信公众号飞书同步系统

微信公众号文章爬取 → 数据清洗 → 飞书多维表格同步

## 触发方式

```
@机器人 爬取 https://mp.weixin.qq.com/s/xxx
@机器人 批量爬取 [公众号名称]
```

## 飞书表格字段

| 字段名 | 描述 |
|--------|------|
| 标题 | 文章标题 |
| 作者 | 公众号名称 |
| 发布时间 | 文章发布时间 |
| 正文 | 清洗后的正文内容 |
| 封面图 | 文章封面图片URL |
| 原文链接 | 原始文章链接 |
| 采集时间 | 爬取时间 |

## 功能特性

- ✅ Playwright 支持无头/有头模式
- ✅ 正文清洗：去广告、去关注引导、去冗余换行
- ✅ 支持 `--no-feishu` 只导出Excel
- ✅ 链接去重：飞书已存在则跳过
- ✅ 完整日志输出
- ✅ 异常捕获与重试机制

## 使用方法

```bash
# 爬取单篇文章
python main.py "https://mp.weixin.qq.com/s/xxx"

# 有头模式（调试）
python main.py "https://mp.weixin.qq.com/s/xxx" --headed

# 不同步飞书，只导出Excel
python main.py "https://mp.weixin.qq.com/s/xxx" --no-feishu

# 指定输出目录
python main.py "https://mp.weixin.qq.com/s/xxx" --output ./output
```

## 配置要求

- Python 3.8+
- Playwright
- 飞书多维表格权限
