"""
Language configuration for the Multilingual Voice Translator.
Contains language codes, names, and supported translation pairs.
"""

# Supported languages with their codes and display names
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "ar": "Arabic",
    "pt": "Portuguese",
    "ru": "Russian",
}

# Language names for display
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "हिन्दी (Hindi)",
    "es": "Español (Spanish)",
    "fr": "Français (French)",
    "de": "Deutsch (German)",
    "zh": "中文 (Chinese)",
    "ja": "日本語 (Japanese)",
    "ar": "العربية (Arabic)",
    "pt": "Português (Portuguese)",
    "ru": "Русский (Russian)",
}

# gTTS language codes (some differ from standard ISO codes)
GTTS_LANGUAGE_CODES = {
    "en": "en",
    "hi": "hi",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "zh": "zh-CN",  # Simplified Chinese
    "ja": "ja",
    "ar": "ar",
    "pt": "pt",
    "ru": "ru",
}

def get_language_name(code: str) -> str:
    """Get display name for a language code."""
    return LANGUAGE_NAMES.get(code, code.upper())

def get_gtts_code(code: str) -> str:
    """Get gTTS-compatible language code."""
    return GTTS_LANGUAGE_CODES.get(code, code)

def is_language_supported(code: str) -> bool:
    """Check if a language code is supported."""
    return code in SUPPORTED_LANGUAGES

def get_supported_languages() -> dict:
    """Return all supported languages."""
    return SUPPORTED_LANGUAGES.copy()

def get_language_options_for_dropdown() -> list:
    """Return list of tuples for Streamlit dropdown."""
    return [(code, get_language_name(code)) for code in SUPPORTED_LANGUAGES.keys()]
