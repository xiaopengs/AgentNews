#!/usr/bin/env python3
"""DailyGithub - 每日 GitHub 热门项目贴图生成器

从 GitHub Trending 获取当日上升最快的 6 个开源项目，
生成一张精美的信息图（1080x1920），适合分享到社交媒体。

版式严格 1:1 还原目标模板：奶油底色、GitHub 头部、暖色插画横幅、
带序号方块+Logo+标签+火焰徽章的卡片、底部山丘插画。
"""

import argparse
import math
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

# ── 配置 ───────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
ASSET_DIR = BASE_DIR / "assets"
TODAY = datetime.now().strftime("%Y-%m-%d")
TODAY_SHORT = datetime.now().strftime("%Y%m%d")
WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
WEEKDAY = WEEKDAYS[datetime.now().weekday()]

IMG_W = 1080
IMG_H = 1920

# 颜色方案 - 还原模板的暖奶油配色
C = {
    "bg": (246, 242, 233),           # 奶油底
    "card_bg": (255, 255, 255),
    "card_border": (236, 230, 218),
    "shadow": (224, 216, 200),
    "text_dark": (35, 32, 28),       # 近黑
    "text_mid": (110, 105, 98),      # 灰
    "text_gray": (150, 146, 138),
    "text_white": (255, 255, 255),
    "hero_text": (70, 52, 30),       # 手写深棕
    "banner_bg1": (250, 240, 214),
    "banner_bg2": (247, 233, 200),
    "banner_border": (238, 224, 190),
    "tag_bg": (240, 238, 233),
    "tag_text": (120, 116, 108),
    "logo_tile": (30, 41, 59),       # 深色 logo 底
    "lang_dot": (56, 189, 120),
}

# 序号方块配色（还原模板：黄/蓝/橙/蓝/绿/紫）
RANK_COLORS = [
    (245, 166, 35),
    (59, 130, 246),
    (249, 115, 22),
    (59, 130, 246),
    (34, 197, 94),
    (139, 92, 246),
]

# 语言点颜色
LANG_COLORS = {
    "Python": (56, 118, 223),
    "JavaScript": (241, 200, 40),
    "TypeScript": (49, 120, 198),
    "Go": (0, 173, 215),
    "Rust": (222, 110, 50),
    "Java": (220, 130, 50),
    "C++": (100, 150, 220),
    "HTML": (227, 76, 38),
    "CSS": (86, 61, 124),
    "Shell": (89, 129, 82),
}

FONT_DIR = "/usr/share/fonts/opentype/noto"
FONT_BOLD = os.path.join(FONT_DIR, "NotoSerifCJK-Bold.ttc")
FONT_REGULAR = os.path.join(FONT_DIR, "NotoSansCJK-Regular.ttc")

