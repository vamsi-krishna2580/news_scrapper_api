"""
tts_api.py — Text-to-speech for voice summary
==============================================
Converts summary text to MP3 audio using gTTS (free, supports Indian languages).
"""

import io
from typing import Optional

# gTTS language codes match our codes: en, te, hi, mr, ta, kn, ml
GTTS_LANG_MAP = {
    "en": "en",
    "te": "te",
    "hi": "hi",
    "mr": "mr",
    "ta": "ta",
    "kn": "kn",
    "ml": "ml",
}


def text_to_mp3(text: str, language: str = "en") -> Optional[bytes]:
    """
    Convert text to MP3 audio bytes using Google TTS (gTTS).

    Args:
        text: Text to speak (voice_summary or llm_summary).
        language: Language code (en, te, hi, mr, ta, kn, ml).

    Returns:
        MP3 file bytes, or None if TTS fails.
    """
    if not text or not text.strip():
        return None
    lang = GTTS_LANG_MAP.get(language, "en")
    try:
        from gtts import gTTS
        buf = io.BytesIO()
        tts = gTTS(text=text.strip(), lang=lang, slow=False)
        tts.write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        return None
