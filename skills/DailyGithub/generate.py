#!/usr/bin/env python3
"""DailyGithub：实时 Trending 数据与 1024×1536 模板排版。"""
import argparse
import html
import math
import re
from datetime import datetime
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

BASE_DIR = Path(__file__).parent
ASSET_DIR = BASE_DIR / 'assets'
OUTPUT_DIR = BASE_DIR / 'output'
IMG_W, IMG_H = 1024, 1536
FONT_DIR = Path('/usr/share/fonts/opentype/noto')
BG = '#fcf9ef'
INK = '#20252d'
GRAY = '#68717c'
COLORS = ['#efa923', '#329bea', '#fb883b', '#329bea', '#49b58c', '#8a69df']
CURATED_DESCRIPTIONS = {
    'TencentCloud/Octop': '腾讯云推出的智能 AI 助手平台，支持多用户、多 Agent 协作，可私有化部署，适合企业级智能对话场景。',
    'cloudflare/security-audit-skill': 'Cloudflare 推出的安全审计 Agent 技能，支持多阶段安全审计，可独立验证并生成机器可读的安全发现报告。',
    'alibaba/open-code-review': '阿里巴巴开源的代码审查工具，采用混合架构（确定性流水线 + LLM Agent），支持多语言规则集，涵盖 NPE、线程安全、XSS、SQL 注入等检测，兼容 OpenAI 和 Anthropic 模型。',
    'Tencent/BrowserSkill': '腾讯推出的浏览器自动化技能，让 AI Agent 使用真实登录态浏览器执行操作，不干扰用户工作，支持 CLI 和扩展两种模式。',
    'affaan-m/ECC': 'Agent 性能优化系统，提供技能、直觉、记忆、安全等模块，支持 Claude Code、Codex、Opencode、Cursor 等主流 AI 编程工具。',
    'Tencent/WeKnora': '腾讯开源的 LLM 知识平台，可将原始文档转化为可查询的 RAG 系统，具备自主推理 Agent 和自我维护 Wiki 能力。',
}
CURATED_TAGS = {
    'TencentCloud/Octop': ['AI', '大模型', '企业级', 'Agent'],
    'cloudflare/security-audit-skill': ['Security', 'Audit', 'Cloudflare', 'Agent'],
    'alibaba/open-code-review': ['Code Review', 'AI', 'Security', 'Alibaba'],
    'Tencent/BrowserSkill': ['Browser', 'Automation', 'AI', 'TypeScript'],
    'affaan-m/ECC': ['Performance', 'Agent', 'LLM', 'Developer Tools'],
    'Tencent/WeKnora': ['RAG', 'LLM', 'Knowledge', 'Tencent'],
}
# 以视觉稿为坐标基准；第六张较短，给底部插画留白。
CARD_BOXES = [(38, 276, 990, 456), (38, 475, 990, 656),
              (38, 675, 990, 865), (38, 884, 990, 1074),
              (38, 1093, 990, 1274), (38, 1293, 990, 1455)]


def parse_article(article):
    match = re.search(r'<h2[^>]*>.*?<a[^>]*href="/([^"?]+/[^"?]+)"', article, re.S)
    if not match:
        return None
    full_name = html.unescape(match[1]).strip('/')
    owner, name = full_name.split('/', 1)
    desc = re.search(r'<p[^>]*>(.*?)</p>', article, re.S)
    description = html.unescape(re.sub('<[^>]+>', ' ', desc[1])) if desc else ''
    language = re.search(r'itemprop="programmingLanguage"[^>]*>(.*?)</span>', article)
    today = re.search(r'([\d,]+)\s+stars\s+today', article)
    project = dict(full_name=full_name, owner=owner, name=name,
                   description=' '.join(description.split()),
                   language=language[1].strip() if language else 'Unknown',
                   today_stars=int(today[1].replace(',', '')) if today else None)
    for key, suffix in [('stars', 'stargazers'), ('forks', 'forks')]:
        section = re.search(r'href="[^"]*/' + suffix + r'".*?</a>', article, re.S)
        count = re.search(r'<svg.*?</svg>\s*([\d,]+)', section[0], re.S) if section else None
        project[key] = int(count[1].replace(',', '')) if count else 0
    return project


def fetch_github_trending():
    response = requests.get('https://github.com/trending?since=daily',
                            headers={'User-Agent': 'DailyGithub/2.0'}, timeout=30)
    response.raise_for_status()
    articles = re.findall(r'<article class="Box-row".*?</article>', response.text, re.S)
    return [p for a in articles if (p := parse_article(a))]


