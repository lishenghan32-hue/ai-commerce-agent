# AI Commerce Agent

一个面向电商场景的 AI 直播话术生成项目。当前版本聚焦单次生成链路：商品解析、OCR 识别、结构化信息确认、用户评论生成、单份话术流式输出。

## 当前能力

- 商品链接解析
- OCR 图片文字识别
- AI 提取结构化商品信息
- 用户手动触发评论生成，并支持重新生成评论
- 基于结构化信息和评论生成单份直播带货话术
- 话术以 Markdown 形式在前端流式输出
- 支持导出话术和改写话术

## 技术栈

- Backend: FastAPI
- Frontend: HTML + React CDN + JavaScript
- Crawler: Playwright
- OCR: PaddleOCR
- LLM: MiniMax

## 项目结构

```text
ai-commerce-agent/
├─ backend/
│  ├─ api/
│  │  └─ routes_production.py
│  ├─ ai_engine/
│  ├─ crawler/
│  ├─ schemas/
│  ├─ services/
│  ├─ static/
│  │  ├─ css/
│  │  ├─ js/
│  │  └─ workflow_v2.html
│  ├─ config.py
│  └─ main.py
├─ tests/
│  └─ test_single_generation.py
├─ requirements.txt
└─ README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
MINIMAX_API_KEY=your-api-key-here
```

可选配置：

```env
XHS_COOKIE=
XHS_USER_AGENT=
```

### 3. 启动服务

```bash
py -3 -m backend.main
```

### 4. 打开页面

- 工作流页面: `http://localhost:8000`
- 健康检查: `http://localhost:8000/health`

## 主要流程

1. 输入商品链接，服务端解析商品信息
2. OCR 提取图片文字
3. AI 汇总并生成结构化商品信息
4. 前端展示可编辑结构化卡片
5. 用户可手动触发评论生成，也可以跳过评论
6. 服务端生成一份直播带货话术
7. 前端以 Markdown 文本流式展示话术内容

## 主要接口

### `POST /api/parse-product`

解析商品链接，返回商品基础信息、结构化数据、评论和图片列表。

请求示例：

```json
{
  "url": "https://v.douyin.com/xxxx"
}
```

### `POST /api/parse-product-stream`

流式执行商品解析、OCR、结构化提取和话术生成相关步骤。

请求示例：

```json
{
  "name": "商品名称",
  "selling_points": "商品卖点",
  "images": ["https://example.com/1.jpg"],
  "comments": ["评论1", "评论2"]
}
```

### `GET /api/generate-scripts-sse`

基于结构化信息和评论流式生成单份话术。

查询参数：

- `product_url`
- `product_name`
- `product_info`
- `selling_points`
- `structured`
- `comments`

### `POST /api/generate-script-from-comments`

非 SSE 方式生成单份话术。

### `POST /api/generate-comments`

根据商品名称和商品信息生成用户评论。

请求示例：

```json
{
  "product_name": "商品名称",
  "product_info": "商品卖点"
}
```

### `POST /api/rewrite-script`

对现有话术进行改写。

### `POST /api/export-scripts`

将话术导出为 `txt` 或 `md`。

## 当前话术生成说明

- 当前主流程使用单次生成，不再生成多种风格
- 当前主流程不再做评分和最佳结果选择
- 当前默认生成风格为 `带货型`
- 当前主流程实际使用的 prompt 为 `build_single_style_script_prompt(...)`
  位置：`backend/services/ai/prompts.py`

## 测试

当前仓库包含一组最小后端回归测试，覆盖单次生成链路。

运行方式：

```bash
py -3 -m unittest discover -s tests -p "test_*.py" -v
```

## 注意事项

- `README.md` 现已按 UTF-8 重新整理，旧版乱码内容已移除
- 若前端静态资源更新后浏览器仍显示旧行为，建议强刷页面
- OCR、Playwright、外部 LLM 依赖本地环境和可用密钥，首次运行前请先确认

## License

MIT
