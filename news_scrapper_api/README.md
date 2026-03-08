# 🌾 Farmer News Scraper API

Hyperlocal, multilingual, categorized agricultural news for farmers — built for the Argrithm hackathon voice advisory system.

## Quick Start

```bash
pip install -r news_scrapper_api/requirements.txt
uvicorn server:app --reload --port 8000
```

## Endpoint

```
GET /news?city=Ongole&crop=rice&state=Andhra Pradesh&language=te&limit=5
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