def select_top_projects(projects, include_url=None):
    ordered = sorted(projects, key=lambda p: p['today_stars'] or 0, reverse=True)
    selected = []
    if include_url:
        match = re.fullmatch(r'https://github.com/([\w.-]+/[\w.-]+)/?', include_url)
        if not match:
            raise ValueError('--include 必须是 GitHub 仓库 URL')
        path = match[1]
        project = next((p for p in ordered if p['full_name'].lower() == path.lower()), None)
        if project is None:
            response = requests.get(f'https://api.github.com/repos/{path}', timeout=20)
            response.raise_for_status()
            data = response.json()
            project = dict(full_name=data['full_name'], name=data['name'],
                           owner=data['owner']['login'], description=data.get('description') or '',
                           language=data.get('language') or 'Unknown', stars=data['stargazers_count'],
                           forks=data['forks_count'], today_stars=None)
        selected.append(project)
    selected.extend(p for p in ordered if p['full_name'] not in {s['full_name'] for s in selected})
    if len(selected) < 6:
        raise ValueError('数据不足六个项目，未生成不完整图片')
    return selected[:6]


def font(size, bold=False):
    return ImageFont.truetype(str(FONT_DIR / ('NotoSansCJK-Bold.ttc' if bold else 'NotoSansCJK-Regular.ttc')), size)


def tint(color, amount=.1):
    rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    return tuple(round(255 + (c - 255) * amount) for c in rgb)


def text(draw, xy, value, f, fill=INK):
    # 使用可见字形的顶边，消除字体 ascender 带来的伪边距。
    draw.text(xy, value, font=f, fill=fill, anchor='lt')


def centered(draw, box, value, f, fill):
    x0, y0, x1, y1 = box
    b = draw.textbbox((0, 0), value, font=f)
    draw.text(((x0+x1-b[2]-b[0])/2, (y0+y1-b[3]-b[1])/2), value, font=f, fill=fill)


def wrap_text(draw, value, f, width):
    # 英文单词保持完整；中文标点不得出现在行首。
    tokens = re.findall(r'[A-Za-z0-9]+(?:[·./+-][A-Za-z0-9]+)*|\s+|.', value)
    lines, current = [], ''
    for token in tokens:
        candidate = current + token
        if draw.textlength(candidate, font=f) <= width:
            current = candidate
            continue
        if token in '，。；：！？、）》】”’' and current:
            moved = current[-1]
            current = current[:-1]
            lines.append(current.rstrip())
            current = moved + token
        else:
            if current.strip():
                lines.append(current.rstrip())
            current = token.lstrip()
    if current.strip():
        lines.append(current.rstrip())
    if any(draw.textlength(line, font=f) > width for line in lines):
        raise ValueError('存在无法容纳的超长词，请调整介绍内容')
    return lines


def paste_asset(img, path, box, crop=None):
    x, y, w, h = box
    with Image.open(path) as source:
        source = source.convert('RGB')
        if crop:
            source = source.crop(crop)
        # 单一缩放倍率，不独立缩放宽高；裁切而非拉伸。
        fitted = ImageOps.fit(source, (w, h), method=Image.Resampling.LANCZOS)
    mask = Image.new('L', (w, h))
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w-1, h-1), radius=12, fill=255)
    img.paste(fitted, (x, y), mask)


def star(draw, x, y, color, r=7):
    points = [(x + math.cos(-math.pi/2+i*math.pi/5)*(r if i%2==0 else r*.45),
               y + math.sin(-math.pi/2+i*math.pi/5)*(r if i%2==0 else r*.45)) for i in range(10)]
    draw.polygon(points, fill=color)


def fork(draw, x, y):
    draw.line([(x-4,y-4),(x-4,y),(x,y+3),(x+4,y),(x+4,y-4)], fill=GRAY, width=2)
    draw.line([(x,y+3),(x,y+8)], fill=GRAY, width=2)
    for px, py in [(x-4,y-6),(x+4,y-6),(x,y+8)]:
        draw.ellipse((px-2,py-2,px+2,py+2), outline=GRAY, width=1)


def flame(draw, x, y, color):
    draw.polygon([(x,y-12),(x+2,y-3),(x+5,y-6),(x+8,y+4),(x+5,y+10),
                  (x-4,y+11),(x-8,y+5),(x-5,y-4),(x-3,y)], fill=color)
    draw.polygon([(x+1,y),(x+3,y+8),(x,y+11),(x-3,y+7)], fill=tint(color,.3))


