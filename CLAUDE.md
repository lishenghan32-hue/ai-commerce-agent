# AI Commerce Agent - Claude Code 开发指南

## 1. 项目概述

AI Commerce Insight Generator 是一个用于分析抖音商品链接、爬取小红书笔记/评论、使用 AI 分析用户反馈、生成直播带货话术和 PPT 的 Web 应用。

- **技术栈**：FastAPI + MiniMax AI + PaddleOCR + Playwright
- **前端**：原生 HTML + JavaScript + React CDN
- **运行端口**：http://localhost:8000
- **启动命令**：`py -3 -m backend.main`

## 2. 项目结构

```
ai-commerce-agent/
├── backend/
│   ├── main.py                    # FastAPI 应用入口
│   ├── config.py                  # 配置（API Key 等）
│   │
│   ├── api/                       # API 路由
│   │   ├── routes_production.py  # 生产接口（话术生成）
│   │   └── export_service.py     # 导出服务
│   │
│   ├── services/                  # 业务逻辑层
│   │   ├── ai_service.py         # AI 服务（MiniMax 集成）
│   │   └── production_service.py # 生产服务
│   │
│   ├── crawler/                   # 爬虫模块
│   │   ├── douyin_parser.py      # 抖音商品解析（Playwright + PaddleOCR）
│   │   └── simple_parser.py      # 基础 HTML 解析
│   │
│   ├── ai_engine/                 # AI 引擎
│   │   ├── ocr_service.py        # PaddleOCR 文字识别
│   │   └── structure_service.py  # 结构化信息提取
│   │
│   └── static/
│       ├── workflow_v2.html       # 工作流模式（AI Agent UI）
│       ├── js/utils.js            # 工具函数
│       ├── js/api.js              # API 调用
│       ├── css/workflow_v2.css    # 样式文件
│       └── downloads/             # 导出文件目录
│
├── .env                           # 环境变量（API Key）
├── .gitignore
├── requirements.txt               # Python 依赖
├── CLAUDE.md                      # 开发指南（本文件）
└── README.md                      # 项目说明
```

## 3. 后端接口说明

### 3.1 生产接口（主要使用）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/parse-product` | POST | 解析商品链接（V4: Playwright 抖音，V3: HTML+AI） |
| `/api/generate-scripts-sse` | GET | SSE 流式生成话术（实时进度） |
| `/api/generate-script-from-comments` | POST | 从评论生成单条话术 |
| `/api/generate-multi-style-scripts-from-comments` | POST | 生成多风格话术（含评分） |
| `/api/rewrite-script` | POST | 重写话术（4种模式） |
| `/api/export-scripts` | POST | 导出话术（TXT/Markdown） |

### 3.2 SSE 流式接口

**`GET /api/generate-scripts-sse`**

参数：
- `product_url`: 商品链接（可选）
- `product_name`: 商品名称
- `product_info`: 商品信息
- `selling_points`: 卖点
- `structured`: JSON 格式结构化数据
- `comments`: JSON 数组格式的评论

返回：Server-Sent Events 流式数据，包含进度事件和话术 chunk

### 3.3 商品解析接口

**`POST /api/parse-product`**

请求体：
```json
{
  "url": "https://v.douyin.com/..."
}
```

返回：
- 淘宝 → 美白精华液
- 抖音/快手 → Playwright 动态解析 + PaddleOCR 图片识别
- 京东 → 智能手环

返回字段：
```json
{
  "name": "商品名称",
  "selling_points": "卖点1, 卖点2, 卖点3",
  "ocr_text": "图片识别文字",
  "structured": {
    "title": "商品标题",
    "material": "材质",
    "function": "功能",
    "scene": "使用场景",
    "target": "目标人群",
    "advantage": "核心优势"
  },
  "comments": ["评论1", "评论2", ...]
}
```

### 3.4 话术重写接口

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

### 3.5 健康检查

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 返回工作流模式页面 |
| `/health` | GET | 健康检查 |

## 4. 前端页面结构

### 4.1 工作流模式 (`workflow_v2.html`)

- **UI**：ChatGPT 风格 AI Agent UI
- **特性**：
  - 顶部进度条（解析 → OCR → 结构化 → 话术）
  - 子步骤实时状态指示器
  - 多图 OCR 逐张渲染
  - StructuredCard AI 协作模式（编辑/恢复）
  - AbortController 中断支持
  - 流式话术实时渲染
- **访问**：`http://localhost:8000`

## 5. 已实现功能

### 5.1 核心功能
- [x] FastAPI 后端搭建
- [x] MiniMax AI 集成（评论分析 + 话术生成）
- [x] 多风格话术生成（带货型/共情型/理性型）
- [x] 话术评分系统（自动选出最佳脚本）
- [x] 结构化商品信息提取
- [x] PaddleOCR 图片文字识别
- [x] 前端页面（工作流模式）

### 5.2 流式输出
- [x] SSE 流式输出（EventSource）
- [x] 打字机效果
- [x] 骨架屏 UI
- [x] 实时进度更新

### 5.3 商品链接解析
- [x] 链接解析自动填充
- [x] Playwright 动态页面解析（抖音/快手）
- [x] PaddleOCR 图片文字识别
- [x] AI fallback 补全信息
- [x] 结构化信息提取

### 5.4 话术操作
- [x] 复制功能（单部分 + 完整话术）
- [x] 话术重写（4种模式）
- [x] 导出功能（TXT/Markdown）

### 5.5 工作流 UI
- [x] 进度条组件
- [x] 子步骤状态指示
- [x] 多图 OCR 逐张渲染
- [x] AI 协作模式（StructuredCard）
- [x] 中断生成按钮
- [x] 输入框优化

### 5.6 话术生成流程
```
商品链接 → 解析商品 → OCR识别 → 结构化提取 → AI生成话术 → 评分排序 → 流式返回
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
- React 组件保持在单 HTML 文件中（workflow_v2.html）

### 6.4 其他
- 使用 Git 管理代码，提交前确认变更内容
- 敏感信息（API Key）不提交到 Git
- 优先使用 Python 标准库和已有依赖
- **安全配置**：
  - `.env` 文件包含敏感配置，已加入 `.gitignore`
  - CORS 默认只允许 `localhost:8000`，生产环境需修改 `config.py`
  - `debug` 默认关闭

## 7. 启动方式

```bash
# 启动服务
cd ai-commerce-agent
py -3 -m backend.main

# 访问工作流模式
http://localhost:8000
```

## 8. 待开发功能

- [ ] 小红书爬虫（爬取笔记/评论）
- [ ] PPT 生成器
- [ ] 用户认证
- [ ] 数据持久化（商品、任务存储）