# 常见开源项目中文描述数据库
CURATED_DESCRIPTIONS = {
    "TencentCloud/Octop": "腾讯云推出的智能 AI 助手平台，支持多用户、多 Agent 协作，可私有化部署，适合企业级智能对话场景。",
    "cloudflare/security-audit-skill": "Cloudflare 推出的安全审计 Agent 技能，支持多阶段安全审计，可独立验证并生成机器可读的安全发现报告。",
    "alibaba/open-code-review": "阿里巴巴开源的代码审查工具，采用混合架构（确定性流水线 + LLM Agent），支持多语言规则集，涵盖 NPE、线程安全、XSS、SQL 注入等检测，兼容 OpenAI 和 Anthropic 模型。",
    "Tencent/BrowserSkill": "腾讯推出的浏览器自动化技能，让 AI Agent 使用真实登录态浏览器执行操作，不干扰用户工作，支持 CLI 和扩展两种模式。",
    "affaan-m/ECC": "Agent 性能优化系统，提供技能、直觉、记忆、安全等模块，支持 Claude Code、Codex、Opencode、Cursor 等主流 AI 编程工具。",
    "Tencent/WeKnora": "腾讯开源的 LLM 知识平台，可将原始文档转化为可查询的 RAG 系统，具备自主推理 Agent 和自我维护 Wiki 能力。",
    "langchain-ai/langchain": "最流行的 LLM 应用开发框架，提供链式调用、Agent、RAG 等核心能力，生态丰富，社区活跃。",
    "openai/openai-python": "OpenAI 官方 Python SDK，提供 GPT、DALL·E、Whisper 等模型的统一调用接口。",
    "microsoft/TypeScript": "微软开发的 JavaScript 超集，添加静态类型系统，大幅提升大型项目的可维护性和开发体验。",
    "rust-lang/rust": "注重安全、并发和性能的系统编程语言，零成本抽象和无垃圾回收是其核心特色。",
    "pytorch/pytorch": "Meta 开源的深度学习框架，以动态计算图和 Python 友好著称，是学术研究的首选框架。",
    "tensorflow/tensorflow": "Google 开源的端到端机器学习平台，支持从训练到部署的全流程，适合生产环境大规模应用。",
    "huggingface/transformers": "HuggingFace 推出的 NLP 模型库，提供数千个预训练模型的统一接口，覆盖文本、图像、语音等多模态任务。",
    "vercel/next.js": "React 全栈框架，支持服务端渲染、静态生成和 API 路由，是构建现代 Web 应用的主流选择。",
    "docker/compose": "Docker 官方多容器编排工具，通过 YAML 文件定义和运行多容器应用，简化微服务开发流程。",
    "kubernetes/kubernetes": "Google 开源的容器编排平台，自动化部署、扩展和管理容器化应用，是云原生基础设施的核心。",
    "ansible/ansible": "Red Hat 开源的自动化运维工具，无需 Agent 即可管理数千台服务器，支持配置管理、应用部署和任务编排。",
    "grafana/grafana": "开源的可观测性平台，支持多数据源可视化监控和告警，是 DevOps 团队的标配工具。",
    "prometheus/prometheus": "CNCF 毕业项目，开源的监控系统和时序数据库，通过 Pull 模型采集指标，是云原生监控的事实标准。",
    "elastic/elasticsearch": "开源的分布式搜索和分析引擎，基于 Lucene 构建，支持全文搜索、结构化搜索和分析，广泛用于日志和数据分析。",
    "apache/kafka": "LinkedIn 开源的分布式流处理平台，高吞吐、低延迟，是事件驱动架构和实时数据管道的核心组件。",
    "redis/redis": "开源的内存数据结构存储，支持字符串、哈希、列表、集合等多种数据类型，广泛用于缓存、会话和消息队列。",
    "nginx/nginx": "高性能 HTTP 和反向代理服务器，以高并发、低内存著称，是全球使用最广泛的 Web 服务器之一。",
    "postgres/postgres": "世界上最先进的开源关系型数据库，支持 JSON、全文搜索、地理信息等扩展，是复杂业务场景的首选。",
    "mongodb/mongo": "开源的文档型 NoSQL 数据库，灵活的 Schema 设计和强大的查询能力，适合快速迭代的应用开发。",
}

# 项目标签（用于卡片底部标签行）
CURATED_TAGS = {
    "TencentCloud/Octop": ["AI", "大模型", "企业级", "Agent"],
    "cloudflare/security-audit-skill": ["Security", "Audit", "Cloudflare", "Agent"],
    "alibaba/open-code-review": ["Code Review", "AI", "Security", "Alibaba"],
    "Tencent/BrowserSkill": ["Browser", "Automation", "AI", "TypeScript"],
    "affaan-m/ECC": ["Performance", "Agent", "LLM", "Developer Tools"],
    "Tencent/WeKnora": ["RAG", "LLM", "Knowledge", "Tencent"],
}

# 项目 Logo 图标类型
LOGO_GLYPHS = {
    "TencentCloud/Octop": "cloud",
    "cloudflare/security-audit-skill": "cloud",
    "alibaba/open-code-review": "letters",
    "Tencent/BrowserSkill": "person",
    "affaan-m/ECC": "code",
    "Tencent/WeKnora": "waves",
}

