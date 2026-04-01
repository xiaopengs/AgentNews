# AgentNews 项目说明书

> **目标：** 任何 AI Agent 接手此项目时，通过本文档即可了解项目全貌、当前进展和下一步行动。

---

## 📌 项目概述

**项目名称：** AgentNews - 科技博主 AI 写作助手

**核心目标：** 通过多个专业 AI Agent 协作，实现从信息获取 → 选题筛选 → 内容创作 → 质量把控 → 多平台发布的全自动工作流，让博主专注于选题策划和观点输出。

**定位人群：** 科技领域内容创作者（微信公众号、知乎、头条等）

**核心技术栈：**
- LLM：Claude（主）、GPT-4（备选）、通义千问（本土优化）
- Agent 编排：LangChain
- 数据存储：Redis（队列）、PostgreSQL（持久化）、向量数据库（知识库）
- 服务层：FastAPI、Celery、APScheduler

---

## 📁 项目结构

```
AgentNews/
├── src/
│   └── example.py          # ⚠️ 目前仅为占位文件，无实际功能
├── config/                 # 配置文件（待创建）
├── scripts/                # 脚本工具（待创建）
├── tests/                  # 测试（待创建）
├── docs/                   # 文档（待创建）
├── docker-compose.yml      # Docker 部署（待创建）
├── Dockerfile              # Docker 构建（待创建）
├── requirements.txt       # 依赖（待创建）
├── README.md              # 项目主说明
└── .gitignore
```

> ⚠️ **当前状态：** 项目架构设计完成（README 中的蓝图），但 **src/ 目录仅有占位文件**，核心代码尚未开发。

---

## ✅ 当前进展

### 已完成

| 内容 | 状态 | 说明 |
|------|------|------|
| 项目架构设计 | ✅ 完成 | README.md 中有完整的架构图和工作流设计 |
| 目录结构规划 | ✅ 完成 | 已在 README 中定义 |
| 需求分析 | ✅ 完成 | 博主痛点、内容类型矩阵、质量控制原则 |
| 技术选型 | ✅ 完成 | LangChain + Claude/GPT-4 + Redis/PG |
| 自动化日报 | ✅ 运作中 | 通过 WorkBuddy Automation 定时推送 |
| 仓库初始化 | ✅ 完成 | GitHub 仓库已建立 |

### 进行中

| 内容 | 状态 | 说明 |
|------|------|------|
| 信息收集 Agent | 🔄 待开发 | RSS fetcher、GitHub trending、Hacker News |
| 选题筛选 Agent | 🔄 待开发 | 热度评分、受众匹配、选题推荐 |
| 内容创作 Agent | 🔄 待开发 | 文章写作、风格学习、SEO 优化 |
| 质量把控 Agent | 🔄 待开发 | 事实核查、敏感词过滤、质量评分 |
| 发布分发 Agent | 🔄 待开发 | 微信公众号、知乎专栏、今日头条 |

---

## 🗺️ 开发路线图

### v0.1 — MVP（当前阶段）
- [ ] 基础信息收集 Agent（RSS、GitHub、Hacker News）
- [ ] 简单选题推荐输出
- [ ] Claude API 接入
- [ ] `src/agents/collector/` 模块开发

### v0.2 — 核心功能
- [ ] 完整的内容创作流程
- [ ] 博主风格学习（基于历史文章）
- [ ] 质量审核 Agent
- [ ] Web 审核界面（FastAPI）

### v0.3 — 自动化
- [ ] 定时任务调度（Celery + APScheduler）
- [ ] 微信公众号 API 对接
- [ ] 多平台适配输出

### v0.4 — 智能化
- [ ] 读者画像分析
- [ ] 内容效果追踪
- [ ] 智能选题推荐
- [ ] A/B 测试标题生成

---

## 🔧 技术规范

### 代码规范
- **语言：** Python 3.10+
- **格式化：** Black + isort
- **类型检查：** mypy
- **测试：** pytest
- **提交规范：** Conventional Commits（feat/fix/docs/style/refactor/test/chore）

### Git 工作流
```
main (稳定分支)
  └── develop (开发分支)
        └── feature/xxx, fix/xxx (功能分支)
```

### 环境变量（需创建 `.env`）
```
CLAUDE_API_KEY=          # Anthropic API Key
OPENAI_API_KEY=          # OpenAI API Key（可选）
WECHAT_APP_ID=           # 微信公众号 AppID（可选）
WECHAT_APP_SECRET=        # 微信公众号 AppSecret（可选）
DATABASE_URL=            # PostgreSQL 连接字符串
REDIS_URL=               # Redis 连接字符串
```

---

## 📍 下一步行动（Next Steps）

接手项目的 AI Agent 应按以下顺序推进：

### 优先级 1：搭建基础骨架
1. 创建 `requirements.txt`（LangChain、Claude SDK、FastAPI、Redis、psycopg2-binary 等）
2. 创建 `src/agents/collector/` — 信息收集 Agent
   - `rss_fetcher.py` — RSS 订阅源抓取
   - `github_trending.py` — GitHub Trending 抓取
3. 创建 `src/core/llm_client.py` — LLM 统一调用接口
4. 创建 `src/core/workflow.py` — 工作流引擎基础

### 优先级 2：跑通第一个 Agent
1. 接入 Claude API
2. 实现 GitHub Trending 收集 → Claude 整理输出
3. 验证 Agent 协作流程

### 优先级 3：扩展与集成
1. 添加更多信息源（36氪、Hacker News 等）
2. 开发选题筛选 Agent
3. 对接 Web 服务（FastAPI）

---

## 🔗 相关资源

- **GitHub 仓库：** https://github.com/xiaopengs/AgentNews
- **AI 日报推送：** WorkBuddy Automation（每周一、三、五、六）
- **依赖工具：** Claude API、GitHub API、RSS 订阅源

---

## 📝 维护记录

| 日期 | 操作 | 负责人 | 说明 |
|------|------|--------|------|
| 2026-04-01 | 项目初始化 | OpenClaw Agent | 仓库 clone，搭建项目说明文档 |
| 2026-04-01 | 设计文档编写 | OpenClaw Agent | 新建 `docs/` 目录，编写架构设计、目录结构、功能规格三份文档 |

### 文档清单

| 文档 | 路径 | 说明 |
|------|------|------|
| 架构设计 | `docs/01-架构设计.md` | 系统架构、Agent 设计、数据模型、API 设计、调度策略、安全设计 |
| 目录结构 | `docs/02-目录结构.md` | 完整目录树、职责说明、命名规范、导入规范 |
| 功能规格 | `docs/03-功能规格.md` | 功能矩阵、信息收集、选题筛选、内容创作、质量审核、发布分发详细规格 |
