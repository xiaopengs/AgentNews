# AgentNews - 科技博主 AI 写作助手

> 一个专为科技博主打造的微信公众号内容创作自动化工具链

## 项目定位

科技博主的核心痛点：
- **信息过载**：每天海量科技资讯，筛选有价值内容耗时巨大
- **时效性要求**：热点稍纵即逝，错过黄金发布窗口流量减半
- **原创压力**：既要保证质量，又要保持更新频率
- **多平台分发**：微信、知乎、头条等平台格式要求各异

**AgentNews** 通过 AI Agent 协作，构建从信息获取到内容发布的全自动工作流，让博主专注于选题策划和观点输出。

---

## 核心设计理念

### 1. Agent 协作架构

不是简单的"AI 写文章"，而是多个专业 Agent 协同工作：

```
┌─────────────────────────────────────────────────────────────────┐
│                      AgentNews 工作流                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ 信息收集  │───▶│ 内容筛选  │───▶│ 内容创作  │───▶│ 质量把控  │  │
│  │  Agent   │    │  Agent   │    │  Agent   │    │  Agent   │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │              │              │              │           │
│       ▼              ▼              ▼              ▼           │
│   RSS/新闻源      价值评估       深度改写        事实核查         │
│   GitHub Trend   热点检测       观点生成        敏感词过滤       │
│   Hacker News    受众匹配       排版优化        合规审查         │
│   ProductHunt    竞品分析       标题润色        质量评分         │
│                                                                  │
│                          ▼                                      │
│                   ┌──────────┐                                  │
│                   │ 发布分发  │                                  │
│                   │  Agent   │                                  │
│                   └──────────┘                                  │
│                          │                                      │
│         ┌────────────────┼────────────────┐                    │
│         ▼                ▼                ▼                    │
│    微信公众号         知乎专栏          今日头条                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. 内容类型矩阵

| 内容类型 | 信息来源 | 创作方式 | 发布频率 | 自动化程度 |
|---------|---------|---------|---------|-----------|
| **热点速递** | 新闻RSS、社交媒体 | 快速整合+观点 | 每日1-2篇 | 80% |
| **产品评测** | 官网、测评视频 | 深度分析+体验 | 每周2-3篇 | 40% |
| **技术解读** | 论文、技术博客 | 代码实践+解析 | 每周1篇 | 30% |
| **行业观察** | 财报、行业报告 | 数据可视化 | 每月1篇 | 50% |
| **观点评论** | 热点事件 | 个人观点输出 | 不定期 | 20% |

### 3. 质量控制原则

**AI 是副驾驶，人类是机长：**

- ✅ AI 负责：信息收集、初稿生成、排版美化、多平台适配
- ⚠️ AI 辅助：观点提炼、标题优化、内容审核
- 🔒 人工把控：选题决策、核心观点、最终审核、发布确认

---

## 自动化工作流详解

### 阶段一：智能信息收集

```python
# 信息源配置示例
sources = {
    # 科技新闻
    "news": [
        "https://www.36kr.com/feed",           # 36氪
        "https://www.ifanr.com/feed",          # 爱范儿
        "https://www.pingwest.com/feed",       # 品玩
    ],
    
    # 技术社区
    "tech": [
        "https://github.com/trending",         # GitHub Trending
        "https://news.ycombinator.com/rss",    # Hacker News
        "https://www.producthunt.com/feed",    # ProductHunt
    ],
    
    # 学术前沿
    "academic": [
        "https://arxiv.org/list/cs.AI/recent", # AI 论文
        "https://paperswithcode.com/rss",      # 代码论文
    ],
    
    # 公司动态
    "companies": [
        "OpenAI Blog",
        "Google AI Blog", 
        "Microsoft Research Blog",
    ]
}
```

**Agent 任务：**
- 定时抓取各信息源最新内容
- 去重、分类、打标签
- 初步质量评估（阅读量、评论数、转发数）

### 阶段二：智能选题筛选

```python
# 选题评分模型
def score_topic(article):
    score = 0
    
    # 热度权重 (40%)
    score += article.trend_score * 0.4
    
    # 受众匹配度 (30%)
    score += calculate_audience_match(article, blogger_profile) * 0.3
    
    # 时效性 (20%)
    score += calculate_timeliness(article) * 0.2
    
    # 原创空间 (10%)
    score += calculate_originality_space(article) * 0.1
    
    return score
```

**输出：每日选题推荐清单**

```markdown
## 今日选题推荐 (2026-03-15)

### 🔥 高优先级
1. **Claude 3.7 发布：编程能力大幅提升** 
   - 来源：Anthropic Blog | 热度：98分 | 建议：产品速递
   - 关键角度：与 GPT-4 编程能力对比测试

2. **苹果取消造车项目，转向生成式 AI**
   - 来源：彭博社 | 热度：95分 | 建议：行业观察
   - 关键角度：对自动驾驶行业的影响

### 📊 中优先级  
3. **GitHub Copilot Workspace 公测**
4. **Sora 正式开放 API**

### 📰 待观察
5. **小米汽车 SU7 交付数据**
```

### 阶段三：内容创作流程

```
输入：选题 + 参考素材
    │
    ▼
