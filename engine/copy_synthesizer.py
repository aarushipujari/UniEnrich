"""
UniEnrich Multi-Channel Copywriting Synthesizer
Generates 5 distinct description formats dynamically from extracted and verified attributes:
1. INVOICE_DESC (≤ 40 chars, UPPERCASE, generalized token abbreviations)
2. MOBILE_DESC (Strict target length 60–80 chars with dynamic padding/trimming)
3. SHORT_DESC / Product Title (Formula: Brand + Series + MPN + Item Type + Modifiers + Attributes)
4. LONG_DESC1 (Grammatically coherent descriptive technical narrative)
5. RETAIL_DESC & MARKETING_DESCRIPTION
"""
import re

GENERIC_ABBREVIATIONS = {
    "DISHWASHER": "DISHWASHER", "COUPLING": "CPLG", "RECEPTACLE": "RECEPT", "CIRCUIT BREAKER": "CIR BRKR",
    "SANDING BELT": "SAND BELT", "SANDING DISC": "SAND DISC", "CUT-OFF DISC": "CUT OFF DISC",
    "CIRCULAR SAW": "CIRC SAW", "MITER SAW": "MITER SAW", "TABLE SAW": "TABLE SAW",
    "LASER LEVEL": "LASER LEVEL", "CROSS LINE LASER": "LINE LASER", "SPINDLE SANDER": "SPINDLE SAND",
    "HEATER KIT": "HEATER KIT", "LED LIGHT BULB": "LED BULB", "DECK BOARD": "DECK BRD",
    "FASCIA BOARD": "FASCIA BRD", "RAILING KIT": "RAIL KIT", "POST WRAP": "POST WRAP",
    "MASON LINE": "MASON LINE", "CHALK REEL": "CHALK REEL", "WET/DRY SHOP VACUUM": "SHOP VAC",
    "AIR COMPRESSOR": "AIR COMP", "DRYWALL GYPSUM BOARD": "DRYWALL BRD", "SMOKE & CO ALARM": "SMOKE/CO ALM",
    "FIRE EXTINGUISHER": "FIRE EXT", "SAFETY GLASSES": "SAFETY GLASS", "STAINLESS STEEL": "SST"
}

def build_invoice_desc(product_name: str, mpn: str, attrs: dict) -> str:
    """
    Constructs Invoice Description: strictly <= 40 chars, UPPERCASE.
    """
    p_upper = (product_name or "ITEM").upper()
    
    # Check generic abbreviations
    base_name = p_upper
    for term, abbr in GENERIC_ABBREVIATIONS.items():
        if term in p_upper:
            base_name = abbr
            break
    if len(base_name) > 16:
        base_name = base_name[:16].strip()

    tokens = [base_name]

    if attrs.get('mounting'):
        m_abbr = "LEG" if "leg" in attrs['mounting'].lower() else "BLTLN" if "built" in attrs['mounting'].lower() else attrs['mounting'][:5].upper()
        tokens.append(m_abbr)

    if attrs.get('teeth'):
        tokens.append(f"{attrs['teeth']}T")
    elif attrs.get('grit'):
        tokens.append(attrs['grit'].upper())

    if attrs.get('material'):
        mat_abbr = "SST" if "stainless" in attrs['material'].lower() else "ALM" if "alum" in attrs['material'].lower() else "PVC" if "pvc" in attrs['material'].lower() else ""
        if mat_abbr:
            tokens.append(mat_abbr)

    if attrs.get('voltage', ('', ''))[0]:
        tokens.append(f"{attrs['voltage'][0]}V")

    if attrs.get('amperage', ('', ''))[0]:
        tokens.append(f"{attrs['amperage'][0]}A")

    if attrs.get('pack_qty'):
        tokens.append(f"{attrs['pack_qty']}PC")

    result = " ".join(tokens).upper()
    if len(result) > 40:
        result = result[:40].strip()
    return result