def project_icon(draw, name, x, y):
    tile_colors = {'TencentCloud/Octop':'#080b0e', 'cloudflare/security-audit-skill':'#ff803e',
                   'alibaba/open-code-review':'#ff8134', 'Tencent/BrowserSkill':'#078efa',
                   'affaan-m/ECC':'#193c97', 'Tencent/WeKnora':'#329af3'}
    draw.rounded_rectangle((x,y,x+70,y+70), radius=15, fill=tile_colors.get(name, '#27354c'))
    if name.endswith('Octop') or name.startswith('cloudflare/'):
        points = [(x+18,y+45),(x+15,y+41),(x+15,y+35),(x+20,y+30),(x+26,y+30),
                  (x+27,y+23),(x+33,y+19),(x+40,y+20),(x+46,y+27),(x+46,y+31),
                  (x+53,y+32),(x+57,y+37),(x+56,y+43),(x+52,y+47),(x+18,y+47)]
        if name.endswith('Octop'):
            draw.line(points+[points[0]], fill='white', width=4, joint='curve')
        else:
            draw.polygon(points, fill='white')
    elif name.endswith('WeKnora'):
        for offset in (-6, 8):
            pts = [(x+17+i,y+35+offset+5*math.sin(i/36*2*math.pi)) for i in range(37)]
            draw.line(pts, fill='white', width=5, joint='curve')
    elif name.endswith('BrowserSkill'):
        draw.line([(x+22,y+46),(x+35,y+20),(x+45,y+39)], fill='white', width=6, joint='curve')
        draw.arc((x+23,y+34,x+49,y+54), 0, 165, fill='white', width=5)
    else:
        centered(draw,(x,y,x+70,y+70), '</>' if name.endswith('ECC') else 'eℓ', font(27,True),'white')


def draw_header(img, draw, day):
    paste_asset(img, ASSET_DIR/'github_mark.png', (44,22,66,66))
    text(draw,(130,25),'GitHub 热门项目',font(36,True))
    text(draw,(131,70),'发现优秀开源项目 · 和全球开发者一起成长',font(18),GRAY)
    draw.rounded_rectangle((873,37,888,52),radius=2,outline=GRAY,width=1)
    draw.line((873,42,888,42),fill=GRAY)
    for x in (877,884):
        draw.line((x,34,x,39),fill=GRAY,width=2)
    text(draw,(899,36),day.strftime('%Y-%m-%d'),font(14),GRAY)
    weekday = '一二三四五六日'[day.weekday()]
    text(draw,(879,62),f'星期{weekday} · 每日更新',font(11),GRAY)
    paste_asset(img, ASSET_DIR/'hero_wide.png', (38,107,952,151))
    lettering = Image.new('RGBA',(310,110))
    ld = ImageDraw.Draw(lettering)
    text(ld,(14,5),'好的项目',font(30),'#302b20')
    text(ld,(65,45),'让世界更好',font(30),'#302b20')
    ld.arc((80,86,285,114),185,350,fill='#51412a',width=2)
    lettering = lettering.rotate(10, resample=Image.Resampling.BICUBIC, expand=True)
    img.paste(lettering,(376,117),lettering)


