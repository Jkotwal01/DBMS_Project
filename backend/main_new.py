# main_new.py - Refactored main application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from config.settings import settings

# Import routers
from api.routes import auth, student, faculty, subjects

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Scalable ERP System with Role-Based Access Control",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(faculty.router)
app.include_router(subjects.router)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ERP System API",
        "version": "2.0.0",
        "docs": "/api/docs",
        "status": "active"
    }

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ERP System",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_new:app", host="0.0.0.0", port=8000, reload=True)
