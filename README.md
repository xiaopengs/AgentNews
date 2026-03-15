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

## 开发路线图

### v0.1 - MVP (当前)
- [x] 项目架构设计
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
