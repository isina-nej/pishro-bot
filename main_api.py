"""Main FastAPI server for Pishro Investment Backend."""

import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# Import API routers
from app.api import users, investments, transactions
from app.database.session import init_db, close_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting API server...")
    await init_db()
    logger.info("✅ Database initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down API server...")
    await close_db()
    logger.info("✅ Database closed")


# Create FastAPI app
app = FastAPI(
    title="Pishro Investment API",
    description="RESTful API for investment management system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all exceptions globally."""
    logger.error(f"Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc)
        }
    )


# Include routers
app.include_router(users.router)
app.include_router(investments.router)
app.include_router(transactions.router)


# API info endpoint
@app.get("/api")
async def api_info():
    """API info endpoint."""
    return {
        "name": "Pishro Investment API",
        "version": "1.0.0",
        "docs": "/docs",
        "dashboard": "/",
        "API endpoints": {
            "users": "/api/v1/users",
            "investments": "/api/v1/investments",
            "transactions": "/api/v1/transactions"
        }
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Pishro API"}


# Serve static files (dashboard) - Must be after all routes
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    logger.warning(f"Static directory not found: {static_dir}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
