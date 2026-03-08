"""
Voice_app — Farmer Advisory API Server
=======================================
FastAPI app that serves the web UI, news scraper, and Gemini voice endpoints.
Run: uvicorn server:app --reload --port 8000
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from news_scrapper_api.news_router import router as news_router
from news_scrapper_api.web_router import router as web_router

app = FastAPI(
    title="Farmer Voice Advisory API",
    description="Hyperlocal agri news + weather + Gemini voice summary for toll-free farmer calls",
    version="2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news_router)
app.include_router(web_router)

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/")
def index():
    """Serve the web UI."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api")
def api_info():
    """API info for programmatic access."""
    return {
        "app": "Farmer Voice Advisory API",
        "docs": "/docs",
        "submit": "POST /api/submit (JSON: city, crop, state?, language?)",
        "submit_voice": "POST /api/submit/voice (multipart: audio file)",
        "news": "GET /news?city=...&crop=...&state=...&language=...",
        "voice_audio": "GET /news/voice/audio?city=...&crop=...&language=... (MP3)",
    }
