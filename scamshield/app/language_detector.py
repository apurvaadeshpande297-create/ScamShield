"""
ScamShield Language Detector Module.

Detects message language across:
  - 'hi' (Devanagari Hindi script)
  - 'hi_roman' (Roman script Hinglish)
  - 'en' (English)
"""

import re
import sys

# Characteristic Hinglish (Roman Hindi) keywords & token patterns
HINGLISH_PATTERNS = [
    r"\baap(?:ka|ke|ko|ne)?\b",
    r"\bkarein?\b",
    r"\bhai[n]?\b",
    r"\bh[ae]i?\b",
    r"\bbhai\b",
    r"\bkaro\b",
    r"\bgaya\b",
    r"\bmil[ae]ga\b",
    r"\bmujhe\b",
    r"\bbhej[ao]?\b",
    r"\brupaye\b",
    r"\bpais[aa]\b",
    r"\bkhata\b",
    r"\bkhate\b",
    r"\blink pe\b",
    r"\brah[ae]i?\b",
    r"\bnahi\b",
    r"\bna\b",
    r"\bkya\b",
    r"\bpar\b",
    r"\bbina\b",
    r"\bhoga\b",
    r"\bbas\b",
    r"\bchahiye\b",
    r"\bturant\b",
    r"\bbhar[ao]\b",
    r"\bshukriya\b",
    r"\bdhanyawad\b",
    r"\bji\b",
    r"\bhun\b",
    r"\bhaiz\b",
    r"\blor\b",
    r"\byar\b",
    r"\bmah\b",
    r"\bdunno\b",
    r"\bden\b",
    r"\bwat\b",
    r"\bwen\b",
    r"\bwif\b",
]

HINGLISH_REGEX = re.compile("|".join(HINGLISH_PATTERNS), re.IGNORECASE)


def detect_language(text: str) -> str:
    """
    Identifies language of the input string.
    Returns: 'hi', 'hi_roman', or 'en'.
    """
    if not text or not isinstance(text, str):
        return "en"

    # 1. Check for Devanagari script (Hindi Unicode block: U+0900 to U+097F)
    devanagari_count = len(re.findall(r"[\u0900-\u097F]", text))
    if devanagari_count > 3:
        return "hi"

    # 2. Check for Roman Hinglish pattern matches
    matches = HINGLISH_REGEX.findall(text)
    if len(matches) >= 2 or (len(text.split()) <= 6 and len(matches) >= 1):
        return "hi_roman"

    # 3. Default to English
    return "en"


if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    test_cases = [
        ("Your SBI account statement is ready.", "en"),
        ("Aapka SBI account block ho gaya hai. KYC update karein.", "hi_roman"),
        ("आपका खाता ब्लॉक हो गया है।", "hi"),
        ("Bhai galti se refund chala gaya h", "hi_roman"),
    ]
    for text, expected in test_cases:
        res = detect_language(text)
        print(f"Text: '{text}' -> Detected: {res} (Expected: {expected})")
