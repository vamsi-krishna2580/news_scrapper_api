# 🌾 Farmer News Scraper API

Hyperlocal, multilingual, categorized agricultural news for farmers — built for the Argrithm hackathon voice advisory system. Optional **Gemini** integration for a voice-ready summary in the farmer’s language.

## Quick Start

```bash
pip install -r news_scrapper_api/requirements.txt
# Optional: cp .env.example .env and add OPENWEATHER_API_KEY, GEMINI_API_KEY
uvicorn server:app --reload --port 8000
```

## Endpoints

| Endpoint | Description |
|----------|-------------|
| **GET /news** | News + weather + English `llm_summary`. |
| **GET /news/voice** | Same + Gemini `voice_summary` in farmer’s language (for TTS). |

Example:

```
GET /news?city=Ongole&crop=rice&state=Andhra Pradesh&language=te&limit=5
GET /news/voice?city=Ongole&crop=rice&language=te
```

| Param | Required | Example |
|-------|----------|---------|
| `city` | ✅ | `Ongole` |
| `crop` | ✅ | `rice` |
| `state` | ❌ | `Andhra Pradesh` |
| `language` | ❌ | `te` / `hi` / `mr` / `ta` / `kn` / `ml` / `en` |
| `limit` | ❌ | `5` (max 15) |

## Full Documentation

See **[DOCS.md](./DOCS.md)** for the complete API reference.

## Test

```bash
cd news_scrapper_api
python test_news_api.py
```
