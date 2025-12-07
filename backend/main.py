# ------------------------------------------------------
# This is the main FastAPI application entry point.
# It initializes the API, creates database tables,
# configures CORS, and mounts all routers.
# ------------------------------------------------------

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from database import engine, Base
from routers import rfps, vendors, proposals, email


# ------------------------------------------------------
# Application Lifespan — run logic before/after app starts
# ------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all database tables automatically at startup
    Base.metadata.create_all(bind=engine)
    yield  # Continue running the application


# ------------------------------------------------------
# Initialize FastAPI application
# ------------------------------------------------------
app = FastAPI(
    title="RFP Management System",
    description="AI-powered RFP management for procurement managers",
    version="1.0.0",
    lifespan=lifespan
)


# ------------------------------------------------------
# CORS Configuration — allows frontend to access backend
# ------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all origins (frontend)
    allow_credentials=True,
    allow_methods=["*"],       # Allow all HTTP methods
    allow_headers=["*"],       # Allow all custom headers
)


# ------------------------------------------------------
# Register API Routers for different modules
# ------------------------------------------------------
app.include_router(rfps.router, prefix="/api/rfps", tags=["RFPs"])
app.include_router(vendors.router, prefix="/api/vendors", tags=["Vendors"])
app.include_router(proposals.router, prefix="/api/proposals", tags=["Proposals"])
app.include_router(email.router, prefix="/api/email", tags=["Email"])


# ------------------------------------------------------
# Basic Routes
# ------------------------------------------------------
@app.get("/")
async def root():
    """Root endpoint to verify API is running."""
    return {"message": "RFP Management System API"}

@app.get("/api/health")
async def health():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


# ------------------------------------------------------
# Run the server (only when executed directly)
# ------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload during development
    )