# Logo 方块底色
LOGO_TILES = {
    "TencentCloud/Octop": (30, 41, 59),
    "cloudflare/security-audit-skill": (249, 122, 24),
    "alibaba/open-code-review": (255, 106, 0),
    "Tencent/BrowserSkill": (37, 99, 235),
    "affaan-m/ECC": (30, 41, 59),
    "Tencent/WeKnora": (30, 41, 59),
}


def translate_description(full_name, english_desc):
    if full_name in CURATED_DESCRIPTIONS:
        return CURATED_DESCRIPTIONS[full_name]
    for key, value in CURATED_DESCRIPTIONS.items():
        if key.lower() == full_name.lower():
            return value
    return english_desc


def get_tags(full_name):
    if full_name in CURATED_TAGS:
        return CURATED_TAGS[full_name]
    for key, value in CURATED_TAGS.items():
        if key.lower() == full_name.lower():
            return value
    return []


# ─── 数据获取 ─────────────────────────────────────────────────────────────────

def fetch_github_trending():
    url = "https://github.com/trending"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        html = resp.text
    except requests.RequestException as e:
        print(f"[ERROR] 无法访问 GitHub Trending: {e}")
        return []

    article_pattern = re.compile(r'<article class="Box-row".*?</article>', re.DOTALL)
    articles = article_pattern.findall(html)

    projects = []
    for article in articles:
        project = parse_article(article)
        if project:
            projects.append(project)
        if len(projects) >= 30:
            break
    return projects


def parse_article(article_html):
    project = {}
    h2_match = re.search(r'<h2[^>]*>.*?<a[^>]*href="(/[^/"]+/[^"]+)"', article_html, re.DOTALL)
    if not h2_match:
        return None
    repo_path = h2_match.group(1).strip()
    if "login" in repo_path:
        return None

    project["full_name"] = repo_path.lstrip("/")
    project["name"] = repo_path.split("/")[-1]
    project["owner"] = repo_path.split("/")[1] if "/" in repo_path else ""

    desc_match = re.search(r'<p[^>]*>(.*?)</p>', article_html, re.DOTALL)
    if desc_match:
        desc = desc_match.group(1).strip()
        desc = re.sub(r'<svg[^>]*>.*?</svg>', '', desc, flags=re.DOTALL)
        desc = re.sub(r'<button[^>]*>.*?</button>', '', desc, flags=re.DOTALL)
        desc = re.sub(r'<details[^>]*>.*?</details>', '', desc, flags=re.DOTALL)
        desc = re.sub(r'<a[^>]*>.*?</a>', '', desc, flags=re.DOTALL)
        desc = re.sub(r'<[^>]+>', ' ', desc)
        desc = re.sub(r'\s+', ' ', desc).strip()
        if desc.startswith("Star "):
            desc = desc[5:]
        if desc.startswith("Sponsor "):
            desc = desc[8:]
        repo_prefix = f"{project['owner']} / {project['name']} "
        if desc.startswith(repo_prefix):
            desc = desc[len(repo_prefix):]
        project["description"] = desc
    else:
        project["description"] = "暂无描述"

    lang_match = re.search(r'<span itemprop="programmingLanguage">(.*?)</span>', article_html)
    project["language"] = lang_match.group(1).strip() if lang_match else "Unknown"

    stars_section = re.search(r'href="[^"]*/stargazers".*?</a>', article_html, re.DOTALL)
    project["stars"] = 0
    if stars_section:
        num_match = re.search(r'<svg.*?</svg>\s*([\d,]+)', stars_section.group(), re.DOTALL)
        if num_match:
            project["stars"] = int(num_match.group(1).replace(",", ""))

    today_match = re.search(r'([\d,]+)\s+stars\s+today', article_html)
    project["today_stars"] = 0
    if today_match:
        project["today_stars"] = int(today_match.group(1).replace(",", ""))

    fork_section = re.search(r'href="[^"]*/forks".*?</a>', article_html, re.DOTALL)
    project["forks"] = 0
    if fork_section:
        num_match = re.search(r'<svg.*?</svg>\s*([\d,]+)', fork_section.group(), re.DOTALL)
        if num_match:
            project["forks"] = int(num_match.group(1).replace(",", ""))

    return project


