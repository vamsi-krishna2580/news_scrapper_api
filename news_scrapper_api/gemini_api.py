"""
gemini_api.py — Gemini integration for voice advisory
=====================================================
Uses Google Gemini (free tier) to generate a short, natural-language
summary in the farmer's language, optimized for reading aloud over a call.
Also supports audio input: transcribe farmer speech and extract city, crop, etc.
"""

import base64
import json
import os
import re
from typing import Optional

# Load env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Language code -> full name for prompts
LANGUAGE_NAMES = {
    "en": "English",
    "te": "Telugu",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
}


def get_voice_summary(
    llm_summary: str,
    language: str = "en",
    city: str = "",
    crop: str = "",
) -> Optional[str]:
    """
    Use Gemini to produce a short, natural summary in the farmer's language,
    suitable for text-to-speech (simple sentences, clear, friendly).

    Args:
        llm_summary: Raw English summary from news_api (weather + news headlines).
        language: Farmer's language code (en, te, hi, mr, ta, kn, ml).
        city: Farmer's city (for personalization).
        crop: Farmer's crop (for personalization).

    Returns:
        Summary string in the requested language, or None if API key missing / request fails.
    """
    if not GEMINI_API_KEY:
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")  # Free tier friendly
    except Exception:
        return None

    lang_name = LANGUAGE_NAMES.get(language, "English")
    if language == "en":
        instruction = (
            "Rewrite the following farmer advisory summary in simple, clear English "
            "suitable for reading aloud over a phone call. Keep 2–4 short sentences. "
            "Friendly and direct tone."
        )
    else:
        instruction = (
            f"Translate and adapt the following farmer advisory summary into {lang_name}. "
            "Output ONLY in {lang_name} script (no English). "
            "Keep it to 2–4 short sentences, simple and clear for reading aloud over a phone call. "
            "Friendly, direct tone for a farmer."
        ).format(lang_name=lang_name)

    prompt = f"""{instruction}

Summary to adapt:
{llm_summary}

Output (plain text only, no labels or bullets):"""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=256,
                temperature=0.3,
            ),
        )
        if response and response.text:
            return response.text.strip()
    except Exception:
        pass
    return None


def extract_params_from_audio(
    audio_bytes: bytes,
    mime_type: str = "audio/mpeg",
    language_hint: str = "en",
) -> Optional[dict]:
    """
    Use Gemini to transcribe farmer audio and extract city, crop, state, language.
    Farmer might say e.g. "I am from Ongole, I grow rice, Telugu".

    Returns:
        {"city": str, "crop": str, "state": str, "language": str} or None.
    """
    if not GEMINI_API_KEY or not audio_bytes:
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        return None

    prompt = """Listen to this audio of a farmer speaking. They may mention:
- Their city or village
- The crop they grow (e.g. rice, wheat, cotton)
- Their state (e.g. Andhra Pradesh, Punjab)
- Their language (English, Telugu, Hindi, Marathi, Tamil, Kannada, Malayalam)

Extract what you can. Return ONLY a JSON object with these exact keys (use empty string if unknown):
{"city": "...", "crop": "...", "state": "...", "language": "..."}

For language, use code: en, te, hi, mr, ta, kn, ml. Infer from speech or default to "en".
For city and crop, use the exact words if possible. Be lenient with spelling."""

    try:
        # Use inline data (base64) - works for audio under ~20MB
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        audio_part = {
            "inline_data": {
                "mime_type": mime_type or "audio/mpeg",
                "data": audio_b64,
            }
        }
        response = model.generate_content(
            [prompt, audio_part],
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=256,
                temperature=0.1,
            ),
        )

        if not response or not response.text:
            return None
        text = response.text.strip()
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            # Normalize language code
            lang = (data.get("language") or "en").strip().lower()
            lang_map = {"english": "en", "telugu": "te", "hindi": "hi", "marathi": "mr",
                       "tamil": "ta", "kannada": "kn", "malayalam": "ml"}
            data["language"] = lang_map.get(lang, lang[:2] if len(lang) >= 2 else "en")
            if data["language"] not in LANGUAGE_NAMES:
                data["language"] = "en"
            return {
                "city": (data.get("city") or "").strip() or "Unknown",
                "crop": (data.get("crop") or "").strip() or "Unknown",
                "state": (data.get("state") or "").strip(),
                "language": data["language"],
            }
    except Exception:
        pass
    return None