┌─────────────────────────────────────────┐
│           内容创作 Agent                 │
├─────────────────────────────────────────┤
│  Step 1: 资料深度消化                    │
│  - 阅读所有参考资料                      │
│  - 提取关键数据和观点                    │
│  - 识别争议点和讨论空间                  │
├─────────────────────────────────────────┤
│  Step 2: 文章结构规划                    │
│  - 确定文章类型（速递/深度/观点）        │
│  - 设计叙事逻辑                          │
│  - 规划小标题和段落                      │
├─────────────────────────────────────────┤
│  Step 3: 内容生成                        │
│  - 写作风格：博主历史文章风格学习        │
│  - 内容要求：原创、有观点、有洞察        │
│  - 格式规范：微信公众号排版标准          │
├─────────────────────────────────────────┤
│  Step 4: 质量优化                        │
│  - 标题：3个候选，选最优                 │
│  - 导语：黄金3秒原则                     │
│  - 排版：图文搭配、重点高亮              │
└─────────────────────────────────────────┘
    │
    ▼
输出：初稿 + 修改建议
```

### 阶段四：人工审核与发布

```markdown
## 审核清单

- [ ] 事实核查：关键数据和引用是否准确？
- [ ] 观点检查：是否有独特见解？是否与已有内容重复？
- [ ] 合规审查：敏感话题处理是否得当？
- [ ] 排版确认：图片、格式、链接是否正常？
- [ ] 发布设置：时间、标签、摘要是否完善？

审核意见：_______________________
```

---

## 技术实现方案

### 核心技术栈

```
┌─────────────────────────────────────────────────────┐
│                    技术架构                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   Claude    │  │   GPT-4     │  │  通义千问   │ │
│  │  (主创作)   │  │ (备选/对比) │  │ (本土优化)  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
│          │               │                │        │
│          └───────────────┼────────────────┘        │
│                          ▼                         │
│                 ┌─────────────────┐                │
│                 │   LangChain     │                │
│                 │  Agent 编排框架  │                │
│                 └─────────────────┘                │
│                          │                         │
│  ┌───────────────────────┼───────────────────────┐ │
│  │                       ▼                       │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │ │
│  │  │  Redis   │  │ PostgreSQL│  │ 向量数据库│    │ │
│  │  │ (队列)   │  │ (持久化)  │  │ (知识库) │    │ │
│  │  └──────────┘  └──────────┘  └──────────┘    │ │
│  │               数据层                          │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │                 服务层                         │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐         │ │
│  │  │ FastAPI │ │ Celery  │ │ APSched │         │ │
│  │  │ (API)   │ │ (异步)  │ │ (定时)  │         │ │
│  │  └─────────┘ └─────────┘ └─────────┘         │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 项目结构

```
AgentNews/
├── src/
│   ├── agents/                 # Agent 模块
│   │   ├── collector/         # 信息收集 Agent
│   │   │   ├── rss_fetcher.py
│   │   │   ├── github_trending.py
│   │   │   └── news_aggregator.py
│   │   ├── curator/           # 选题筛选 Agent
│   │   │   ├── topic_scorer.py
│   │   │   ├── trend_detector.py
│   │   │   └── recommender.py
│   │   ├── writer/            # 内容创作 Agent
│   │   │   ├── article_writer.py
│   │   │   ├── style_learner.py
│   │   │   └── seo_optimizer.py
│   │   ├── reviewer/          # 质量把控 Agent
│   │   │   ├── fact_checker.py
│   │   │   ├── sensitive_filter.py
│   │   │   └── quality_scorer.py
│   │   └── publisher/         # 发布分发 Agent
│   │       ├── wechat.py
│   │       ├── zhihu.py
│   │       └── toutiao.py
│   │
│   ├── core/                   # 核心引擎
│   │   ├── workflow.py        # 工作流引擎
│   │   ├── llm_client.py      # LLM 统一接口
│   │   ├── vector_store.py    # 向量存储
│   │   └── scheduler.py       # 调度系统
│   │
│   ├── data/                   # 数据层
│   │   ├── models/            # 数据模型
│   │   ├── repositories/      # 数据仓库
│   │   └── migrations/        # 数据迁移
│   │
│   ├── api/                    # API 层
│   │   ├── routes/            # 路由
│   │   ├── schemas/           # 数据模式
│   │   └── middleware/        # 中间件
│   │
│   └── utils/                  # 工具函数
│       ├── logger.py
│       ├── config.py
│       └── helpers.py
│
├── config/                     # 配置文件
│   ├── settings.yaml          # 主配置
│   ├── sources.yaml           # 信息源配置
│   └── prompts/               # Prompt 模板
│
├── scripts/                    # 脚本工具
│   ├── setup.sh               # 环境初始化
│   └── daily_run.py           # 每日任务入口
│
├── tests/                      # 测试
├── docs/                       # 文档
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/xiaopengs/AgentNews.git
cd AgentNews

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置

```bash
# 复制配置模板
cp config/settings.example.yaml config/settings.yaml

