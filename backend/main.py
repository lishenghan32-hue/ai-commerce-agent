"""
AI Commerce Insight Generator - FastAPI Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import os

from backend.config import settings
from backend.api import routes_products, routes_tasks, routes_test, routes_analysis, routes_production

app = FastAPI(
    title="AI Commerce Insight Generator",
    description="Generate insights, marketing scripts, and PPT from Douyin product links",
    version="1.0.0"
)

# CORS middleware - 使用配置中的允许域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_products.router, prefix="/api", tags=["products"])
app.include_router(routes_tasks.router, prefix="/api", tags=["tasks"])
app.include_router(routes_test.router, prefix="/api", tags=["test"])
app.include_router(routes_analysis.router, prefix="/api", tags=["analysis"])
app.include_router(routes_production.router, prefix="/api", tags=["production"])

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """Serve index.html"""
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "AI Commerce Insight Generator API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/workflow_v2")
async def workflow_v2():
    """Serve workflow_v2.html"""
    workflow_v2_path = os.path.join(os.path.dirname(__file__), "static", "workflow_v2.html")
    if os.path.exists(workflow_v2_path):
        return FileResponse(workflow_v2_path)
    return {"message": "Workflow V2 page not found"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
