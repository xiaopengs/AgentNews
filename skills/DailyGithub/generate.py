#!/usr/bin/env python3
"""DailyGithub - 每日 GitHub 热门项目贴图生成器

从 GitHub Trending 获取当日上升最快的 6 个开源项目，
生成一张精美的信息图（1080x1920），适合分享到社交媒体。
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

# ── 配置 ───────────────────────────────────────────────────────────────────

OUTPUT_DIR = Path(__file__).parent / "output"
TODAY = datetime.now().strftime("%Y-%m-%d")
TODAY_SHORT = datetime.now().strftime("%Y%m%d")
WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
WEEKDAY = WEEKDAYS[datetime.now().weekday()]

# 颜色方案 - 参考模板的清新蓝白风格
C = {
    "bg": (235, 240, 252),
    "header_bg": (28, 55, 110),
    "header_accent": (55, 110, 210),
    "card_bg": (255, 255, 255),
    "card_border": (200, 210, 235),
    "rank_1": (245, 160, 30),
    "rank_2": (160, 170, 190),
    "rank_3": (195, 140, 90),
    "rank_default": (70, 120, 200),
    "text_dark": (25, 30, 50),
    "text_mid": (80, 90, 115),
    "text_light": (140, 150, 170),
    "text_white": (255, 255, 255),
    "star": (240, 175, 40),
    "up": (210, 60, 50),
    "lang_dot": (70, 155, 215),
    "tag_bg": (230, 238, 252),
    "tag_text": (50, 100, 180),
    "footer_bg": (28, 55, 110),
    "section_bg": (245, 248, 255),
    "divider": (200, 210, 230),
}

IMG_W = 1080
IMG_H = 1920

FONT_DIR = "/usr/share/fonts/opentype/noto"
FONT_BOLD = os.path.join(FONT_DIR, "NotoSerifCJK-Bold.ttc")
FONT_REGULAR = os.path.join(FONT_DIR, "NotoSansCJK-Regular.ttc")


# ─── 数据获取 ─────────────────────────────────────────────────────────────────

def fetch_github_trending():
    """从 GitHub Trending 页面获取热门项目"""
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
    """解析单个 article 块 - 适配 GitHub 当前 HTML 结构"""
    project = {}

    # 获取 repo 名称 - 从 h2 中的链接
    # Pattern: href="/owner/repo" in h2 block (not login redirect)
    h2_match = re.search(r'<h2[^>]*>.*?<a[^>]*href="(/[^/"]+/[^"]+)"', article_html, re.DOTALL)
    if not h2_match:
        return None
    repo_path = h2_match.group(1).strip()
    # 排除 login 跳转
    if "login" in repo_path:
        return None

    project["full_name"] = repo_path.lstrip("/")
    project["name"] = repo_path.split("/")[-1]
    project["owner"] = repo_path.split("/")[1] if "/" in repo_path else ""

    # 获取描述 - <p> 标签，排除按钮内容
    desc_match = re.search(r'<p[^>]*>(.*?)</p>', article_html, re.DOTALL)
    if desc_match:
        desc = desc_match.group(1).strip()
        # 移除 SVG 图标和按钮
        desc = re.sub(r'<svg[^>]*>.*?</svg>', '', desc, flags=re.DOTALL)
        desc = re.sub(r'<button[^>]*>.*?</button>', '', desc, flags=re.DOTALL)
        desc = re.sub(r'<details[^>]*>.*?</details>', '', desc, flags=re.DOTALL)
        desc = re.sub(r'<a[^>]*>.*?</a>', '', desc, flags=re.DOTALL)  # 移除链接
        desc = re.sub(r'<[^>]+>', ' ', desc)
        desc = re.sub(r'\s+', ' ', desc).strip()
        # 移除开头的 "Star" 文字（来自 star 按钮）
        if desc.startswith("Star "):
            desc = desc[5:]
        # 移除 "Sponsor" 文字
        if desc.startswith("Sponsor "):
            desc = desc[8:]
        # 移除重复的仓库名称前缀
        repo_prefix = f"{project['owner']} / {project['name']} "
        if desc.startswith(repo_prefix):
            desc = desc[len(repo_prefix):]
        project["description"] = desc
    else:
        project["description"] = "暂无描述"

    # 获取语言
    lang_match = re.search(r'<span itemprop="programmingLanguage">(.*?)</span>', article_html)
    project["language"] = lang_match.group(1).strip() if lang_match else "Unknown"

    # 获取总星标数 - 找到 stargazers 链接后的 SVG+数字
    stars_section = re.search(r'href="[^"]*/stargazers".*?</a>', article_html, re.DOTALL)
    if stars_section:
        num_match = re.search(r'<svg.*?</svg>\s*([\d,]+)', stars_section.group(), re.DOTALL)
        if num_match:
            project["stars"] = int(num_match.group(1).replace(",", ""))
        else:
            project["stars"] = 0
    else:
        project["stars"] = 0

    # 获取今日新增星标
    today_match = re.search(r'([\d,]+)\s+stars\s+today', article_html)
    if today_match:
        project["today_stars"] = int(today_match.group(1).replace(",", ""))
    else:
        project["today_stars"] = 0

    # 获取 fork 数
    fork_section = re.search(r'href="[^"]*/forks".*?</a>', article_html, re.DOTALL)
    if fork_section:
        num_match = re.search(r'<svg.*?</svg>\s*([\d,]+)', fork_section.group(), re.DOTALL)
        if num_match:
            project["forks"] = int(num_match.group(1).replace(",", ""))
        else:
            project["forks"] = 0
    else:
        project["forks"] = 0

    return project


def fetch_repo_details(repo_path):
    """通过 GitHub API 获取仓库详细信息"""
    url = f"https://api.github.com/repos/{repo_path}"
    headers = {
        "User-Agent": "DailyGithub-Bot/1.0",
        "Accept": "application/vnd.github.v3+json",
    }
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
    """选择上升最快的 6 个项目"""
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


# ─── 图片生成 ────────────────────────────────────────────────────────────────

def load_fonts():
    """加载中文字体"""
    try:
        return {
            "title": ImageFont.truetype(FONT_BOLD, 46),
            "subtitle": ImageFont.truetype(FONT_REGULAR, 22),
            "project_name": ImageFont.truetype(FONT_BOLD, 28),
            "project_desc": ImageFont.truetype(FONT_REGULAR, 20),
            "small": ImageFont.truetype(FONT_REGULAR, 18),
            "rank": ImageFont.truetype(FONT_BOLD, 32),
            "footer": ImageFont.truetype(FONT_REGULAR, 16),
            "tag": ImageFont.truetype(FONT_REGULAR, 15),
            "big_num": ImageFont.truetype(FONT_BOLD, 40),
        }
    except Exception as e:
        print(f"[WARN] 字体加载失败: {e}")
        f = ImageFont.load_default()
        return {k: f for k in ["title", "subtitle", "project_name", "project_desc",
                                "small", "rank", "footer", "tag", "big_num"]}


def rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    """绘制圆角矩形"""
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


def draw_text_center(draw, text, y, font, fill, width=IMG_W):
    """居中绘制文字"""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, y), text, fill=fill, font=font)


def wrap_text(text, font, max_width, draw):
    """智能换行 - 支持中英文混合"""
    lines = []
    current = ""

    for char in text:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = char

    if current:
        lines.append(current)
    return lines


def draw_project_card(draw, fonts, project, rank, y):
    """绘制单个项目卡片 - 参考模板的分区布局风格"""
    margin = 36
    card_x = margin
    card_w = IMG_W - 2 * margin
    card_h = 250
    radius = 14

    # 卡片阴影
    rounded_rect(draw, [card_x + 3, y + 3, card_x + card_w + 3, y + card_h + 3],
                 radius, fill=(210, 218, 235))

    # 卡片主体
    rounded_rect(draw, [card_x, y, card_x + card_w, y + card_h],
                 radius, fill=C["card_bg"], outline=C["card_border"], width=1)

    # 左侧排名色条
    rank_colors = [C["rank_1"], C["rank_2"], C["rank_3"],
                   C["rank_default"], C["rank_default"], C["rank_default"]]
    rank_color = rank_colors[rank - 1] if rank <= 6 else C["rank_default"]

    # 排名圆形
    cx, cy, cr = card_x + 42, y + 52, 26
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=rank_color)
    rank_text = str(rank)
    bbox = draw.textbbox((0, 0), rank_text, font=fonts["rank"])
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2 - 1), rank_text, fill=C["text_white"], font=fonts["rank"])

    # 项目名称
    nx = card_x + 82
    ny = y + 16
    full_name = f"{project['owner']} / {project['name']}"
    draw.text((nx, ny), full_name, fill=C["text_dark"], font=fonts["project_name"])

    # 语言 + 星标 + 今日增长 信息行
    info_y = ny + 38
    lang = project.get("language", "Unknown")

    # 语言圆点
    draw.ellipse([nx, info_y + 3, nx + 10, info_y + 13], fill=C["lang_dot"])
    draw.text((nx + 16, info_y), lang, fill=C["text_mid"], font=fonts["small"])

    # 总星标
    stars = project.get("stars", 0)
    sx = nx + 110
    draw.text((sx, info_y), f"★ {stars:,}", fill=C["text_mid"], font=fonts["small"])

    # Fork 数
    forks = project.get("forks", 0)
    fx = sx + 110
    draw.text((fx, info_y), f" {forks:,}", fill=C["text_mid"], font=fonts["small"])

    # 今日增长
    today_stars = project.get("today_stars", 0)
    if today_stars > 0:
        tx = fx + 110
        draw.text((tx, info_y), f"▲ +{today_stars:,} today", fill=C["up"], font=fonts["small"])

    # 描述区域
    desc = project.get("description", "暂无描述").strip()
    if not desc:
        desc = "暂无描述"

    desc_x = nx
    desc_y = info_y + 28
    max_dw = card_w - 100
    desc_lines = wrap_text(desc, fonts["project_desc"], max_dw, draw)

    for i, line in enumerate(desc_lines[:3]):
        draw.text((desc_x, desc_y + i * 26), line, fill=C["text_mid"], font=fonts["project_desc"])

    # 右侧今日星标大数字（仅对有增长的项目）
    if today_stars > 0:
        big_x = card_x + card_w - 130
        big_y = y + 22
        big_text = f"+{today_stars:,}"
        bbox = draw.textbbox((0, 0), big_text, font=fonts["big_num"])
        bw = bbox[2] - bbox[0]
        draw.text((big_x + (130 - bw) // 2, big_y), big_text, fill=rank_color, font=fonts["big_num"])
        draw.text((big_x + 35, big_y + 46), "today", fill=C["text_light"], font=fonts["tag"])

    return card_h + 14


def generate_image(projects, output_path):
    """生成最终图片 - 参考模板的分段布局"""
    fonts = load_fonts()

    img = Image.new("RGB", (IMG_W, IMG_H), C["bg"])
    draw = ImageDraw.Draw(img)

    # 背景微渐变
    for y in range(IMG_H):
        ratio = y / IMG_H
        r = int(C["bg"][0] + (220 - C["bg"][0]) * ratio * 0.3)
        g = int(C["bg"][1] + (228 - C["bg"][1]) * ratio * 0.3)
        b = int(C["bg"][2] + (248 - C["bg"][2]) * ratio * 0.3)
        draw.line([(0, y), (IMG_W, y)], fill=(r, g, b))

    # ── 顶部标题区 ───
    header_h = 170
    draw.rectangle([0, 0, IMG_W, header_h], fill=C["header_bg"])

    # 底部装饰线
    draw.rectangle([0, header_h - 5, IMG_W, header_h], fill=C["header_accent"])
    draw.rectangle([0, header_h - 2, IMG_W, header_h], fill=(80, 140, 230))

    # 主标题
    draw_text_center(draw, "Daily GitHub Trending", 32, fonts["title"], C["text_white"])

    # 副标题
    subtitle = f"{TODAY} {WEEKDAY}  ·  每日上升最快的 6 个开源项目"
    draw_text_center(draw, subtitle, 95, fonts["subtitle"], (170, 195, 240))

    # 装饰小图标区域 - 三个小圆点
    for i, color in enumerate([(245, 160, 30), (70, 155, 215), (80, 200, 120)]):
        cx = IMG_W // 2 - 40 + i * 40
        draw.ellipse([cx - 4, 135, cx + 4, 143], fill=color)

    # ─── 项目卡片 ───
    card_start = header_h + 20
    current_y = card_start

    for i, project in enumerate(projects):
        card_h = draw_project_card(draw, fonts, project, i + 1, current_y)
        current_y += card_h

    # ─── 底部信息区 ───
    footer_h = 90
    footer_y = IMG_H - footer_h
    draw.rectangle([0, footer_y, IMG_W, IMG_H], fill=C["footer_bg"])

    # 顶部装饰线
    draw.rectangle([0, footer_y, IMG_W, footer_y + 3], fill=C["header_accent"])

    # 底部文字
    draw_text_center(draw, "数据来源: GitHub Trending  ·  由 DailyGithub Skill 自动生成",
                     footer_y + 28, fonts["footer"], (160, 185, 230))

    # 保存
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
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = OUTPUT_DIR / f"daily_github_{TODAY_SHORT}.png"

    result = generate_image(selected, output_path)
    print(f"\n完成! 输出文件: {result}")
    return result


if __name__ == "__main__":
    main()
