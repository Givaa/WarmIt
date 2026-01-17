"""Main FastAPI application.

Developed with ❤️ by Giovanni Rapa
https://github.com/giovannirapa
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from warmit.api import accounts, campaigns, metrics, test, tracking
from warmit.database import init_db, get_session
from warmit.config import settings
from warmit.services.health_monitor import HealthMonitor
from warmit.middleware.rate_limit import RateLimitMiddleware
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting WarmIt application...")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    yield

    logger.info("Shutting down WarmIt application...")


# Create FastAPI app
app = FastAPI(
    title="WarmIt",
    description="AI-powered email warming tool to improve deliverability",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
# SECURITY: Only allow requests from the dashboard (same origin via Nginx)
# In production, Nginx handles all external requests and proxies internally
# This restricts direct API access to internal Docker network only
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:8501",  # Dashboard dev
    "http://dashboard:8501",  # Docker internal
    "http://nginx",           # Docker internal via Nginx
    "http://nginx:80",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Add rate limiting middleware
# SECURITY: Protects against brute-force and API abuse
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(test.router, prefix="/api/test", tags=["test"])
app.include_router(tracking.router, tags=["tracking"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "WarmIt",
        "version": "0.1.0",
        "description": "AI-powered email warming tool",
    }


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy"}


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all system components."""
    report = await HealthMonitor.get_full_health_report()
    return report


@app.post("/health/recover")
async def trigger_recovery():
    """Manually trigger auto-recovery process."""
    result = await HealthMonitor.auto_recover()
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "warmit.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
