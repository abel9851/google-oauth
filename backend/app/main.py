from app.auth.jwt import get_current_user
from app.auth.oauth import router as oauth_router
from app.config import settings
from app.db.database import Base, engine
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Google OAuth 2.0 and OpenID Connect implementation",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(oauth_router)


@app.get("/")
def read_root():
    """Root endpoint that returns basic API information"""
    return {
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "description": "Google OAuth 2.0 and OpenID Connect implementation",
    }


@app.get("/api/me")
async def get_my_info(current_user=Depends(get_current_user)):
    """Get current user information (requires authentication)"""
    return current_user


# For demonstration only - protected endpoint
@app.get("/api/protected")
async def protected_route(current_user=Depends(get_current_user)):
    """Protected route that requires authentication"""
    return {"message": "This is a protected endpoint", "user": current_user}


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
