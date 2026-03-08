"""
web_router.py — Web UI API
==========================
Unified endpoint for form or voice input. Returns summary text + audio.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from .news_api import get_farmer_news
from .gemini_api import get_voice_summary, extract_params_from_audio
from .tts_api import text_to_mp3

router = APIRouter(prefix="/api", tags=["Web UI"])


class SubmitForm(BaseModel):
    city: str
    crop: str
    state: Optional[str] = None
    language: str = "en"
    limit: int = 5


LANGUAGE_NAMES = {
    "en": "English", "te": "Telugu", "hi": "Hindi",
    "mr": "Marathi", "ta": "Tamil", "kn": "Kannada", "ml": "Malayalam",
}


def _get_summary_and_audio(
    city: str,
    crop: str,
    state: Optional[str],
    language: str,
    limit: int = 5,
) -> dict:
    """Fetch news, build voice summary, generate audio. Returns dict with summary_text, audio_base64, query."""
    if language not in LANGUAGE_NAMES:
        language = "en"

    result = get_farmer_news(
        city=city.strip(),
        crop=crop.strip(),
        state=state.strip() if state else None,
        language=language,
        limit=limit,
    )
    llm_summary = result.get("llm_summary", "")
    voice_summary = get_voice_summary(
        llm_summary=llm_summary,
        language=language,
        city=city,
        crop=crop,
    )
    text_to_speak = (voice_summary or llm_summary or "").strip()
    if not text_to_speak:
        raise HTTPException(status_code=500, detail="No summary text available.")

    audio_bytes = text_to_mp3(text=text_to_speak, language=language)
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="TTS failed to generate audio.")

    import base64
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

    return {
        "summary_text": text_to_speak,
        "audio_base64": audio_base64,
        "query": {
            "city": city,
            "crop": crop,
            "state": state or "India (national)",
            "language": LANGUAGE_NAMES.get(language, language),
        },
    }


@router.post("/submit", summary="Submit form (JSON) — get summary text + audio")
async def submit_json(form: SubmitForm):
    """Submit city, crop, state, language as JSON. Returns summary_text + audio_base64."""
    try:
        return _get_summary_and_audio(
            city=form.city,
            crop=form.crop,
            state=form.state,
            language=form.language,
            limit=form.limit,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit/voice", summary="Submit voice file — get summary text + audio")
async def submit_voice(
    audio: UploadFile = File(..., description="Voice input (MP3/WAV) — extracts params via Gemini"),
    language: str = Form("en", description="Language hint if not detected from speech"),
    limit: int = Form(5, ge=1, le=15),
):
    """
    Upload audio of farmer speaking (city, crop, etc.). Gemini transcribes and extracts params.
    Returns: `{ summary_text, audio_base64, query }` — summary in the same language, plus MP3 as base64.
    """
    try:
        contents = await audio.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Audio file is empty.")
        mime = audio.content_type or "audio/mpeg"
        if "wav" in mime or (audio.filename and audio.filename.lower().endswith(".wav")):
            mime = "audio/wav"
        params = extract_params_from_audio(contents, mime_type=mime, language_hint=language)
        if not params:
            raise HTTPException(
                status_code=400,
                detail="Could not extract city/crop from audio. Ensure GEMINI_API_KEY is set and audio is clear.",
            )
        city = params.get("city", "")
        crop = params.get("crop", "")
        state = params.get("state")
        language = params.get("language") or language

        if not city or not crop:
            raise HTTPException(
                status_code=400,
                detail="Could not extract city and crop from audio. Please speak clearly: 'I am from [city], I grow [crop]'.",
            )

        return _get_summary_and_audio(city, crop, state, language, limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
