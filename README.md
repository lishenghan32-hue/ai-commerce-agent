# AI Commerce Agent

一个用于电商数据分析与 AI 直播带货话术生成的智能 Agent。

## ✨ 功能

- 📊 商品数据分析
- 🤖 AI 自动生成直播带货话术
- 📝 评论分析与处理
- ⚡ 多风格话术生成（SSE 流式输出）
- 🔗 抖音/快手商品链接自动解析（Playwright）
- 📷 PaddleOCR 图片文字识别
- 🎯 结构化商品信息提取
- 📱 双 UI 模式（基础模式 + V2 工作流）

## 🧱 技术架构

- **Backend**: Python (FastAPI)
- **Database**: SQLite
- **AI**: MiniMax API
- **Crawler**: Playwright
- **OCR**: PaddleOCR
- **Frontend**: HTML + JavaScript + React CDN

## 📂 项目结构

```
ai-commerce-agent/
├── backend/
│   ├── main.py                    # FastAPI 应用入口
│   ├── config.py                  # 配置（API Key 等）
│   ├── api/                       # API 路由
│   │   ├── routes_production.py  # 话术生成接口
│   │   ├── routes_analysis.py    # 分析接口
│   │   └── ...
│   ├── services/                  # 业务逻辑层
│   │   ├── ai_service.py         # AI 服务
│   │   └── production_service.py # 生产服务
│   ├── crawler/                   # 爬虫模块
│   │   ├── douyin_parser.py      # 抖音商品解析
│   │   └── simple_parser.py      # 基础解析
│   ├── ai_engine/                 # AI 引擎
│   │   ├── ocr_service.py        # PaddleOCR
│   │   └── structure_service.py  # 结构化提取
│   └── static/                    # 前端静态文件
│       ├── index.html             # 基础模式
│       ├── workflow_v2.html       # V2 工作流模式
│       ├── js/app.js
│       └── css/styles.css
├── .env                           # 环境变量
├── requirements.txt               # Python 依赖
└── README.md
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# MiniMax API Key
MINIMAX_API_KEY=your-api-key-here
```

### 3. 启动服务

```bash
cd ai-commerce-agent
py -3 -m backend.main
```

### 4. 访问

- 基础模式：http://localhost:8000
- V2 工作流：http://localhost:8000/workflow_v2

## 📡 API 接口

### 商品解析

```bash
POST /api/parse-product
{
  "url": "https://v.douyin.com/..."
}
```

### 生成话术（SSE 流式）

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

## 📱 UI 模式

### 基础模式 (`/`)
- 左侧输入商品链接/评论
- 右侧 SSE 流式输出话术
- 支持话术重写、复制、导出

### V2 工作流模式 (`/workflow_v2`)
- ChatGPT 风格 AI Agent UI
- 顶部进度条（解析 → OCR → 结构化 → 话术）
- 子步骤实时状态指示
- StructuredCard AI 协作模式
- 支持中断生成

## 📸 Demo

![Demo](https://github.com/user-attachments/assets/fd81f0d6-709d-40a8-9767-cef3324d7d90)

## 🧑‍💻 开发

```bash
# 开发模式启动
py -3 -m backend.main

# 运行测试
curl http://localhost:8000/health
```

## 📄 许可证

MIT

## 🧑‍💻 作者

lishenghan32