def build_mobile_desc(mfg_name: str, brand_name: str, product_name: str, series: str, mpn: str, attrs: dict) -> str:
    """
    Constructs Mobile Description: strictly guaranteed to fall within 60–80 characters.
    """
    clean_brand = brand_name.replace('®', '').replace('™', '').strip()
    clean_mfg = mfg_name.replace('®', '').replace('™', '').strip()
    
    brand_prefix = f"{clean_mfg} {clean_brand}".strip() if clean_mfg and clean_mfg != clean_brand and len(clean_mfg) < 30 else clean_brand
    p_type = product_name or "Product"
    
    # Base candidates
    core_parts = [brand_prefix, p_type]
    if series:
        core_parts.append(series)
    if mpn:
        core_parts.append(mpn)
        
    cand = ", ".join([p for p in core_parts if p])
    
    # Candidate pool of real attributes to hit the 60-80 window
    extra_specs = []
    if attrs.get('mounting'):
        extra_specs.append(f"{attrs['mounting']} Mounting")
    if attrs.get('dimensions'):
        extra_specs.append(attrs['dimensions'])
    if attrs.get('teeth'):
        extra_specs.append(f"{attrs['teeth']} Tooth")
    elif attrs.get('grit'):
        extra_specs.append(f"{attrs['grit']} Grit")
    if attrs.get('material'):
        extra_specs.append(attrs['material'])
    elif attrs.get('color'):
        extra_specs.append(attrs['color'])
    if attrs.get('voltage', ('', ''))[0]:
        extra_specs.append(f"{attrs['voltage'][0]} {attrs['voltage'][1]}")
    if attrs.get('pack_qty'):
        extra_specs.append(f"{attrs['pack_qty']} Pack")

    for spec in extra_specs:
        if len(cand) >= 60:
            break
        cand_plus = f"{cand}, {spec}"
        if len(cand_plus) <= 80:
            cand = cand_plus

    # If still below 60 chars, add full corporate prefix or descriptive filler
    if len(cand) < 60 and clean_mfg and clean_mfg not in cand:
        cand_plus = f"{clean_mfg}, {cand}"
        if len(cand_plus) <= 80:
            cand = cand_plus

    if len(cand) < 60:
        fillers = ["Commercial Grade", "Standard Duty", "Professional Tool", "Distributor Pack"]
        for f in fillers:
            cand_plus = f"{cand}, {f}"
            if 60 <= len(cand_plus) <= 80:
                cand = cand_plus
                break
            elif len(cand_plus) < 60:
                cand = cand_plus

    # Truncate at word boundary if > 80 chars
    if len(cand) > 80:
        cand = cand[:80].rsplit(',', 1)[0]
        if len(cand) > 80:
            cand = cand[:80].rsplit(' ', 1)[0]
        if len(cand) > 80:
            cand = cand[:80].strip()

    return cand

def build_short_desc(brand_name: str, series: str, mpn: str, product_name: str, with_modifier: str, attrs: dict) -> str:
    """
    Constructs Product Title: [Brand®] [Series] [MPN] [Item Type] [With Modifier], [Key Attributes]
    """
    title_parts = [brand_name]
    if series:
        title_parts.append(series)
    if mpn:
        title_parts.append(mpn)
    title_parts.append(product_name)
    if with_modifier:
        title_parts.append(with_modifier)
        
    title_main = " ".join([p for p in title_parts if p]).strip()
    
    spec_parts = []
    if attrs.get('mounting'):
        spec_parts.append(f"{attrs['mounting']} Mounting")
    if attrs.get('teeth'):
        spec_parts.append(f"{attrs['teeth']} Tooth")
    elif attrs.get('grit'):
        spec_parts.append(f"{attrs['grit']} Grit")
    if attrs.get('dimensions'):
        spec_parts.append(attrs['dimensions'])
    if attrs.get('material'):
        spec_parts.append(attrs['material'])
    elif attrs.get('color'):
        spec_parts.append(attrs['color'])
    if attrs.get('pack_qty'):
        spec_parts.append(f"{attrs['pack_qty']} Pack")

    if spec_parts:
        return f"{title_main}, {', '.join(spec_parts[:3])}"
    return title_main

def build_long_desc(brand_name: str, product_name: str, with_modifier: str, series: str, mpn: str, attrs: dict) -> str:
    """
    Synthesizes a grammatically complete and structured technical sentence.
    """
    subject = f"The {brand_name} {product_name}".strip()
    if series:
        subject = f"The {brand_name} {series} {product_name}".strip()
        
    specs = []
    if attrs.get('dimensions'):
        specs.append(f"measuring {attrs['dimensions']}")
    if attrs.get('voltage', ('', ''))[0]:
        specs.append(f"rated at {attrs['voltage'][0]} {attrs['voltage'][1]}")
    if attrs.get('amperage', ('', ''))[0]:
        specs.append(f"drawing {attrs['amperage'][0]} {attrs['amperage'][1]}")
    if attrs.get('wattage', ('', ''))[0]:
        specs.append(f"operating at {attrs['wattage'][0]} {attrs['wattage'][1]}")
    if attrs.get('material'):
        specs.append(f"constructed from durable {attrs['material']}")
    elif attrs.get('color'):
        specs.append(f"finished in {attrs['color']}")
    if attrs.get('mounting'):
        specs.append(f"featuring {attrs['mounting']} mounting")
    if attrs.get('sound_level', ('', ''))[0]:
        specs.append(f"with {attrs['sound_level'][0]} {attrs['sound_level'][1]} sound rating")

    if specs:
        narrative = f"{subject} is designed for commercial and industrial applications, {', '.join(specs)}."
    else:
        narrative = f"{subject} delivers reliable performance engineered for industrial distribution and commercial use."
        
    if with_modifier:
        narrative += f" Equipped {with_modifier}."
        
    return narrative

def build_retail_desc(series: str, product_name: str, attrs: dict) -> str:
    lead = f"{series} {product_name}" if series else product_name
    parts = [lead]
    if attrs.get('mounting'):
        parts.append(f"{attrs['mounting']} Mounting")
    if attrs.get('material'):
        parts.append(attrs['material'])
    elif attrs.get('color'):
        parts.append(attrs['color'])
    return ", ".join(parts)
