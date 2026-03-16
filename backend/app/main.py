"""
Main FastAPI application for Wadiz Page Builder
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.projects import router as projects_router
from app.api.endpoints.images import router as images_router
from app.api.endpoints.templates import router as templates_router
from app.api.endpoints.export import router as export_router
from app.api.endpoints.page_renewal import router as page_renewal_router

# ai_generate 파일이 있다면 아래 주석 해제
# from app.api.endpoints.ai_generate import router as ai_generate_router

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Wadiz Page Builder API",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


# Include routers
app.include_router(
    auth_router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"]
)

app.include_router(
    projects_router,
    prefix=f"{settings.API_V1_PREFIX}/projects",
    tags=["Projects"]
)

app.include_router(
    images_router,
    prefix=f"{settings.API_V1_PREFIX}/images",
    tags=["Images"]
)

# ai_generate 파일이 있다면 아래 주석 해제
# app.include_router(
#     ai_generate_router,
#     prefix=f"{settings.API_V1_PREFIX}/ai",
#     tags=["AI Generation"]
# )

app.include_router(
    templates_router,
    prefix=f"{settings.API_V1_PREFIX}/templates",
    tags=["Templates"]
)

app.include_router(
    export_router,
    prefix=f"{settings.API_V1_PREFIX}/export",
    tags=["Export"]
)

app.include_router(
    page_renewal_router,
    prefix=f"{settings.API_V1_PREFIX}/renewal",
    tags=["Page Renewal"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
