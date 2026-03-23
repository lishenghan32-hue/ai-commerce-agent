# AI Commerce Agent - Claude Code 开发指南

## 1. 项目概述

AI Commerce Insight Generator 是一个用于分析抖音商品链接、爬取小红书笔记/评论、使用 AI 分析用户反馈、生成直播带货话术和 PPT 的 Web 应用。

- **技术栈**：FastAPI + SQLAlchemy + MiniMax AI
- **数据库**：SQLite (test.db)
- **前端**：原生 HTML + JavaScript
- **运行端口**：http://localhost:8000
- **启动命令**：`py -3 -m backend.main`

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
│   │   ├── routes_production.py   # 生产接口（话术生成）
│   │   └── export_service.py      # 导出服务
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
│       ├── index.html             # 前端页面
│       ├── js/app.js              # 前端逻辑
│       └── css/styles.css          # 样式文件
│
├── .env                           # 环境变量（API Key）
├── .gitignore
└── README.md
```

## 3. 后端接口说明

### 3.1 生产接口（主要使用）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/generate-script-from-comments` | POST | 从评论生成单条话术 |
| `/api/generate-multi-style-scripts-from-comments` | POST | 生成多风格话术（含评分） |
| `/api/generate-scripts-sse` | GET | SSE 流式生成话术（实时打字机效果） |
| `/api/parse-product` | POST | 解析商品链接（Mock 数据） |
| `/api/rewrite-script` | POST | 重写话术（4种模式） |
| `/api/export-scripts` | POST | 导出话术（TXT/Markdown） |

### 3.2 SSE 流式接口

**`GET /api/generate-scripts-sse`**

参数：
- `product_url`: 商品链接（可选）
- `product_name`: 商品名称
- `product_info`: 商品信息
- `selling_points`: 卖点
- `comments`: JSON 数组格式的评论

返回：Server-Sent Events 流式数据

### 3.3 话术重写接口

**`POST /api/rewrite-script`**

请求体：
```json
{
  "script": {
    "style": "带货型",
    "opening_hook": "...",
    "pain_point": "...",
    "solution": "...",
    "proof": "...",
    "offer": "..."
  },
  "mode": "强化转化"
}
```

重写模式：
- `强化转化`：增强促单效果
- `更口语`：改为更自然的口语化表达
- `更理性`：改为更理性的分析风格
- `更简短`：精简内容

### 3.4 商品解析接口

**`POST /api/parse-product`**

请求体：
```json
{
  "url": "https://item.taobao.com/..."
}
```

返回 Mock 数据：
- 淘宝 → 美白精华液
- 抖音 → 无线蓝牙耳机
- 京东 → 智能手环

### 3.5 健康检查

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 返回 index.html |
| `/health` | GET | 健康检查 |

## 4. 前端页面结构

`backend/static/index.html` 是前端页面：

- **功能**：输入评论/商品链接，生成直播带货话术
- **UI**：极简高级风格（灰白主题 + 紫色强调色 #667eea）
- **交互**：
  - 输入商品链接自动解析填充
  - 输入评论（每行一条）
  - 点击生成按钮，SSE 流式输出
  - 实时打字机效果 + 骨架屏动画
  - 3 种风格话术可折叠展示
  - 最佳脚本自动标星
  - 每条话术支持复制和重写

## 5. 已实现功能

### 5.1 核心功能
- [x] FastAPI 后端搭建
- [x] MiniMax AI 集成（评论分析 + 话术生成）
- [x] SQLite 数据库模型
- [x] 多风格话术生成（带货型/共情型/理性型）
- [x] 话术评分系统（自动选出最佳脚本）
- [x] 前端页面

### 5.2 流式输出
- [x] 真正 SSE 流式输出（EventSource）
- [x] 打字机效果
- [x] 骨架屏 UI
- [x] 思考动画

### 5.3 商品链接解析
- [x] 链接解析自动填充
- [x] Mock 数据：淘宝、抖音、京东

### 5.4 话术操作
- [x] 复制功能（单部分 + 完整话术）
- [x] 话术重写（4种模式）
- [x] 导出功能（TXT/Markdown）

### 5.5 话术生成流程
```
评论/商品链接 → AI分析评论 → AI生成多风格话术 → 评分排序 → 流式返回
```

话术结构（5部分）：
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
- **前后端分离**：后端提供 API，前端通过 fetch/EventSource 调用
- **分层架构**：routes → services → AI
- **Schema 驱动**：使用 Pydantic 定义请求/响应模型

### 6.3 UI 规范
- **风格保持一致**：
  - 主色调：灰白 + 紫色强调 (#667eea)
  - 布局：简洁卡片式
  - 交互：loading 状态、复制反馈、展开/收起动画
- 新增页面需遵循现有风格

### 6.4 其他
- 使用 Git 管理代码，提交前确认变更内容
- 敏感信息（API Key）不提交到 Git
- 优先使用 Python 标准库和已有依赖

## 7. 启动方式

```bash
# 启动服务
cd ai-commerce-agent
py -3 -m backend.main

# 访问
http://localhost:8000
```

## 8. 待开发功能

- [ ] 小红书爬虫（爬取笔记/评论）
- [ ] 真实商品链接解析 API
- [ ] PPT 生成器
- [ ] 用户认证
- [ ] 数据持久化（商品、任务存储）
