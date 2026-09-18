---
name: DailyGithub
description: "生成每日 GitHub 上升最快的 6 个开源项目介绍贴图。从 GitHub Trending 获取数据，生成一张精美的信息图，适合分享到社交媒体。"
---

# DailyGithub - 每日 GitHub 热门项目贴图生成器

## 功能

从 GitHub Trending 获取当日上升最快的开源项目，生成一张精美的信息图（1080x1920），包含 6 个项目的介绍。

## 使用方式

```bash
python3 skills/DailyGithub/generate.py
```

可选参数：
- `--output PATH`：指定输出路径（默认 `skills/DailyGithub/output/daily_github_YYYYMMDD.png`）
- `--include URL`：额外包含指定项目（如 `https://github.com/TencentCloud/Octop`）
- `--date YYYY-MM-DD`：指定日期（默认今天）

## 输出

一张 PNG 图片，包含：
- 标题和日期
- 6 个项目的排名、名称、描述、语言、星标数、今日新增星标
- 底部来源说明

## 数据来源

- GitHub Trending API（通过 web scraping）
- GitHub Repository API（获取详细信息）
