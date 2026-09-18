# AgentNews Skills 索引

> 本目录包含 AgentNews 项目的所有 Skill 模块，每个 Skill 是一个独立的功能单元。

---

## 当前 Skills 列表

### 1. DailyGithub - 每日 GitHub 热门项目贴图生成器

**路径：** `skills/DailyGithub/`

**功能：** 从 GitHub Trending 日榜筛选 6 个开源项目，生成一张 1024×1536 的暖奶油色信息图，适合分享到社交媒体。指定项目模式下首位是指定项目，序号不代表全站排名。

**使用方式：**
```bash
python3 skills/DailyGithub/generate.py
```

**可选参数：**
- `--output PATH`：指定输出路径
- `--include URL`：额外包含指定项目（如 `https://github.com/TencentCloud/Octop`）
- `--date YYYY-MM-DD`：指定日期

**输出：** 一张 PNG 图片，包含 6 个项目的排名、名称、描述、语言、星标数、今日新增星标。

**数据来源：** GitHub Trending 页面 + GitHub Repository API

---

## 目录结构

```
skills/
├── README.md              # 本文件 - Skills 索引
└── DailyGithub/           # 每日 GitHub 热门项目贴图生成器
    ├── SKILL.md           # Skill 说明文档
    ├── generate.py        # 主程序
    └── output/            # 输出目录
        └── daily_github_YYYYMMDD.png
```

---

## 如何添加新 Skill

1. 在 `skills/` 下创建新文件夹，命名使用 PascalCase（如 `MyNewSkill/`）
2. 创建 `SKILL.md` 文件，包含 frontmatter 和说明文档
3. 编写主程序代码
4. 在本索引中添加条目

### SKILL.md 模板

```markdown
---
name: MyNewSkill
description: "简要描述此 Skill 的功能"
---

# MyNewSkill - 功能名称

## 功能
简要说明...

## 使用方式
```bash
python3 skills/MyNewSkill/main.py
```

## 输出
说明输出内容...
```

---

## 开发规范

- 每个 Skill 独立运行，不依赖其他 Skill
- 使用 Python 3.10+ 编写
- 依赖库：Pillow、requests（已安装）
- 输出文件统一放在 `output/` 子目录
- 图片尺寸按各 Skill 的视觉模板定义；DailyGithub 为 1024×1536（2:3）
- 使用 Noto Sans CJK / Noto Serif CJK 字体（已安装）