def fetch_repo_details(repo_path):
    url = f"https://api.github.com/repos/{repo_path}"
    headers = {"User-Agent": "DailyGithub-Bot/1.0", "Accept": "application/vnd.github.v3+json"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "description": data.get("description") or "暂无描述",
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "language": data.get("language") or "Unknown",
                "topics": data.get("topics", []),
            }
    except requests.RequestException:
        pass
    return None


def select_top_projects(projects, include_url=None):
    projects.sort(key=lambda p: p.get("today_stars", 0), reverse=True)
    selected = []
    if include_url:
        include_path = include_url.replace("https://github.com/", "").rstrip("/")
        found = False
        for p in projects:
            if p["full_name"].lower() == include_path.lower():
                selected.append(p)
                found = True
                break
        if not found:
            details = fetch_repo_details(include_path)
            if details:
                selected.append({
                    "full_name": include_path,
                    "name": include_path.split("/")[-1],
                    "owner": include_path.split("/")[0],
                    "description": details["description"],
                    "language": details["language"],
                    "stars": details["stars"],
                    "today_stars": 0,
                    "forks": details["forks"],
                    "topics": details.get("topics", []),
                    "from_api": True,
                })
    for p in projects:
        if len(selected) >= 6:
            break
        if p["full_name"] not in [s["full_name"] for s in selected]:
            selected.append(p)
    return selected[:6]


# ─── 绘图基础 ────────────────────────────────────────────────────────────────

def load_fonts():
    try:
        return {
            "title": ImageFont.truetype(FONT_BOLD, 42),
            "sub": ImageFont.truetype(FONT_REGULAR, 19),
            "hero": ImageFont.truetype(FONT_BOLD, 40),
            "date": ImageFont.truetype(FONT_REGULAR, 20),
            "proj_name": ImageFont.truetype(FONT_BOLD, 26),
            "meta": ImageFont.truetype(FONT_REGULAR, 18),
            "desc": ImageFont.truetype(FONT_REGULAR, 19),
            "tag": ImageFont.truetype(FONT_REGULAR, 16),
            "rank": ImageFont.truetype(FONT_BOLD, 26),
            "fire": ImageFont.truetype(FONT_BOLD, 26),
            "fire_sub": ImageFont.truetype(FONT_REGULAR, 15),
            "footer": ImageFont.truetype(FONT_BOLD, 26),
        }
    except Exception as e:
        print(f"[WARN] 字体加载失败: {e}")
        f = ImageFont.load_default()
        return {k: f for k in ["title", "sub", "hero", "date", "proj_name", "meta",
                               "desc", "tag", "rank", "fire", "fire_sub", "footer"]}


def rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = xy
    r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)
    if fill:
        draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
        draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
        draw.pieslice([x0, y0, x0 + 2*r, y0 + 2*r], 180, 270, fill=fill)
        draw.pieslice([x1 - 2*r, y0, x1, y0 + 2*r], 270, 360, fill=fill)
        draw.pieslice([x0, y1 - 2*r, x0 + 2*r, y1], 90, 180, fill=fill)
        draw.pieslice([x1 - 2*r, y1 - 2*r, x1, y1], 0, 90, fill=fill)
    if outline:
        draw.arc([x0, y0, x0 + 2*r, y0 + 2*r], 180, 270, fill=outline, width=width)
        draw.arc([x1 - 2*r, y0, x1, y0 + 2*r], 270, 360, fill=outline, width=width)
        draw.arc([x0, y1 - 2*r, x0 + 2*r, y1], 90, 180, fill=outline, width=width)
        draw.arc([x1 - 2*r, y1 - 2*r, x1, y1], 0, 90, fill=outline, width=width)
        draw.line([x0 + r, y0, x1 - r, y0], fill=outline, width=width)
        draw.line([x0 + r, y1, x1 - r, y1], fill=outline, width=width)
        draw.line([x0, y0 + r, x0, y1 - r], fill=outline, width=width)
        draw.line([x1, y0 + r, x1, y1 - r], fill=outline, width=width)


