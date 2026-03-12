from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import uvicorn
import os

from routers import auth, chat, crisis
from database import init_firebase

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase()
    yield

app = FastAPI(
    title="MindEase API",
    description="AI-Driven Mental Wellness Platform for Indian Youth",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router,   prefix="/api/auth",   tags=["Authentication"])
app.include_router(chat.router,   prefix="/api/chat",   tags=["Chat"])
app.include_router(crisis.router, prefix="/api/crisis", tags=["Crisis"])

# Serve frontend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))

app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse(os.path.join(frontend_path, "templates", "index.html"))

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "MindEase"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
