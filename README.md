# AI Commerce Agent

一个用于电商数据分析与内容生成的 AI Agent。

## ✨ 功能

- 📊 商品数据分析
- 🤖 AI 自动生成分析报告
- 📝 笔记 / 评论处理
- 📦 商品信息管理
- ⚡ 基于 API 的任务执行系统

## 🧱 技术架构

- Backend: Python (FastAPI)
- Database: SQLite
- AI: Minimax API

## 📂 项目结构
backend/

├── api/ # 接口层

├── models/ # 数据模型

├── services/ # 业务逻辑

├── ai_engine/ # AI处理模块

├── crawler/ # 数据抓取

├── main.py # 启动入口


## 🚀 快速开始

```bash
pip install -r requirements.txt
python backend/main.py

```
## **创建任务**
POST /tasks
获取商品分析
GET /analysis/{product_id}


##🎯 **项目目标**
---

构建一个可以自动完成：

- 数据抓取

- 数据分析

- 内容生成

的电商 AI 自动化工具。


##🧑‍💻 **作者**
---
lishenghan32