def rounded_mask(size, radius):
    w, h = size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, w, h], radius=radius, fill=255)
    return mask


def blend(color, ratio, base=(255, 255, 255)):
    return tuple(int(c * ratio + b * (1 - ratio)) for c, b in zip(color, base))


def darken(color, ratio, base=(0, 0, 0)):
    return tuple(int(c * ratio + b * (1 - ratio)) for c, b in zip(color, base))


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_text(draw, text, font, max_width):
    lines, cur = [], ""
    for ch in text:
        test = cur + ch
        if text_size(draw, test, font)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


# ─── 图标绘制 ────────────────────────────────────────────────────────────────

def draw_star_icon(draw, x, y, color=(180, 160, 120), r=8):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((x + rad * math.cos(ang), y + rad * math.sin(ang)))
    draw.polygon(pts, fill=color)


def draw_fork_icon(draw, x, y, color=(150, 146, 138), s=8):
    r = s * 0.32
    for cy in (y - s * 0.5, y + s * 0.5):
        draw.ellipse([x - r, cy - r, x + r, cy + r], outline=color, width=2)
    draw.ellipse([x - r, y - r, x + r, y + r], outline=color, width=2)
    draw.line([x, y - s * 0.5 + r, x, y - r], fill=color, width=2)
    draw.line([x, y + r, x, y + s * 0.5 - r], fill=color, width=2)


def draw_flame(draw, x, y, color, size=22):
    """简易火焰图标：橙色水滴状"""
    h = size
    w = size * 0.72
    # 外焰
    outer = blend(color, 0.15, (255, 120, 30))
    draw.ellipse([x - w/2, y - h*0.5, x + w/2, y + h*0.5], fill=(255, 130, 40))
    draw.polygon([(x, y - h*0.62), (x - w*0.42, y - h*0.05), (x + w*0.42, y - h*0.05)],
                 fill=(255, 130, 40))
    # 内焰
    draw.ellipse([x - w*0.28, y - h*0.18, x + w*0.28, y + h*0.42], fill=(255, 190, 70))


def draw_logo_glyph(draw, glyph, cx, cy, size, color=(255, 255, 255), name=""):
    """在 logo 方块中心绘制白色图标"""
    s = size * 0.5
    if glyph == "cloud":
        draw.ellipse([cx - s*0.9, cy - s*0.2, cx - s*0.1, cy + s*0.6], fill=color)
        draw.ellipse([cx - s*0.4, cy - s*0.7, cx + s*0.6, cy + s*0.4], fill=color)
        draw.ellipse([cx + s*0.1, cy - s*0.1, cx + s*0.95, cy + s*0.6], fill=color)
        draw.rectangle([cx - s*0.5, cy + s*0.1, cx + s*0.6, cy + s*0.6], fill=color)
    elif glyph == "code":
        f = ImageFont.truetype(FONT_BOLD, int(size*0.62))
        t = "</>"
        bbox = draw.textbbox((0, 0), t, font=f)
        draw.text((cx - (bbox[2]-bbox[0])/2, cy - (bbox[3]-bbox[1])/2 - bbox[1]),
                  t, fill=color, font=f)
    elif glyph == "person":
        draw.ellipse([cx - s*0.35, cy - s*0.8, cx + s*0.35, cy - s*0.1], fill=color)
        draw.pieslice([cx - s*0.75, cy + s*0.1, cx + s*0.75, cy + s*1.4],
                      180, 360, fill=color)
    elif glyph == "waves":
        for k in range(2):
            yy = cy - s*0.25 + k * s*0.55
            pts = []
            for i in range(24):
                px = cx - s + (2*s) * i / 23
                py = yy + math.sin(i / 23 * 2 * math.pi) * s*0.22
                pts.append((px, py))
            draw.line(pts, fill=color, width=4)
    else:  # letters
        t = (name[:2] if name else "?").upper()
        f = ImageFont.truetype(FONT_BOLD, int(size*0.5))
        bbox = draw.textbbox((0, 0), t, font=f)
        draw.text((cx - (bbox[2]-bbox[0])/2, cy - (bbox[3]-bbox[1])/2 - bbox[1]),
                  t, fill=color, font=f)


