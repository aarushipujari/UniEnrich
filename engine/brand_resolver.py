"""
UniEnrich Canonical Brand & Manufacturer Resolver
Precision token-boundary and regex-based entity matcher against UniCat reference data.
Strips false-positive substring triggers and enforces trademark legal casing (®, ™).
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

# Strict regex patterns for brand identification (word boundaries and exact prefixes ONLY)
STRICT_BRAND_PATTERNS = [
    ("Milwaukee", [r"\bmilw\b", r"\bmilwaukee\b", r"^4[89]-\d{2}-\d{4}", r"^(?:25|27|28|29|30|32|34)\d{2}-\d{2}", r"^0887-20"]),
    ("DEWALT", [r"\bdewalt\b", r"\bdewlt\b", r"^dc[bcdfglmnstvw]\d+", r"^dw[a-z0-9]+", r"^dzn\d+"]),
    ("Makita", [r"\bmakita\b", r"^x[nrlbvps][a-z0-9]+", r"^bl18\d+", r"^191v\d+", r"^gsl02", r"^a-96095"]),
    ("Diablo", [r"\bdiablo\b", r"\bfreud\b", r"^dcb\d+", r"^dbd\d+", r"^dph\d+", r"^dsq\d+", r"^dt[0-9]+", r"^ddwssb", r"^d0\d{3}", r"^d1\d{3}", r"^djt\d+", r"^dfbl", r"^dsa\d+"]),
    ("3M", [r"\b3m\b", r"^3mabr-", r"\bstikit\b", r"\bcubitron\b", r"\bscotch\b"]),
    ("Mirka", [r"\bmirka\b", r"\bhiolit\b", r"\babranet\b", r"\biridium\b", r"\bdeos\b", r"^5b-\d+", r"^9a-\d+", r"^24-35m", r"^mid663"]),
    ("Festool", [r"\bfestool\b", r"\betsc\b", r"\bsystainer\b", r"^57[78]\d{3}"]),
    ("Trex", [r"\btrex\b", r"^543\d{6}", r"^15137\d{2}", r"^15168[789]\d", r"^15169\d{2}"]),
    ("TimberTech", [r"\btimbertech\b", r"\bazek\b", r"^adb\d+", r"^agb\d+", r"^adcb\d+", r"^adr\d+", r"^adcr\d+", r"^150839[56]"]),
    ("Kichler", [r"\bkichler\b", r"^(?:45297|45573|37418|45496|45973|55155|55157|55184|55185|55186|55210|55211|55212|55226|55239|44072|44073|52033|84322|52404|34686|34687|34688|43671|52616|52678|52680|52772|82399|42955|42275|42296|43913|52476|42199|42200|43851|43852|43853|43905|43911|52529|52662|52734|82400|43849|59061|59062|59124|59025)"]),
    ("Satco", [r"\bsatco\b", r"\bnuvo\b", r"\bstarfish\b", r"^6[245]-\d+", r"^s11\d+", r"^s21\d+", r"^s35\d+", r"^s34\d+", r"^s37\d+", r"^s47\d+"]),
    ("Philips", [r"\bphilips\b", r"\bphillips\b", r"^(?:141465|391227|392225|467316|567313|586875|576355|576363|565374|565390|576371|576496|564856|565796|576389|564492|586909|566364|571497|576306|588533|576520|574004|574012|573971|573989|576769|567446|573997|571463|576512|581181|566430|568337|565788|565770|573436|576538|573451|586883|586859|576488|575217|586479|571471|570762|533352|573519|573378|565622|586891|585448|573444|566687|564385|566661|564898|538319|576009|564450|572669|564906|573410|576504|576017|574392|576751|583161|566695|577007|566653|566679|573311|573394|573329|564930|565000|564922|573295|564914|573485|573337|544874|570846|565473|573402|573352|573428|573386|564948|573303|573188|573469|565671|573204|581199|565887|586867|568451|568444|573196|564500|571513|588566|565655|565812|586917)"]),
    ("WiZ", [r"\bwiz\b", r"^603571", r"^603449"]),
    ("Speed Queen", [r"\bspeed\s*queen\b", r"\bsq\b", r"^d519127", r"^df7004", r"^dr7004", r"^dv2000", r"^dc5004", r"^ff7011", r"^dr5004", r"^tv2000", r"^tc5003", r"^tr7006", r"^tr5006"]),
    ("FRIGIDAIRE", [r"\bfrigidaire\b", r"^pdsh\d+", r"^gcfg\d+", r"^prfs\d+", r"^pmos\d+", r"^pcfe\d+"]),
    ("Whirlpool", [r"\bwhirlpool\b", r"^wdts\d+", r"^wmms\d+", r"^wsgs\d+"]),
    ("GE Appliances", [r"\bge\b", r"\bgeneral\s*electric\b", r"^pdt\d+", r"^pdd\d+", r"^ptd\d+", r"^ptw\d+", r"^gde\d+", r"^fcm\d+", r"^gne\d+", r"^pad\d+", r"^pge\d+", r"^pep\d+", r"^ps960", r"^pb900", r"^pcwk\d+", r"^gcst\d+", r"^jxgri"]),
    ("Café", [r"\bcaf[eé]\b", r"^ces700", r"^chp90", r"^cvm51", r"^c9tma", r"^c7cda", r"^c7ceb", r"^c7ces", r"^cve28"]),
    ("KitchenAid", [r"\bkitchen\s*aid\b", r"\bkitchenaid\b", r"^kdfm\d+", r"^kdts\d+", r"^kdps\d+", r"^kmmf\d+", r"^kses\d+"]),
    ("LG", [r"\blg\b", r"^ldph\d+", r"^wke100", r"^lt18", r"^mser2090", r"^lsel6333"]),
    ("Grizzly", [r"\bgrizzly\b", r"^g0771z", r"^t27417"]),
    ("Oliver Machinery", [r"\boliver\b", r"^10047vs", r"^4225\.201", r"^kc-426c", r"^10045\.201", r"^10014\.201", r"^4430\.201", r"^10055\.201"]),
    ("SawStop", [r"\bsawstop\b", r"^tgp2-fa", r"^atgi-fa", r"^atgp-fa", r"^tgi2-fa", r"^tgi2-t36a"]),
    ("Bow Products", [r"\bbow\s*products\b", r"^xt524", r"^xt536", r"^xt546", r"^xtp235", r"^xtp242"]),
    ("Leviton", [r"\bleviton\b", r"^r02-", r"^pbuc", r"^r00-", r"^r92-", r"^r12-", r"^r62-", r"^165-04729", r"^161-04720", r"^r56-", r"^r20-05378", r"^r51-", r"^s03-", r"^174-0csb3", r"^r50-", r"^r52-"]),
    ("Square D", [r"\bsquare\s*d\b", r"^hom2040", r"^hom3060", r"^qo612"]),
    ("Southwire", [r"\bsouthwire\b", r"^bha1", r"^g1941", r"^g1950", r"^g1951", r"^52c3", r"^52c14", r"^54151", r"^54171", r"^52151", r"^72171", r"^wc1v12w", r"^13093005", r"^r50003", r"^10-4 so", r"^2/2/4 ud", r"^55418901"]),
    ("Rees Cast Stone", [r"\brees\s*cast\s*stone\b", r"^25-a\b", r"^38-e\b", r"^59-j\b", r"^44-a\b"]),
    ("James Hardie", [r"\bhardie\b", r"\bjameshardie\b", r"^8912220", r"^8904015"]),
    ("LP SmartSide", [r"\bsmartside\b", r"\bsmart\s*lap\b", r"\bsmart\s*pan\b", r"\bsmart\s*vented\b", r"^25796", r"^40503", r"^25825", r"^25822"]),
    ("CertainTeed", [r"\bcertainteed\b", r"\beasi-lite\b", r"\bfirelite\b", r"^640383", r"^653258"]),
    ("First Alert", [r"\bfirst\s*alert\b", r"^1046793"]),
    ("BRK", [r"\bbrk\b", r"^1046870"]),
    ("Wera", [r"\bwera\b", r"^05134545001", r"^133164", r"^950/9", r"^9516"]),
    ("Kreg", [r"\bkreg\b", r"^kpt", r"^bcb2a20a", r"^batt4a", r"^batt2a", r"^crgr401a"]),
    ("ProVia", [r"\bprovia\b", r"\becoliteplus\b", r"^1501831", r"^1501832"]),
    ("United Window & Door", [r"\bunited\s*window\b", r"^1517602", r"^1517603", r"^1517604", r"^1517605", r"^1515974"]),
    ("Velux", [r"\bvelux\b", r"^fs c01", r"^fs c04", r"^fs c06"])
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
    raw_brands = [
        clean_placeholder(unilog_brand),
        clean_placeholder(e1_brand),
        clean_placeholder(dib_brand)
    ]
    raw_brand = next((b for b in raw_brands if b), "")
    clean_manuf = strip_trailing_distributor_codes(clean_placeholder(part_manuf))
    clean_desc = (part_desc or "").strip()
    clean_mpn = (mfg_part_num or "").strip()
    
    # 1. Exact match on raw_brand alias
    if raw_brand:
        key = raw_brand.lower()
        if key in ALIASES:
            canon_key = ALIASES[key]
            if canon_key in CANONICAL:
                return format_canonical_result(CANONICAL[canon_key], 'EXACT_BRAND_ALIAS', 1.0)

    # 2. Exact match on clean_manuf alias
    if clean_manuf:
        m_lower = clean_manuf.lower()
        if m_lower in ALIASES:
            canon_key = ALIASES[m_lower]
            if canon_key in CANONICAL:
                return format_canonical_result(CANONICAL[canon_key], 'MANUF_ALIAS_RESOLVED', 0.98)

    # 3. Match against strict regex patterns (with word boundaries)
    for canon_name, patterns in STRICT_BRAND_PATTERNS:
        for pat in patterns:
            if re.search(pat, clean_desc, re.IGNORECASE) or re.search(pat, clean_mpn, re.IGNORECASE) or re.search(pat, clean_manuf, re.IGNORECASE):
                if canon_name in CANONICAL:
                    return format_canonical_result(CANONICAL[canon_name], 'STRICT_REGEX_BRAND_RESOLVED', 0.96)

    # 4. Fuzzy match against ALIASES keys (token set ratio >= 85)
    search_terms = [clean_manuf, raw_brand, clean_desc[:30]]
    search_term = next((t for t in search_terms if t), "")
    if search_term:
        best_match = process.extractOne(search_term.lower(), ALIASES.keys(), scorer=fuzz.token_set_ratio)
        if best_match and best_match[1] >= 85:
            canon_key = ALIASES[best_match[0]]
            if canon_key in CANONICAL:
                return format_canonical_result(CANONICAL[canon_key], 'FUZZY_ENTITY_RESOLVED', round(best_match[1]/100.0, 2))

    # 5. Clean fallback (No hallucinated default)
    fallback_name = raw_brand or clean_manuf or "Unbranded"
    return {
        'MANUFACTURER_NAME': clean_manuf or fallback_name,
        'BRAND_NAME': fallback_name,
        'mfg_code': '',
        'brand_code': '',
        'provenance': 'FALLBACK_RAW',
        'confidence': 0.60
    }
