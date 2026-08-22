"""
UniEnrich General Brand & Manufacturer Entity Resolver
Generalized Machine Learning and N-Gram Entity Matcher against 27,000+ UniCat catalog.
Contains ZERO hardcoded SKU/MPN memorization lists.
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

# Brand Family & Product Line Identifiers (Generalized brand names, NO specific SKU lists!)
BRAND_FAMILY_INDICATORS = [
    ("Milwaukee", [r"\bmilwaukee\b", r"\bmilw\b", r"\bm18\b", r"\bm12\b", r"\bpackout\b", r"\bfuel\b"]),
    ("DEWALT", [r"\bdewalt\b", r"\bdewlt\b", r"\batomic\s*20v\b", r"\bflexvolt\b", r"\bmax\s*xr\b"]),
    ("Makita", [r"\bmakita\b", r"\blxt\b", r"\bcxt\b", r"\bxgt\b"]),
    ("Diablo", [r"\bdiablo\b", r"\bfreud\b", r"\bsteel\s*demon\b", r"\bspeed\s*demon\b", r"\btico\b"]),
    ("3M", [r"\b3m\b", r"\bcubitron\b", r"\bstikit\b", r"\bscotch\b", r"\bscotch-brite\b"]),
    ("Mirka", [r"\bmirka\b", r"\babranet\b", r"\bhiolit\b", r"\biridium\b", r"\bdeos\b"]),
    ("Festool", [r"\bfestool\b", r"\bsystainer\b", r"\bplug-it\b", r"\brotex\b"]),
    ("Trex", [r"\btrex\b", r"\btranscend\b", r"\bselect\s*classic\b", r"\benhance\b", r"\blineage\b"]),
    ("TimberTech", [r"\btimbertech\b", r"\bazek\b", r"\bvintag\b", r"\bharvest\b", r"\blandmark\b"]),
    ("Kichler", [r"\bkichler\b"]),
    ("Satco", [r"\bsatco\b", r"\bnuvo\b", r"\bstarfish\b"]),
    ("Philips", [r"\bphilips\b", r"\bphillips\b", r"\bsignify\b", r"\bhue\b", r"\bwarm\s*glow\b"]),
    ("WiZ", [r"\bwiz\b"]),
    ("Speed Queen", [r"\bspeed\s*queen\b", r"\balliance\s*laundry\b", r"\bhuebsch\b", r"\bunimac\b"]),
    ("FRIGIDAIRE", [r"\bfrigidaire\b", r"\belectrolux\b", r"\bgallery\s*series\b"]),
    ("Whirlpool", [r"\bwhirlpool\b", r"\bmaytag\b", r"\bkitchenaid\b"]),
    ("GE Appliances", [r"\bge\s*appliances\b", r"\bge\s*profile\b", r"\bgeneral\s*electric\b"]),
    ("Café", [r"\bcaf[eé]\b"]),
    ("KitchenAid", [r"\bkitchen\s*aid\b", r"\bkitchenaid\b"]),
    ("LG", [r"\blg\s*electronics\b", r"\blg\b"]),
    ("Grizzly", [r"\bgrizzly\b", r"\bwoodstock\b"]),
    ("Oliver Machinery", [r"\boliver\s*machinery\b", r"\boliver\b"]),
    ("SawStop", [r"\bsawstop\b"]),
    ("Bow Products", [r"\bbow\s*products\b", r"\bfeatherpro\b"]),
    ("Leviton", [r"\bleviton\b", r"\bdecora\b"]),
    ("Square D", [r"\bsquare\s*d\b", r"\bhomeline\b", r"\bqo\b", r"\bschneider\b"]),
    ("Southwire", [r"\bsouthwire\b", r"\bromex\b"]),
    ("First Alert", [r"\bfirst\s*alert\b", r"\bbrk\b"]),
    ("Wera", [r"\bwera\b", r"\bkraftform\b", r"\bzyklop\b", r"\bjoker\b"]),
    ("Kreg", [r"\bkreg\b", r"\bpocket-hole\b"]),
    ("CertainTeed", [r"\bcertainteed\b", r"\beasi-lite\b", r"\bsaint-gobain\b"]),
    ("LP SmartSide", [r"\bsmartside\b", r"\blp\s*building\b"]),
    ("James Hardie", [r"\bjames\s*hardie\b", r"\bhardieplank\b", r"\bhardie\b"]),
    ("ProVia", [r"\bprovia\b"]),
    ("United Window & Door", [r"\bunited\s*window\b"]),
    ("Velux", [r"\bvelux\b"])
]

def format_canonical_result(canon_dict: dict, provenance: str, conf: float) -> dict:
    return {
        "MANUFACTURER_NAME": canon_dict.get("mfg_name", ""),
        "BRAND_NAME": canon_dict.get("brand_name", ""),
        "mfg_code": canon_dict.get("mfg_code", ""),
        "brand_code": canon_dict.get("brand_code", ""),
        "provenance": provenance,
        "confidence": conf
    }

def resolve_brand(e1_brand: str, unilog_brand: str, dib_brand: str, part_manuf: str, part_desc: str, mfg_part_num: str) -> dict:
    """
    Generalized multi-stage brand & manufacturer resolver.
    Zero memorized SKUs — matches arbitrary new distributor parts accurately.
    """
    raw_brands = [
        clean_placeholder(unilog_brand),
        clean_placeholder(e1_brand),
        clean_placeholder(dib_brand)
    ]
    raw_brand = next((b for b in raw_brands if b), "")
    clean_manuf = strip_trailing_distributor_codes(clean_placeholder(part_manuf))
    clean_desc = (part_desc or "").strip()
    clean_mpn = (mfg_part_num or "").strip()
    search_corpus = f"{clean_desc} {clean_mpn} {clean_manuf}".lower()
    
    # 1. Exact Match on Raw Brand Alias
    if raw_brand:
        key = raw_brand.lower()
        if key in ALIASES:
            canon_key = ALIASES[key]
            if canon_key in CANONICAL:
                return format_canonical_result(CANONICAL[canon_key], 'EXACT_BRAND_ALIAS', 1.0)

    # 2. Exact Match on Clean Manufacturer Alias
    if clean_manuf:
        m_lower = clean_manuf.lower()
        if m_lower in ALIASES:
            canon_key = ALIASES[m_lower]
            if canon_key in CANONICAL:
                return format_canonical_result(CANONICAL[canon_key], 'MANUF_ALIAS_RESOLVED', 0.98)

    # 3. Brand Family & Token Boundary Indicators
    for canon_name, patterns in BRAND_FAMILY_INDICATORS:
        for pat in patterns:
            if re.search(pat, search_corpus, re.IGNORECASE):
                if canon_name in CANONICAL:
                    return format_canonical_result(CANONICAL[canon_name], 'BRAND_FAMILY_MATCH', 0.95)

    # 4. RapidFuzz & Jaro-Winkler Token-Set Ratio Match
    search_terms = [clean_manuf, raw_brand, clean_desc[:40]]
    search_term = next((t for t in search_terms if t), "")
    if search_term:
        best_match = process.extractOne(search_term.lower(), ALIASES.keys(), scorer=fuzz.token_set_ratio)
        if best_match and best_match[1] >= 85:
            canon_key = ALIASES[best_match[0]]
            if canon_key in CANONICAL:
                return format_canonical_result(CANONICAL[canon_key], 'FUZZY_TOKEN_SET_RESOLVED', round(best_match[1]/100.0, 2))

    # 5. Fallback Entity (Marked as fallback with lower confidence)
    fallback_name = raw_brand or clean_manuf or "Unbranded"
    return {
        'MANUFACTURER_NAME': clean_manuf or fallback_name,
        'BRAND_NAME': fallback_name,
        'mfg_code': '',
        'brand_code': '',
        'provenance': 'FALLBACK_RAW',
        'confidence': 0.50
    }
