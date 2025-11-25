from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.logging import setup_logging
from src.api.routes import router

# Setup logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Hybrid RAG API for SportSee Basketball Analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME}
