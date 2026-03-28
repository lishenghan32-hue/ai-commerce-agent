"""
AI Commerce Insight Generator - FastAPI Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import os

from backend.config import settings
from backend.api import routes_production

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
app.include_router(routes_production.router, prefix="/api", tags=["production"])

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """Redirect to workflow_v2"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    workflow_v2_path = os.path.join(static_dir, "workflow_v2.html")
    if os.path.exists(workflow_v2_path):
        return FileResponse(workflow_v2_path)
    return {"message": "AI Commerce Insight Generator API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
