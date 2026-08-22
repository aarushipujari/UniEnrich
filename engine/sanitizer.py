"""
UniEnrich Sanitization & Hygiene Module
Cleans placeholders, repairs quotes, normalizes whitespace and raw abbreviation tokens.
"""
import re

PLACEHOLDERS = {
    "-- unbranded --", "-- no unilog brand --", "-- no dib brand --",
    "commodity - unbranded", "-", "null", "none", "nan", "unbranded", "-- none --"
}

def clean_placeholder(val: str) -> str:
    """Returns empty string if val is a placeholder or null, else cleaned string."""
    if val is None:
        return ""
    s = str(val).strip()
    if s.lower() in PLACEHOLDERS:
        return ""
    return s

def sanitize_text(text: str) -> str:
    """Normalizes quotes, unescapes, and cleans irregular spacing."""
    if not text:
        return ""
    s = str(text).strip()
    # Replace escaped quotes
    s = s.replace('""', '"')
    # Replace double spaces
    s = re.sub(r'\s+', ' ', s)
    # Fix spacing before/after hyphens if isolated
    s = re.sub(r'\s*-\s*Display\s*(Only)?', ' - Display Only', s, flags=re.IGNORECASE)
    return s.strip()

def strip_trailing_distributor_codes(text: str) -> str:
    """Removes trailing distributor supplier codes like (4031), (2435), (JAMIN)."""
    if not text:
        return ""
    s = re.sub(r'\s*\([A-Z0-9_-]+\)\s*$', '', text.strip())
    return s.strip()