def draw_calendar(draw, x, y, color=(120, 116, 108), size=20):
    draw.rounded_rectangle([x, y, x + size, y + size], radius=3, outline=color, width=2)
    draw.line([x, y + size*0.32, x + size, y + size*0.32], fill=color, width=2)
    draw.line([x + size*0.28, y - size*0.12, x + size*0.28, y + size*0.12], fill=color, width=2)
    draw.line([x + size*0.72, y - size*0.12, x + size*0.72, y + size*0.12], fill=color, width=2)


# ─── 图片生成 ────────────────────────────────────────────────────────────────

def paste_asset(img, path, box, radius, mode="fill_h"):
    """将素材按指定方式贴入 box=(x,y,w,h)，圆角裁剪"""
    if not os.path.exists(path):
        return
    x, y, w, h = box
    src = Image.open(path).convert("RGB")
    sw, sh = src.size
    if mode == "fill_h":
        nw = int(w * sw / sh * 0.62)
        nh = h
        src = src.resize((nw, nh))
    elif mode == "fill_w":
        nw = w
        nh = int(h * sh / sw)
        src = src.resize((nw, nh))
    canvas = Image.new("RGB", (w, h), C["banner_bg1"])
    if mode == "fill_h":
        canvas.paste(src, (0, 0))
    else:  # fill_w: 底部对齐裁剪
        canvas.paste(src, (0, h - src.size[1]))
    mask = rounded_mask((w, h), radius)
    img.paste(canvas, (x, y), mask)


def draw_header(draw, fonts, img):
    # GitHub 圆形 logo
    logo_r = 34
    lx, ly = 56 + logo_r, 46 + logo_r
    mark_path = ASSET_DIR / "github_mark.png"
    if os.path.exists(mark_path):
        m = Image.open(mark_path).convert("RGB")
        m = m.resize((logo_r*2, logo_r*2))
        mask = Image.new("L", (logo_r*2, logo_r*2), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, logo_r*2, logo_r*2], fill=255)
        img.paste(m, (lx - logo_r, ly - logo_r), mask)
    else:
        draw.ellipse([lx - logo_r, ly - logo_r, lx + logo_r, ly + logo_r], fill=(30, 30, 30))

    # 标题
    draw.text((110, 40), "GitHub 热门项目", fill=C["text_dark"], font=fonts["title"])
    draw.text((112, 96), "发现优秀开源项目 · 和全球开发者一起成长", fill=C["text_mid"], font=fonts["sub"])

    # 右侧日期
    cal_x = IMG_W - 250
    draw_calendar(draw, cal_x, 52, size=22)
    draw.text((cal_x + 32, 48), TODAY, fill=C["text_dark"], font=fonts["date"])
    tw, _ = text_size(draw, TODAY, fonts["date"])
    right_txt = f"{WEEKDAY} · 每日更新"
    rtw, _ = text_size(draw, right_txt, fonts["sub"])
    draw.text((IMG_W - 48 - rtw, 96), right_txt, fill=C["text_mid"], font=fonts["sub"])


