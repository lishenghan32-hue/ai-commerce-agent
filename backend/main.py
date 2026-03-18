print("🔥 我真的被执行了")
"""
AI Commerce Insight Generator - FastAPI Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.api import routes_products, routes_tasks, routes_test, routes_analysis

app = FastAPI(
    title="AI Commerce Insight Generator",
    description="Generate insights, marketing scripts, and PPT from Douyin product links",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_products.router, prefix="/api", tags=["products"])
app.include_router(routes_tasks.router, prefix="/api", tags=["tasks"])
app.include_router(routes_test.router, prefix="/api", tags=["test"])
app.include_router(routes_analysis.router, prefix="/api", tags=["analysis"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Commerce Insight Generator API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
