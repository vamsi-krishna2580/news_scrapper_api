"""
Voice_app — Farmer Advisory API Server
=======================================
FastAPI app that serves the news scraper and Gemini voice endpoints.
Run: uvicorn server:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from news_scrapper_api.news_router import router as news_router

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


@app.get("/")
def root():
    return {
        "app": "Farmer Voice Advisory API",
        "docs": "/docs",
        "news": "GET /news?city=...&crop=...&state=...&language=...",
        "voice_summary": "GET /news/voice?city=...&crop=...&language=... (Gemini)",
    }
