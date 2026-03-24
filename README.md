# AI Commerce Agent

一个用于电商数据分析与内容生成的 AI Agent。

## ✨ 功能

- 📊 商品数据分析
- 🤖 AI 自动生成直播带货话术
- 📝 评论分析与处理
- ⚡ 多风格话术生成（SSE流式输出）
- 🔗 抖音/快手商品链接自动解析（Playwright）

## 🧱 技术架构

- Backend: Python (FastAPI)
- Database: SQLite
- AI: MiniMax API
- Crawler: Playwright

## 📂 项目结构

```
ai-commerce-agent/
├── backend/
│   ├── main.py                    # FastAPI 应用入口
│   ├── config.py                  # 配置（API Key 等）
│   ├── api/                       # API 路由
│   │   ├── routes_production.py   # 话术生成接口
│   │   ├── routes_analysis.py    # 分析接口
│   │   └── ...
│   ├── services/                  # 业务逻辑层
│   │   ├── ai_service.py          # AI 服务
│   │   └── production_service.py # 生产服务
│   ├── crawler/                   # 爬虫模块
│   │   └── douyin_parser.py      # 抖音商品解析
│   └── static/                    # 前端静态文件
│       ├── index.html
│       └── js/app.js
├── .env                           # 环境变量（API Key）
└── requirements.txt
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```
# MiniMax API Key - 替换为你的真实API Key
MINIMAX_API_KEY=your-api-key-here
```

### 3. 启动服务

```bash
cd ai-commerce-agent
py -3 -m backend.main
```

### 4. 访问

打开浏览器访问：http://localhost:8000

## 📡 API 接口

### 商品解析

```bash
POST /api/parse-product
{
  "url": "https://haohuo.jinritemai.com/..."
}
```

### 生成话术（SSE流式）

```bash
GET /api/generate-scripts-sse?product_name=商品名称&selling_points=卖点&comments=["评论1", "评论2"]
```

### 话术重写

```bash
POST /api/rewrite-script
{
  "script": {...},
  "mode": "强化转化"
}
```

## 📸 Demo

![Demo](https://github.com/user-attachments/assets/fd81f0d6-709d-40a8-9767-cef3324d7d90)

## 🧑‍💻 作者

lishenghan32