# 编辑配置，填入必要的 API Keys
# - LLM API Key (Claude/GPT)
# - 微信公众号配置（可选）
# - 数据库连接信息
```

### 3. 运行

```bash
# 启动每日选题推荐
python scripts/daily_run.py --task topics

# 生成文章初稿
python scripts/daily_run.py --task write --topic "Claude 3.7 发布"

# 启动 Web 服务（审核界面）
python -m src.api.main
```

---

## AI 日报归档

> 每周一、三、五、六自动推送，聚焦 **AI Coding** 与**具身智能**方向的重要动态。

<details>
<summary>📅 2026-03-21（星期六）</summary>

### 🔵 1. Cursor 发布自研编程模型 Composer 2

**事件：** Cursor 正式发布首个自研模型 Composer 2，通过持续预训练 + 强化学习训练而来，在 SWE-bench Multilingual 上达到 **73.7%**、Terminal-Bench 2.0 达到 **61.7%**。定价仅 $0.50/$2.50（每百万 token），远低于 Anthropic/OpenAI 同级别模型。同步发布新界面 Glass alpha 版。

**为什么值得关注：** Cursor 从"用别人模型"走向"自己训练编程专用模型"，是 AI coding 赛道进入纵深竞争的信号。极低的定价策略直指 Anthropic 和 OpenAI 的核心利益，后续博弈值得持续观察。

---

### 🔴 2. OpenAI 收购 Python 工具链公司 Astral，并计划推出桌面超级应用

**事件：** OpenAI 收购了 Ruff、uv、ty 等工具的开发商 Astral（月下载量达数亿次），意在将其整合进 Codex 编程智能体，覆盖完整开发周期。与此同时，《华尔街日报》报道 OpenAI 正将 ChatGPT + Codex + Atlas 浏览器合并为一个统一的桌面"超级应用"。

**为什么值得关注：** 收购 Astral 意味着 OpenAI 在 AI coding 上从"模型层"延伸至"工具链层"，对现有 Python 生态的影响深远。超级应用战略则直接对标 Google 和 Anthropic，是产品整合的关键一步。

---

### 🟢 3. Google AI Studio 推出"全栈 vibe coding"平台

**事件：** Google AI Studio 上线"全栈 vibe coding"功能，集成 Antigravity 编程智能体 + Firebase，支持实时多人协作、自动依赖安装、API 密钥管理，通过自然语言提示即可生成并部署生产级应用。同步推出 AI 原生 UI 设计工具 Stitch。

**为什么值得关注：** Google 把模型能力、数据库、部署打通成一条流水线，是对"从想法到上线"全流程的激进整合，对 Replit、Vercel、Cursor 等均构成竞争压力。

---

### 🟡 4. LangChain 发布 Open-SWE + NVIDIA Newton 开源机器人物理引擎

**事件（双线）：**
- **Open-SWE**：LangChain 发布开源异步编程智能体，支持非阻塞并行处理，面向复杂软件工程任务，透明可扩展。
- **Newton**：NVIDIA Warp 衍生的开源 GPU 加速物理仿真引擎，专为机器人研究设计，Apache-2.0 授权，登上 GitHub Trending。

**为什么值得关注：** Open-SWE 是 LangChain 从框架商走向智能体产品的重要一步；Newton 为具身智能研究提供了高性能开源仿真底座，降低了机器人学习的门槛。

---

### 🟣 5. 中国正式发布人形机器人与具身智能国家标准体系

**事件：** 中国发布《2026版人形机器人与具身智能标准体系》，这是国内首个覆盖具身智能全产业链的顶层标准设计，涵盖感知、运动、交互等核心环节。官方数据显示中国拥有全球 60% 的 AI 专利，机器人专利数量占全球约 2/3。

**为什么值得关注：** 标准出台意味着具身智能产业从"野蛮生长"转向"规范化竞争"阶段，对国内相关创业公司和供应链影响深远，也是中国在这一赛道确立技术话语权的重要动作。

</details>

---

## 开发路线图

### v0.1 - MVP (当前)
- [x] 项目架构设计
- [x] 自动化日报调度（WorkBuddy Automation）
- [ ] 基础信息收集 Agent
- [ ] 简单选题推荐
- [ ] Claude 接入

### v0.2 - 核心功能
- [ ] 完整的内容创作流程
- [ ] 博主风格学习
- [ ] 质量审核 Agent
- [ ] Web 审核界面

### v0.3 - 自动化
- [ ] 定时任务调度
- [ ] 微信公众号 API 对接
- [ ] 多平台适配

### v0.4 - 智能化
- [ ] 读者画像分析
- [ ] 内容效果追踪
- [ ] 选题智能推荐
- [ ] A/B 测试标题

---

## 贡献指南

欢迎贡献代码、提出建议或反馈问题！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: 添加某某功能'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 许可证

本项目采用 MIT 许可证。

---

## 联系方式

- **GitHub**: https://github.com/xiaopengs/AgentNews
- **Issues**: https://github.com/xiaopengs/AgentNews/issues

---

*让 AI 成为你的写作伙伴，而不是替代者。*