def draw_hero(draw, fonts, img):
    bx, by, bw, bh = 40, 150, 1000, 210
    # 背景渐变
    for i in range(bh):
        ratio = i / bh
        col = tuple(int(C["banner_bg1"][j] + (C["banner_bg2"][j] - C["banner_bg1"][j]) * ratio)
                    for j in range(3))
        draw.line([(bx, by + i), (bx + bw, by + i)], fill=col)
    # 贴插画
    paste_asset(img, ASSET_DIR / "hero_banner.png", (bx, by, bw, bh), 24, "fill_h")
    # 边框
    rounded_rect(draw, [bx, by, bx + bw, by + bh], 24, outline=C["banner_border"], width=2)
    # 手写风标语（右侧）
    draw.text((bx + bw - 360, by + 44), "好的项目", fill=C["hero_text"], font=fonts["hero"])
    draw.text((bx + bw - 300, by + 108), "让世界更好", fill=C["hero_text"], font=fonts["hero"])
    # 装饰小星
    for (sx, sy) in [(bx + bw - 120, by + 40), (bx + bw - 40, by + 120)]:
        draw.polygon([(sx, sy-8), (sx+3, sy-3), (sx+8, sy), (sx+3, sy+3),
                      (sx, sy+8), (sx-3, sy+3), (sx-8, sy), (sx-3, sy-3)],
                     fill=(240, 190, 90))


def draw_card(draw, fonts, img, project, rank, y):
    cx, cw = 40, 1000
    ch = 210
    radius = 20
    rank_color = RANK_COLORS[(rank - 1) % 6]

    # 阴影 + 卡片
    rounded_rect(draw, [cx + 3, y + 4, cx + cw + 3, y + ch + 4], radius, fill=C["shadow"])
    rounded_rect(draw, [cx, y, cx + cw, y + ch], radius, fill=C["card_bg"],
                 outline=C["card_border"], width=1)

    # 序号方块（左上角，略微外凸）
    badge = 44
    bx, by = cx - 8, y - 8
    rounded_rect(draw, [bx, by, bx + badge, by + badge], 12, fill=rank_color)
    num = str(rank)
    nw, nh = text_size(draw, num, fonts["rank"])
    draw.text((bx + (badge - nw) / 2, by + (badge - nh) / 2 - 2), num,
              fill=C["text_white"], font=fonts["rank"])

    # Logo 方块
    tile = 60
    tx, ty = cx + 24, y + 24
    tile_color = LOGO_TILES.get(project["full_name"], C["logo_tile"])
    rounded_rect(draw, [tx, ty, tx + tile, ty + tile], 15, fill=tile_color)
    glyph = LOGO_GLYPHS.get(project["full_name"], "letters")
    draw_logo_glyph(draw, glyph, tx + tile/2, ty + tile/2, tile, (255, 255, 255),
                    name=project["name"])

    # 内容起点
    content_x = tx + tile + 22
    # 项目名
    name_y = y + 22
    full_name = f"{project['owner']} / {project['name']}"
    draw.text((content_x, name_y), full_name, fill=C["text_dark"], font=fonts["proj_name"])

    # 元信息行
    meta_y = name_y + 38
    lang = project.get("language", "未知")
    lc = LANG_COLORS.get(lang, (150, 150, 150))
    draw.ellipse([content_x, meta_y + 5, content_x + 10, meta_y + 15], fill=lc)
    draw.text((content_x + 16, meta_y), lang, fill=C["text_mid"], font=fonts["meta"])
    lx = content_x + 16 + text_size(draw, lang, fonts["meta"])[0] + 24
    draw_star_icon(draw, lx + 6, meta_y + 9, (190, 170, 120))
    draw.text((lx + 18, meta_y), f"{project['stars']:,}", fill=C["text_mid"], font=fonts["meta"])
    fx = lx + 18 + text_size(draw, f"{project['stars']:,}", fonts["meta"])[0] + 24
    draw_fork_icon(draw, fx + 6, meta_y + 9, (150, 146, 138))
    draw.text((fx + 18, meta_y), f"{project['forks']:,}", fill=C["text_mid"], font=fonts["meta"])

    # 描述（全宽，位于 logo 下方）
    desc = translate_description(project["full_name"], project.get("description", "暂无描述")).strip()
    desc = desc or "暂无描述"
    desc_y = y + 98
    desc_lines = wrap_text(draw, desc, fonts["desc"], cw - 52)
    for i, line in enumerate(desc_lines[:2]):
        draw.text((cx + 24, desc_y + i * 26), line, fill=C["text_mid"], font=fonts["desc"])

    # 标签行
    tag_y = y + 158
    tags = get_tags(project["full_name"])
    tag_x = cx + 24
    for t in tags:
        tw, th = text_size(draw, t, fonts["tag"])
        pw = tw + 24
        rounded_rect(draw, [tag_x, tag_y, tag_x + pw, tag_y + 28], 14, fill=C["tag_bg"])
        draw.text((tag_x + 12, tag_y + 5), t, fill=C["tag_text"], font=fonts["tag"])
        tag_x += pw + 10

    # 火焰徽章（右上）
    today = project.get("today_stars", 0)
    if today > 0:
        bw_, bh_ = 138, 58
        bxx = cx + cw - bw_ - 20
        byy = y + 18
        rounded_rect(draw, [bxx, byy, bxx + bw_, byy + bh_], 16, fill=rank_color)
        draw_flame(draw, bxx + 26, byy + 24, rank_color, size=24)
        ftxt = f"+{today:,}"
        fw, fh = text_size(draw, ftxt, fonts["fire"])
        draw.text((bxx + 46, byy + 8), ftxt, fill=C["text_white"], font=fonts["fire"])
        sub = "今日"
        sw, sh = text_size(draw, sub, fonts["fire_sub"])
        draw.text((bxx + 46 + (fw - sw) / 2, byy + 38), sub,
                  fill=blend(rank_color, 0.55), font=fonts["fire_sub"])

    return ch + 16


