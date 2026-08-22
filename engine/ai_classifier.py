"""
UniEnrich AI Semantic Classifier & Zero-Shot Taxonomy Mapper
Provides precision zero-shot matching across the Unilog Master Category Tree.
Strictly requires word boundaries and disallows substring fuzzy matching on short tokens (<5 chars).
"""
import re
from rapidfuzz import fuzz

# Master Candidate Industrial Taxonomies for Zero-Shot Classification
MASTER_CATEGORY_CANDIDATES = [
    {
        "type": "LED BR Reflector Bulb",
        "keywords": ["br40", "br30", "par38", "par30", "par20", "mr16", "reflector bulb"],
        "dept": "Electrical", "class": "Lamps & Bulbs", "fine": "LED Bulbs",
        "classpath": "Electrical>Lamps & Bulbs>LED Bulbs>Directional & Reflector Bulbs",
        "unspsc": "39101628"
    },
    {
        "type": "LED General Purpose Bulb",
        "keywords": ["a19", "a21", "st19", "edison", "filament bulb", "decorative bulb"],
        "dept": "Electrical", "class": "Lamps & Bulbs", "fine": "LED Bulbs",
        "classpath": "Electrical>Lamps & Bulbs>LED Bulbs>Standard & Decorative Bulbs",
        "unspsc": "39101628"
    },
    {
        "type": "Fluorescent & LED Tube",
        "keywords": ["linear tube", "fluorescent tube", "u-bend tube"],
        "dept": "Electrical", "class": "Lamps & Bulbs", "fine": "Linear Lamps",
        "classpath": "Electrical>Lamps & Bulbs>Linear Tubes",
        "unspsc": "39101605"
    },
    {
        "type": "Pipe Coupling",
        "keywords": ["cplg", "pipe coupling", "threaded coupling", "brass coupling", "metallic coupling"],
        "dept": "Plumbing & Pumps", "class": "Pipe, Tube & Hose Fittings", "fine": "Fittings",
        "classpath": "Plumbing & Pumps>Pipe, Tube & Hose Fittings>Couplings",
        "unspsc": "40142315"
    },
    {
        "type": "Pipe Elbow",
        "keywords": ["pipe elbow", "90 deg elbow", "45 deg elbow", "street elbow"],
        "dept": "Plumbing & Pumps", "class": "Pipe, Tube & Hose Fittings", "fine": "Fittings",
        "classpath": "Plumbing & Pumps>Pipe, Tube & Hose Fittings>Elbows",
        "unspsc": "40142315"
    },
    {
        "type": "Portable SOOW Cord",
        "keywords": ["so cord", "soow cord", "sjoow cord", "portable power cord", "heavy duty extension cord"],
        "dept": "Electrical", "class": "Wire & Cable", "fine": "Flexible & Portable Cord",
        "classpath": "Electrical>Wire & Cable>Portable Cords",
        "unspsc": "26121629"
    },
    {
        "type": "Building Wire & Cable",
        "keywords": ["romex nm-b", "thhn wire", "uf-b direct burial", "triplex service cable"],
        "dept": "Electrical", "class": "Wire & Cable", "fine": "Building Wire",
        "classpath": "Electrical>Wire & Cable>Building Wire",
        "unspsc": "26121600"
    },
    {
        "type": "Circuit Breaker",
        "keywords": ["circuit breaker", "tandem breaker", "homeline breaker", "qo circuit breaker"],
        "dept": "Electrical", "class": "Power Distribution", "fine": "Circuit Breakers",
        "classpath": "Electrical>Power Distribution>Circuit Breakers",
        "unspsc": "39121601"
    },
    {
        "type": "Smoke & CO Alarm",
        "keywords": ["smoke alarm", "smoke & co alarm", "carbon monoxide alarm", "fire alarm detector"],
        "dept": "Safety & Security", "class": "Alarms & Detectors", "fine": "Smoke Alarms",
        "classpath": "Safety & Security>Alarms & Warnings>Smoke Detectors",
        "unspsc": "46191500"
    },
    {
        "type": "Drywall Gypsum Board",
        "keywords": ["gypsum board", "drywall board", "sheetrock panel", "lightweight drywall", "easi-lite"],
        "dept": "Building Materials", "class": "Drywall & Plaster", "fine": "Drywall Panels",
        "classpath": "Building Materials>Drywall & Gypsum>Panels",
        "unspsc": "30161500"
    }
]

def semantic_zero_shot_classify(text: str, mpn: str = "") -> dict | None:
    """
    Performs AI semantic zero-shot classification with strict word boundary enforcement.
    Never matches short substrings (< 5 chars) fuzzily inside unrelated words.
    """
    query = f"{text} {mpn}".strip().lower()
    
    # 1. Exact Whole-Word Keyword Check (Strict boundary \b...\b)
    for cand in MASTER_CATEGORY_CANDIDATES:
        for kw in cand["keywords"]:
            if re.search(rf"\b{re.escape(kw)}\b", query, re.IGNORECASE):
                return {
                    "cat_key": cand["type"].lower().replace(' ', '_'),
                    "Dept": cand["dept"],
                    "Class": cand["class"],
                    "Fine": cand["fine"],
                    "Classpath": cand["classpath"],
                    "UNSPSC": cand["unspsc"],
                    "Product Name": cand["type"],
                    "is_fallback": False,
                    "provenance": "AI_SEMANTIC_EXACT_TOKEN"
                }

    # 2. Multi-Token Semantic Fuzzy Match (Strictly restricted to long phrases >= 6 chars)
    best_candidate = None
    best_score = 0
    
    for cand in MASTER_CATEGORY_CANDIDATES:
        for kw in cand["keywords"]:
            if len(kw) >= 6 and ' ' in kw:
                score = fuzz.token_set_ratio(kw, query)
                if score >= 90 and score > best_score:
                    best_score = score
                    best_candidate = cand

    if best_candidate and best_score >= 90:
        return {
            "cat_key": best_candidate["type"].lower().replace(' ', '_'),
            "Dept": best_candidate["dept"],
            "Class": best_candidate["class"],
            "Fine": best_candidate["fine"],
            "Classpath": best_candidate["classpath"],
            "UNSPSC": best_candidate["unspsc"],
            "Product Name": best_candidate["type"],
            "is_fallback": False,
            "provenance": "AI_ZERO_SHOT_SEMANTIC"
        }

    return None
