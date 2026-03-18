# AI Commerce Agent - Claude Code 开发指南

## 1. 项目概述

AI Commerce Insight Generator 是一个用于分析抖音商品链接、爬取小红书笔记/评论、使用 AI 分析用户反馈、生成直播带货话术和 PPT 的 Web 应用。

- **技术栈**：FastAPI + SQLAlchemy + MiniMax AI
- **数据库**：SQLite (test.db)
- **前端**：原生 HTML + JavaScript
- **运行端口**：http://localhost:8000

## 2. 项目结构

```
ai-commerce-agent/
├── backend/
│   ├── main.py                    # FastAPI 应用入口
│   ├── config.py                  # 配置（API Key 等）
│   ├── base.py                    # SQLAlchemy Base
│   ├── database.py                # 数据库连接
│   ├── init_database.py          # 数据库初始化
│   │
│   ├── api/                       # API 路由
│   │   ├── routes_products.py     # 商品相关接口
│   │   ├── routes_tasks.py        # 任务相关接口
│   │   ├── routes_test.py         # 测试接口
│   │   ├── routes_analysis.py     # 分析接口
│   │   └── routes_production.py   # 生产接口（话术生成）
│   │
│   ├── services/                  # 业务逻辑层
│   │   ├── ai_service.py          # AI 服务（MiniMax 集成）
│   │   └── production_service.py   # 生产服务
│   │
│   ├── schemas/                   # Pydantic 模型
│   │   └── analysis.py
│   │
│   ├── models/                    # SQLAlchemy 模型
│   │   ├── product_model.py
│   │   ├── comment_model.py
│   │   ├── analysis_model.py
│   │   ├── task_model.py
│   │   └── note_model.py
│   │
│   ├── crawler/                   # 爬虫模块（预留）
│   ├── ai_engine/                 # AI 引擎（预留）
│   └── ppt_generator/             # PPT 生成器（预留）
│
│   └── static/
│       └── index.html             # 前端页面
│
├── .env                           # 环境变量（API Key）
├── .gitignore
└── README.md
```

## 3. 后端接口说明

### 3.1 生产接口（当前主要使用）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/generate-script-from-comments` | POST | 从评论生成话术 |

**请求体：**
```json
{
  "comments": ["效果很好", "价格有点贵", "会反弹吗"]
}
```

**响应：**
```json
{
  "opening_hook": "开场吸引话术",
  "pain_point": "痛点描述",
  "solution": "解决方案",
  "proof": "证明/案例",
  "offer": "促单话术"
}
```

### 3.2 分析接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/analyze-comments` | POST | 分析评论提取洞察 |
| `/api/generate-script` | POST | 基于洞察生成话术 |

### 3.3 健康检查

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 返回 index.html 或 API 信息 |
| `/health` | GET | 健康检查 |

## 4. 前端页面结构

`backend/static/index.html` 是唯一的前端页面：

- **功能**：输入评论，生成 3 条直播带货话术
- **UI**：红色主题 (#ff4757)，卡片式布局
- **交互**：
  - 输入框输入评论（每行一条）
  - 点击"生成3条脚本"按钮
  - 每个脚本有 5 个部分：开头吸引、痛点、解决方案、证明、促单
  - 每个部分有单独的"复制"按钮
  - 每条脚本有"复制完整话术"按钮

## 5. 已实现功能

### 5.1 核心功能
- [x] FastAPI 后端搭建
- [x] MiniMax AI 集成（评论分析 + 话术生成）
- [x] SQLite 数据库模型
- [x] 一键从评论生成话术接口
- [x] 前端页面（多脚本生成 + 复制功能）

### 5.2 话术生成流程
```
评论输入 → AI分析评论 → AI生成话术 → 返回5部分话术
```

话术结构：
1. **开头吸引** (opening_hook) - 抓住观众注意力
2. **痛点** (pain_point) - 描述用户痛点
3. **解决方案** (solution) - 产品如何解决
4. **证明** (proof) - 案例/数据证明
5. **促单** (offer) - 限时优惠促使下单

## 6. 开发约束

### 6.1 接口规范
- **不随意修改已有接口**：已有接口的路径、请求/响应格式保持稳定
- 如需扩展：新增接口，不修改现有接口
- 修改接口前需与用户确认

### 6.2 架构规范
- **前后端分离**：后端提供 API，前端通过 fetch 调用
- **分层架构**：routes → services → AI
- **Schema 驱动**：使用 Pydantic 定义请求/响应模型

### 6.3 UI 规范
- **风格保持一致**：
  - 主色调：红色 (#ff4757)
  - 布局：简洁卡片式
  - 交互：loading 状态、复制反馈
- 新增页面需遵循现有风格

### 6.4 其他
- 使用 Git 管理代码，提交前确认变更内容
- 敏感信息（API Key）不提交到 Git
- 优先使用 Python 标准库和已有依赖

## 7. 启动方式

```bash
# 激活虚拟环境（如有）
# source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# 启动服务
cd ai-commerce-agent
python -m backend.main

# 访问
http://localhost:8000
```

## 8. 待开发功能

- [ ] 小红书爬虫（爬取笔记/评论）
- [ ] 抖音商品解析
- [ ] PPT 生成器
- [ ] 用户认证
- [ ] 数据持久化（商品、任务存储）
