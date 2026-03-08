"""
gemini_api.py — Gemini integration for voice advisory
=====================================================
Uses Google Gemini (free tier) to generate a short, natural-language
summary in the farmer's language, optimized for reading aloud over a call.
"""

import os
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