def draw_card(draw, project, rank):
    x0,y,x1,bottom = CARD_BOXES[rank-1]
    color = COLORS[rank-1]
    draw.rounded_rectangle((x0,y+3,x1,bottom+3),radius=14,fill=tint(color,.08))
    draw.rounded_rectangle((x0,y,x1,bottom),radius=14,fill='#fffefa',outline=tint(color,.24),width=2)
    badge = (44,y+3,92,y+53)
    draw.rounded_rectangle(badge,radius=15,fill=color)
    centered(draw,badge,str(rank),font(28,True),'white')
    project_icon(draw,project['full_name'],106,y+25)
    content_x = 201
    title = f"{project['owner']} / {project['name']}"
    title_font = font(20,True)
    if draw.textlength(title,font=title_font) > 625:
        raise ValueError(f'项目名超出标题区域：{title}')
    text(draw,(content_x,y+(21 if rank == 6 else 25)),title,title_font)
    meta_y = y+(51 if rank == 6 else 59)
    draw.ellipse((201,meta_y,211,meta_y+10),fill='#329bea')
    lang = project.get('language','Unknown')
    text(draw,(218,meta_y-1),lang,font(15),GRAY)
    sx = 218+draw.textlength(lang,font=font(15))+28
    star(draw,sx,meta_y+5,GRAY)
    stars = f"{project['stars']:,}"
    text(draw,(sx+16,meta_y-1),stars,font(15),GRAY)
    fx = sx+16+draw.textlength(stars,font=font(15))+28
    fork(draw,fx,meta_y+5)
    text(draw,(fx+15,meta_y-1),f"{project['forks']:,}",font(15),GRAY)
    desc = CURATED_DESCRIPTIONS.get(project['full_name'],project.get('description',''))
    desc_font = font(16)
    desc_width = [570, 560, 750, 750, 750, 690][rank-1]
    lines = wrap_text(draw,desc,desc_font,desc_width)
    if len(lines)>3:
        raise ValueError(f"介绍超过三行，请精简内容：{project['full_name']}")
    desc_y = y+(73 if rank == 6 else 83)
    tag_y = max(y+(122 if rank == 6 else 132),desc_y+len(lines)*23+5)
    if tag_y+29 > bottom-9:
        raise ValueError(f"正文与标签超出卡片：{project['full_name']}")
    for i,line in enumerate(lines):
        text(draw,(content_x,desc_y+23*i),line,desc_font,GRAY)
    tx = content_x
    for tag in CURATED_TAGS.get(project['full_name'],[]):
        width = math.ceil(draw.textlength(tag,font=font(13)))+30
        if tx+width > 960:
            raise ValueError('标签超过卡片右边界')
        box = (tx,tag_y,tx+width,tag_y+29)
        draw.rounded_rectangle(box,radius=14,fill=tint(color,.11))
        centered(draw,box,tag,font(13),'#82652d' if rank==1 else color)
        tx += width+12
    today = project.get('today_stars')
    value = f'+{today:,}' if today is not None else '暂无'
    number_font = font(22)
    width = max(112,math.ceil(draw.textlength(value,font=number_font))+45)
    bx = 972-width
    draw.rounded_rectangle((bx,y+19,972,y+64),radius=22,fill=tint(color,.07))
    flame(draw,bx+21,y+41,color if rank!=1 else '#fb923c')
    text(draw,(bx+37,y+31),value,number_font,color if rank!=1 else '#ec9250')
    text(draw,(924,y+66),'今日' if today is not None else '未收录',font(13),'#9399a1')


def draw_footer(img, draw):
    draw.polygon([(0,1454),(90,1476),(200,1510),(310,1496),(430,1520),
                  (550,1500),(720,1525),(920,1503),(1024,1480),(1024,1536),(0,1536)],fill='#f9e7a0')
    draw.polygon([(0,1518),(74,1500),(188,1536),(1024,1536),(1024,1485),
                  (992,1508),(940,1530),(420,1536),(0,1536)],fill='#d1d89a')
    for x,y,rx,ry in [(49,1471,12,35),(65,1491,14,31),(30,1501,12,20),
                       (99,1479,10,24),(116,1490,10,14)]:
        draw.ellipse((x-rx,y-ry,x+rx,y+ry),fill='#c4cf77')
        draw.line((x,y-15,x+5,1525),fill='#a4b16b',width=2)
    draw.ellipse((919,1464,940,1485),fill='#f8d75e')
    for i in range(10):
        angle=i*math.pi/5
        draw.line((930+16*math.cos(angle),1475+16*math.sin(angle),
                   930+23*math.cos(angle),1475+23*math.sin(angle)),fill='#f4cd52',width=2)
    layer = Image.new('RGBA',(190,65))
    ld = ImageDraw.Draw(layer)
    text(ld,(0,0),'Open Source',font(16),'#795431')
    text(ld,(14,26),'Better Future',font(16),'#795431')
    layer = layer.rotate(10,resample=Image.Resampling.BICUBIC,expand=True)
    img.paste(layer,(769,1458),layer)


def generate_image(projects, output_path, day=None):
    if len(projects)!=6:
        raise ValueError('必须恰好包含六个项目')
    img = Image.new('RGB',(IMG_W,IMG_H),BG)
    draw = ImageDraw.Draw(img)
    draw_header(img,draw,day or datetime.now())
    for rank,project in enumerate(projects,1):
        draw_card(draw,project,rank)
    draw_footer(img,draw)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True,exist_ok=True)
    img.save(output_path,'PNG')
    print(f'[OK] {output_path} ({IMG_W}×{IMG_H})；六卡片边界检查通过')
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--include')
    parser.add_argument('--output')
    parser.add_argument('--date',type=lambda s: datetime.strptime(s,'%Y-%m-%d'))
    args = parser.parse_args()
    day = args.date or datetime.now()
    projects = select_top_projects(fetch_github_trending(),args.include)
    for p in projects:
        print(p['full_name'],p['today_stars'])
    generate_image(projects,args.output or OUTPUT_DIR/f'daily_github_{day:%Y%m%d}.png',day)


if __name__=='__main__':
    main()
