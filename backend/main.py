from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from database import engine, Base
from routers import rfps, vendors, proposals, email

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="RFP Management System",
    description="AI-powered RFP management for procurement managers",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rfps.router, prefix="/api/rfps", tags=["RFPs"])
app.include_router(vendors.router, prefix="/api/vendors", tags=["Vendors"])
app.include_router(proposals.router, prefix="/api/proposals", tags=["Proposals"])
app.include_router(email.router, prefix="/api/email", tags=["Email"])

@app.get("/")
async def root():
    return {"message": "RFP Management System API"}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