def draw_footer(draw, fonts, img):
    fh = 150
    fy = IMG_H - fh
    paste_asset(img, ASSET_DIR / "footer_hills.png", (0, fy, IMG_W, fh), 0, "fill_w")
    txt = "Open Source"
    tw, _ = text_size(draw, txt, fonts["footer"])
    draw.text((IMG_W - tw - 70, fy + 44), txt, fill=C["hero_text"], font=fonts["footer"])
    txt2 = "Better Future"
    tw2, _ = text_size(draw, txt2, fonts["footer"])
    draw.text((IMG_W - tw2 - 70, fy + 82), txt2, fill=C["hero_text"], font=fonts["footer"])


def generate_image(projects, output_path):
    fonts = load_fonts()
    img = Image.new("RGB", (IMG_W, IMG_H), C["bg"])
    draw = ImageDraw.Draw(img)

    draw_header(draw, fonts, img)
    draw_hero(draw, fonts, img)

    y = 150 + 210 + 34
    for i, project in enumerate(projects):
        y += draw_card(draw, fonts, img, project, i + 1, y)

    draw = ImageDraw.Draw(img)
    draw_footer(draw, fonts, img)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG", quality=95)
    print(f"[OK] 图片已生成: {output_path}")
    return str(output_path)


# ─── 主流程 ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="DailyGithub - 生成每日 GitHub 热门项目贴图")
    parser.add_argument("--output", type=str, default=None, help="输出路径")
    parser.add_argument("--include", type=str, default=None, help="额外包含的项目 URL")
    parser.add_argument("--date", type=str, default=None, help="指定日期")
    args = parser.parse_args()

    print("=" * 50)
    print("DailyGithub - 每日 GitHub 热门项目贴图生成器")
    print("=" * 50)

    print("\n[1/3] 正在获取 GitHub Trending 数据...")
    projects = fetch_github_trending()
    print(f"  获取到 {len(projects)} 个 trending 项目")
    if not projects:
        print("[ERROR] 无法获取 GitHub Trending 数据，请检查网络连接")
        sys.exit(1)

    print("\n[2/3] 正在选择上升最快的 6 个项目...")
    selected = select_top_projects(projects, include_url=args.include)
    for i, p in enumerate(selected):
        today = p.get("today_stars", 0)
        marker = " (指定)" if p.get("from_api") else ""
        print(f"  #{i+1} {p['full_name']} (+{today:,} today){marker}")

    print("\n[3/3] 正在生成贴图...")
    output_path = Path(args.output) if args.output else OUTPUT_DIR / f"daily_github_{TODAY_SHORT}.png"
    result = generate_image(selected, output_path)
    print(f"\n完成! 输出文件: {result}")
    return result


if __name__ == "__main__":
    main()
