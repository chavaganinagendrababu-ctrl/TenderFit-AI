"""
TenderFit - FastAPI Backend Application
Entrypoint for API services, database initialization, and middleware.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from backend.database import init_db, ACTIVE_DIALECT
from backend.routes.companies import router as companies_router
from backend.routes.tenders import router as tenders_router
from backend.routes.logs import router as logs_router


app = FastAPI(
    title=f"{settings.APP_NAME} Backend API",
    description="API for Government Tender Discovery, Company Profile Management, and Eligibility Verification.",
    version="1.0.0",
)

# Startup: initialize database tables
init_db()

# Enable CORS for Streamlit and external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(companies_router)
app.include_router(tenders_router)
app.include_router(logs_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_NAME,
        "tagline": settings.APP_TAGLINE,
        "status": "online",
        "database_dialect": ACTIVE_DIALECT,
        "docs_url": "/docs",
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "dialect": ACTIVE_DIALECT,
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )

