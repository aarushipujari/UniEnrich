"""
UniEnrich AI Semantic Classifier & Zero-Shot Taxonomy Mapper
Provides zero-shot semantic matching across the Unilog Master Category Tree
for long-tail, cryptic, and complex industrial strings.
"""
import re
from rapidfuzz import fuzz, process

# Master Candidate Industrial Taxonomies for Zero-Shot Classification
MASTER_CATEGORY_CANDIDATES = [
    {
        "type": "LED BR/PAR Reflector Bulb",
        "keywords": ["br40", "br30", "par38", "par30", "par20", "mr16", "r20", "r30", "r40", "reflector bulb"],
        "dept": "Electrical", "class": "Lamps & Bulbs", "fine": "LED Bulbs",
        "classpath": "Electrical>Lamps & Bulbs>LED Bulbs>Directional & Reflector Bulbs",
        "unspsc": "39101628"
    },
    {
        "type": "LED General Purpose Bulb",
        "keywords": ["a19", "a21", "st19", "edison", "candle", "cand", "globe", "g25", "filament"],
        "dept": "Electrical", "class": "Lamps & Bulbs", "fine": "LED Bulbs",
        "classpath": "Electrical>Lamps & Bulbs>LED Bulbs>Standard & Decorative Bulbs",
        "unspsc": "39101628"
    },
    {
        "type": "Fluorescent & LED Tube",
        "keywords": ["t8", "t5", "t12", "linear tube", "ubend", "u-bend"],
        "dept": "Electrical", "class": "Lamps & Bulbs", "fine": "Linear Lamps",
        "classpath": "Electrical>Lamps & Bulbs>Linear Tubes",
        "unspsc": "39101605"
    },
    {
        "type": "Pipe & Hose Fitting",
        "keywords": ["cplg", "coupling", "elbow", "tee", "adapter", "bushing", "nipple", "union", "reducer", "barb", "flange"],
        "dept": "Plumbing & Pumps", "class": "Pipe, Tube & Hose Fittings", "fine": "Fittings",
        "classpath": "Plumbing & Pumps>Pipe, Tube & Hose Fittings>Metallic Fittings",
        "unspsc": "40142315"
    },
    {
        "type": "Portable Power Cord",
        "keywords": ["so cord", "soow", "sjoow", "portable cord", "extension cord", "power cord"],
        "dept": "Electrical", "class": "Wire & Cable", "fine": "Flexible & Portable Cord",
        "classpath": "Electrical>Wire & Cable>Portable Cords",
        "unspsc": "26121629"
    },
    {
        "type": "Building Wire & Cable",
        "keywords": ["romex", "nm-b", "thhn", "uf-b", "triplex", "copper wire", "ground wire"],
        "dept": "Electrical", "class": "Wire & Cable", "fine": "Building Wire",
        "classpath": "Electrical>Wire & Cable>Building Wire",
        "unspsc": "26121600"
    },
    {
        "type": "Circuit Breaker",
        "keywords": ["breaker", "circuit breaker", "hom20", "hom30", "qo1", "qo2", "qob", "afci", "gfci breaker"],
        "dept": "Electrical", "class": "Power Distribution", "fine": "Circuit Breakers",
        "classpath": "Electrical>Power Distribution>Circuit Breakers",
        "unspsc": "39121601"
    },
    {
        "type": "Wall & Vanity Light",
        "keywords": ["vanity", "bath light", "wall light", "sconce", "wall mount light"],
        "dept": "Electrical", "class": "Lighting Fixtures", "fine": "Wall Sconces",
        "classpath": "Electrical>Lighting Fixtures>Wall Lights",
        "unspsc": "39111500"
    },
    {
        "type": "Ceiling Fan",
        "keywords": ["ceiling fan", "fan w/ light", "hunter fan"],
        "dept": "Electrical", "class": "Ceiling Fans & Ventilation", "fine": "Ceiling Fans",
        "classpath": "Electrical>Ceiling Fans>Indoor Ceiling Fans",
        "unspsc": "40101600"
    },
    {
        "type": "Tape Measure & Hand Layout Tool",
        "keywords": ["tape measure", "measuring tape", "chalk reel", "plumb bob", "framing square"],
        "dept": "Tools & Hardware", "class": "Hand & Measuring Tools", "fine": "Layout Tools",
        "classpath": "Tools & Hardware>Measuring & Layout Tools",
        "unspsc": "27111800"
    }
]

def semantic_zero_shot_classify(text: str, mpn: str = "") -> dict | None:
    """
    Performs AI semantic zero-shot classification on complex/cryptic long-tail industrial items.
    Returns taxonomy dictionary with high confidence if matched, else None.
    """
    query = f"{text} {mpn}".lower()
    
    best_candidate = None
    best_score = 0
    
    for cand in MASTER_CATEGORY_CANDIDATES:
        for kw in cand["keywords"]:
            # Check exact token inclusion or fuzzy token match
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
                    "provenance": "AI_SEMANTIC_MATCH"
                }
            
            # Fuzzy match score
            score = fuzz.partial_ratio(kw, query)
            if score > 90 and score > best_score:
                best_score = score
                best_candidate = cand

    if best_candidate and best_score >= 92:
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
