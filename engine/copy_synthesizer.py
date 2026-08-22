"""
UniEnrich Multi-Channel Copywriting Synthesizer
Generates 5 standard description tiers strictly from grounded facts:
1. INVOICE_DESC (≤ 40 chars, UPPERCASE, Universal Algorithmic B2B Abbreviator)
2. MOBILE_DESC (Concise, strictly ≤ 80 chars, ZERO synthetic filler)
3. SHORT_DESC / Product Title (Unilog Standard Formula)
4. LONG_DESC1 (Grammatically complete technical sentence)
5. RETAIL_DESC & MARKETING_DESCRIPTION
"""
import re

COMMON_INDUSTRIAL_ABBRS = {
    "STAINLESS STEEL": "SST",
    "ALUMINUM": "ALUM",
    "GALVANIZED": "GALV",
    "POLYVINYL CHLORIDE": "PVC",
    "POLYETHYLENE": "POLY",
    "RECEPTACLE": "RCPT",
    "CIRCUIT BREAKER": "CIR BRKR",
    "COUPLING": "CPLG",
    "DISCONNECT": "DISC",
    "TRANSFORMER": "XFMR",
    "COMPRESSION": "COMP",
    "EXTENSION": "EXT",
    "ENCLOSURE": "ENCL",
    "JUNCTION": "JCT",
    "PORTABLE": "PORT",
    "COMMERCIAL": "COMM",
    "RESIDENTIAL": "RES",
    "ASSEMBLY": "ASSY",
    "CARBIDE": "CRB",
    "RECIPROCATING": "RECIP",
    "OSCILLATING": "OSC",
    "LUBRICANT": "LUB",
    "FASTENER": "FSTNR",
    "MORTAR": "MRTR"
}

def abbreviate_token(word: str) -> str:
    """
    Universal algorithmic consonant-extractor for B2B catalog invoice lines.
    Preserves leading vowel, drops internal vowels and duplicate consonants.
    """
    if len(word) <= 4:
        return word
    
    # Check known roots
    w_up = word.upper()
    if w_up in COMMON_INDUSTRIAL_ABBRS:
        return COMMON_INDUSTRIAL_ABBRS[w_up]

    first_char = w_up[0]
    rest = w_up[1:]
    # Remove vowels from rest
    consonants = re.sub(r'[AEIOU]', '', rest)
    # Remove consecutive duplicate consonants
    dedup = re.sub(r'([A-Z])\1+', r'\1', consonants)
    
    res = first_char + dedup
    return res[:4] if len(res) > 4 else res

def universal_abbreviate_phrase(phrase: str, max_len: int = 40) -> str:
    """
    Universally shortens any arbitrary product noun phrase to <= max_len.
    """
    phrase_upper = (phrase or "").strip().upper()
    for full_term, abbr in COMMON_INDUSTRIAL_ABBRS.items():
        phrase_upper = phrase_upper.replace(full_term, abbr)
        
    tokens = phrase_upper.split()
    abbr_tokens = [abbreviate_token(t) if len(t) > 4 else t for t in tokens]
    res = " ".join(abbr_tokens)
    return res[:max_len].strip()

def build_invoice_desc(product_name: str, mpn: str, attrs: dict) -> str:
    """
    Constructs Invoice Description: strictly <= 40 chars, UPPERCASE.
    Zero product-specific hardcodes; uses universal algorithmic abbreviation.
    """
    base_abbr = universal_abbreviate_phrase(product_name, max_len=18)
    tokens = [base_abbr]

    if attrs.get('mounting'):
        m_abbr = "LEG" if "leg" in attrs['mounting'].lower() else "BLT" if "built" in attrs['mounting'].lower() else attrs['mounting'][:4].upper()
        tokens.append(m_abbr)

    if attrs.get('teeth'):
        tokens.append(f"{attrs['teeth']}T")
    elif attrs.get('grit'):
        tokens.append(attrs['grit'].upper())

    if attrs.get('material'):
        mat_token = universal_abbreviate_phrase(attrs['material'], max_len=4)
        tokens.append(mat_token)

    if attrs.get('voltage', ('', ''))[0]:
        tokens.append(f"{attrs['voltage'][0]}V")

    if attrs.get('amperage', ('', ''))[0]:
        tokens.append(f"{attrs['amperage'][0]}A")

    if attrs.get('pack_qty'):
        tokens.append(f"{attrs['pack_qty']}PK")

    result = " ".join(tokens).upper()
    if len(result) > 40:
        result = result[:40].strip()
    return result

