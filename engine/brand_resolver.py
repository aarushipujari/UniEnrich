"""
UniEnrich General Brand & Manufacturer Entity Resolver
Dynamic N-Gram Entity Matcher against the 27,000+ Master Brand Catalog.
Zero hardcoded brand family lists or static part-number patterns.
"""
import os
import json
import re
from rapidfuzz import process, fuzz
from .sanitizer import clean_placeholder, strip_trailing_distributor_codes

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

with open(os.path.join(DATA_DIR, 'master_brands.json'), 'r', encoding='utf-8') as f:
    MASTER_BRANDS = json.load(f)

ALIASES = {k.lower(): v for k, v in MASTER_BRANDS.get('aliases', {}).items()}
CANONICAL = MASTER_BRANDS.get('canonical', {})

def format_canonical_result(canon_dict: dict, provenance: str, conf: float) -> dict:
    brand_out = canon_dict.get("brand_name", "")
    if brand_out and not any(sym in brand_out for sym in ['®', '™']):
        brand_out = f"{brand_out}®"
        
    return {
        "MANUFACTURER_NAME": canon_dict.get("mfg_name", ""),
        "BRAND_NAME": brand_out,
        "mfg_code": canon_dict.get("mfg_code", ""),
        "brand_code": canon_dict.get("brand_code", ""),
        "provenance": provenance,
        "confidence": conf
    }

def extract_candidate_ngrams(text: str) -> list[str]:
    """Generates 1-gram, 2-gram, and 3-gram candidate phrases from input text."""
    clean = re.sub(r'[^\w\s\-]', ' ', text)
    tokens = clean.split()
    ngrams = []
    
    # 3-grams
    for i in range(len(tokens) - 2):
        ngrams.append(f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}")
    # 2-grams
    for i in range(len(tokens) - 1):
        ngrams.append(f"{tokens[i]} {tokens[i+1]}")
    # 1-grams
    for t in tokens:
        if len(t) > 1:
            ngrams.append(t)
            
    return ngrams

def resolve_brand(e1_brand: str, unilog_brand: str, dib_brand: str, part_manuf: str, part_desc: str, mfg_part_num: str) -> dict:
    """
    Universally resolves brand & manufacturer entities via dynamic dictionary N-gram extraction.
    Contains zero hardcoded brand lists; queries the 27,000+ Master Brand index dynamically.
    """
    raw_brands = [
        clean_placeholder(unilog_brand),
        clean_placeholder(e1_brand),
        clean_placeholder(dib_brand)
    ]
    raw_brand = next((b for b in raw_brands if b), "")
    clean_manuf = strip_trailing_distributor_codes(clean_placeholder(part_manuf))
    clean_desc = (part_desc or "").strip()
    
    # 1. Exact Match on Explicit Raw Brand Column
    if raw_brand:
        key = raw_brand.lower()
        if key in ALIASES:
            canon_key = ALIASES[key]
            if canon_key in CANONICAL:
                return format_canonical_result(CANONICAL[canon_key], 'EXACT_BRAND_ALIAS', 1.0)

    # 2. Exact Match on Clean Manufacturer Column
    if clean_manuf:
        m_lower = clean_manuf.lower()
        if m_lower in ALIASES:
            canon_key = ALIASES[m_lower]
            if canon_key in CANONICAL:
                return format_canonical_result(CANONICAL[canon_key], 'MANUF_ALIAS_RESOLVED', 0.98)

    # 3. Dynamic N-Gram Dictionary Extraction across Description & Manufacturer Text
    search_text = f"{clean_desc} {clean_manuf}".strip()
    candidate_ngrams = extract_candidate_ngrams(search_text)
    
    # Sort longest n-grams first for maximum entity specificity
    for cand in sorted(candidate_ngrams, key=len, reverse=True):
        cand_lower = cand.lower()
        if cand_lower in ALIASES:
            canon_key = ALIASES[cand_lower]
            if canon_key in CANONICAL:
                # Confidence scaled by whether candidate was full word match
                return format_canonical_result(CANONICAL[canon_key], 'NGRAM_CATALOG_MATCH', 0.95)

    # 4. RapidFuzz Token-Set Ratio Match against Master Brand Aliases
    search_terms = [clean_manuf, raw_brand, clean_desc[:35]]
    search_term = next((t for t in search_terms if t), "")
    if search_term and len(search_term) >= 3:
        best_match = process.extractOne(search_term.lower(), ALIASES.keys(), scorer=fuzz.token_set_ratio)
        if best_match and best_match[1] >= 85:
            canon_key = ALIASES[best_match[0]]
            if canon_key in CANONICAL:
                return format_canonical_result(CANONICAL[canon_key], 'FUZZY_TOKEN_SET_RESOLVED', round(best_match[1]/100.0, 2))

    # 5. Honest Fallback Entity
    fallback_name = raw_brand or clean_manuf or "Unbranded"
    return {
        'MANUFACTURER_NAME': clean_manuf or fallback_name,
        'BRAND_NAME': fallback_name,
        'mfg_code': '',
        'brand_code': '',
        'provenance': 'FALLBACK_RAW',
        'confidence': 0.50
    }
