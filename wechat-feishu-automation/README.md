# 📰 微信公众号飞书同步系统

微信公众号文章爬虫 - 自动采集并同步到飞书多维表格

## 功能特性

- ✅ **Playwright 支持** - 无头/有头模式可选
- ✅ **完整字段提取** - 标题、作者、发布时间、正文、封面图、链接、采集时间
- ✅ **正文清洗** - 去除广告、关注引导、多余换行和冗余内容
- ✅ **飞书同步** - 自动同步到飞书多维表格
- ✅ **去重检查** - 飞书已存在则跳过
- ✅ **Excel 导出** - 支持 `--no-feishu` 只导出 Excel
- ✅ **批量爬取** - 支持文本文件批量处理
- ✅ **完整日志** - 实时输出爬取进度

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

## 安装

### 1. 安装依赖

```bash
pip install playwright
playwright install chromium
```

### 2. 配置环境变量

```bash
export FEISHU_APP_ID="your-app-id"
export FEISHU_APP_SECRET="your-app-secret"
export FEISHU_ACCESS_TOKEN="your-access-token"
```

## 使用方法

### 基本用法

```bash
# 爬取单篇文章
python main.py "https://mp.weixin.qq.com/s/xxx"

# 有头模式（调试用，显示浏览器）
python main.py "https://mp.weixin.qq.com/s/xxx" --headed

# 不同步飞书，只导出 Excel
python main.py "https://mp.weixin.qq.com/s/xxx" --no-feishu

# 指定输出目录
python main.py "https://mp.weixin.qq.com/s/xxx" --output ./output
```

### 批量爬取

```bash
# 创建链接文件 urls.txt
# 每行一个链接，# 开头的行为注释
https://mp.weixin.qq.com/s/xxx1
https://mp.weixin.qq.com/s/xxx2
# https://mp.weixin.qq.com/s/xxx3  # 注释行会被跳过

# 批量爬取
python main.py -f urls.txt

# 批量爬取，不同步飞书
python main.py -f urls.txt --no-feishu
```

### 飞书同步

```bash
# 指定飞书表格 ID
python main.py "https://mp.weixin.qq.com/s/xxx" --feishu-table-id xxxxxx

# 导出 JSON 结果
python main.py "https://mp.weixin.qq.com/s/xxx" --json result.json
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `url` | 微信公众号文章链接 |
| `-f`, `--file` | 批量爬取，指定包含链接的文本文件 |
| `--headed` | 有头模式，显示浏览器窗口 |
| `--no-feishu` | 不同步飞书，只导出 Excel |
| `--feishu-table-id` | 飞书多维表格 ID |
| `--output` | 输出目录 (默认: ./output) |
| `--json` | 导出 JSON 文件名 |

## 项目结构

```
wechat-feishu-automation/
├── SKILL.md                  # Skill 主文档
├── README.md                 # 本文件
├── scripts/
│   ├── main.py              # 主程序入口
│   └── wechat_scraper.py    # 爬虫核心模块
└── prompts/
    └── extractor.md         # 内容提取提示词
```

## 运行环境

- Python 3.8+
- Playwright
- 飞书多维表格权限

## License

MIT License

## Contributing

欢迎提交 Issue 和 Pull Request！