def build_mobile_desc(mfg_name: str, brand_name: str, product_name: str, series: str, mpn: str, attrs: dict) -> str:
    """
    Constructs Mobile Description: strictly grounded in real product attributes.
    Zero synthetic marketing filler ("Commercial Grade", "Standard Duty").
    Strictly constrained to <= 80 characters.
    """
    clean_brand = brand_name.replace('®', '').replace('™', '').strip()
    clean_mfg = mfg_name.replace('®', '').replace('™', '').strip()
    
    # Determine brand header
    if clean_mfg and clean_brand and clean_mfg.lower() != clean_brand.lower() and len(clean_mfg) < 25:
        brand_hdr = f"{clean_mfg} {clean_brand}"
    else:
        brand_hdr = clean_brand or clean_mfg
        
    p_type = product_name or "Product"
    
    # Priority ordered grounded attributes
    elements = []
    if brand_hdr:
        elements.append(brand_hdr)
    if series:
        elements.append(series)
    if mpn:
        elements.append(mpn)
    elements.append(p_type)

    if attrs.get('dimensions'):
        elements.append(attrs['dimensions'])
    if attrs.get('teeth'):
        elements.append(f"{attrs['teeth']}T")
    elif attrs.get('grit'):
        elements.append(attrs['grit'])
    if attrs.get('voltage', ('', ''))[0]:
        elements.append(f"{attrs['voltage'][0]} {attrs['voltage'][1]}")
    if attrs.get('color'):
        elements.append(attrs['color'])
    elif attrs.get('material'):
        elements.append(attrs['material'])
    if attrs.get('pack_qty'):
        elements.append(f"{attrs['pack_qty']} Pack")

    # Build description while strictly respecting the 80 character ceiling
    assembled = []
    curr_len = 0
    for el in elements:
        addition_len = len(el) + (2 if assembled else 0)
        if curr_len + addition_len <= 80:
            assembled.append(el)
            curr_len += addition_len
        else:
            break

    return ", ".join(assembled)

def build_short_desc(brand_name: str, series: str, mpn: str, product_name: str, with_modifier: str, attrs: dict) -> str:
    """
    Constructs Product Title: [Brand®] [Series] [MPN] [Item Type] [With Modifier], [Key Attributes]
    """
    title_parts = []
    if brand_name:
        title_parts.append(brand_name)
    if series:
        title_parts.append(series)
    if mpn:
        title_parts.append(mpn)
    if product_name:
        title_parts.append(product_name)
    if with_modifier:
        title_parts.append(with_modifier)
        
    title_main = " ".join(title_parts).strip()
    
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
    subject = f"The {brand_name} {product_name}".strip() if brand_name else f"The {product_name}".strip()
    if series and brand_name:
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
        specs.append(f"constructed from {attrs['material']}")
    elif attrs.get('color'):
        specs.append(f"finished in {attrs['color']}")
    if attrs.get('mounting'):
        specs.append(f"featuring {attrs['mounting']} mounting")
    if attrs.get('sound_level', ('', ''))[0]:
        specs.append(f"with {attrs['sound_level'][0]} {attrs['sound_level'][1]} sound rating")

    if specs:
        narrative = f"{subject} is designed for commercial and industrial applications, {', '.join(specs)}."
    elif mpn:
        narrative = f"{subject} (Part Number: {mpn})."
    else:
        narrative = f"{subject}."
        
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
