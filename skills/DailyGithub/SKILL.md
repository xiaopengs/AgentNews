---
name: DailyGithub
description: "从 GitHub Trending 日榜筛选六个项目，生成一张中文开源项目介绍贴图，使用暖奶油色 2:3 视觉模板。"
---

# DailyGithub

## 运行

```bash
python3 skills/DailyGithub/generate.py --include https://github.com/TencentCloud/Octop
```

参数：`--output PATH` 指定 PNG 路径；`--include URL` 将指定项目放在首位，再补足日榜中新增 Star 最多的五个项目；`--date YYYY-MM-DD` 设置图片日期和星期（不会获取历史数据）。默认输出 `output/daily_github_YYYYMMDD.png`，只生成一张图。

依赖：Python 3.10+、Pillow、requests，以及 NotoSansCJK Regular/Bold 字体。

## 视觉规范

以用户提供的 1024×1536 视觉稿为坐标基准，不再使用 1080×1920 画布。

- 页眉：标识位于 (44,22)，标题位于 (130,25)，日期右对齐区域。
- 横幅：(38,107)，尺寸 952×151。只允许等比缩放与裁切，禁止独立拉伸宽高。人物完整保留，标语单独绘制。
- 六卡片边界集中在 `CARD_BOXES`；左边界 38，右边界 990。卡片、序号、图标不互相覆盖。
- 序号按实际字形包围盒水平和垂直居中；图标 70×70，位于 x=106。
- 项目标题、元信息、正文及标签统一使用 x=201 的内容网格。标题使用无衬线粗体 20px，正文 16px，元信息 15px，标签 13px。
- 前两卡正文采用较窄文本栏，与参考图相近地换成两行；其余描述保持内容完整。英文单词不拆分，中文闭合标点不得单独位于行首。
- 标签采用对应序号色的浅色背景；涨幅只显示一次，浅底彩字，右边界 972，“今日”单独位于下方。
- 不通过截断正文掩盖溢出；标题、正文和标签越界时直接报错，要求精简内容后重跑。

## 内容与来源

数据来自 GitHub Trending 日榜 HTML（不是官方 Trending API）；指定项目未在榜时，使用 GitHub Repository API 补充总 Star/Fork，日新增显示“暂无”，不把未知量伪装成零。

卡片数字在指定项目模式下是展示序号，不代表全站增速排名。GitHub Trending 不是全 GitHub 仓库的完整排名。运行前核对项目 README 与中文描述，未知项目应补充经核实的中文介绍及标签，不能声称英文回退已经翻译。

## 验收

```bash
python3 -m unittest discover -s skills/DailyGithub -p 'test_*.py'
```

每次更新后必须真实运行并打开 PNG，检查人物比例、六张卡片、文字边界、标点、标识与颜色。尺寸检查和单元测试只证明排版约束成立，不能证明与参考图逐像素相同。

当前插画为重新绘制的素材；项目小图标为示意性重绘，不是全部项目的官方标识。原稿的手写字、纹理和插画细节仍有差异，不应宣称已经严格 1:1 复刻。
