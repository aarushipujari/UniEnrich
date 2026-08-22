"""
UniEnrich Multi-Channel Copywriting Synthesizer
Generates 5 distinct description formats dynamically from extracted and inferred attributes:
1. INVOICE_DESC (≤ 40 chars, UPPERCASE)
2. MOBILE_DESC (60–80 chars)
3. SHORT_DESC / Product Title (Formula: Brand + Series + MPN + Item Type + Modifiers + Attributes)
4. LONG_DESC1 (Comprehensive attribute-rich sentence)
5. RETAIL_DESC & MARKETING_DESCRIPTION
"""
import re

def build_invoice_desc(product_name: str, mpn: str, attrs: dict) -> str:
    """
    Constructs Invoice Description: strictly <= 40 chars, UPPERCASE, dense trade abbreviations.
    Never fabricates values.
    """
    tokens = []
    p_name = (product_name or "ITEM").upper()
    
    # Abbreviate product name if long
    if "SANDING BELT" in p_name:
        tokens.append("SAND BELT")
    elif "SANDING DISC" in p_name:
        tokens.append("SAND DISC")
    elif "CUT-OFF DISC" in p_name or "CUT OFF" in p_name:
        tokens.append("CUT OFF DISC")
    elif "SAW BLADE" in p_name:
        tokens.append("SAW BLADE")
    elif "CIRCULAR SAW" in p_name:
        tokens.append("CIRC SAW")
    elif "MITER SAW" in p_name:
        tokens.append("MITER SAW")
    elif "LASER LEVEL" in p_name or "CROSS LINE LASER" in p_name:
        tokens.append("LASER LEVEL")
    elif "SPINDLE SANDER" in p_name:
        tokens.append("SPINDLE SAND")
    elif "DISHWASHER" in p_name:
        tokens.append("DISHWASHER")
    elif "HEATER KIT" in p_name:
        tokens.append("HEATER KIT")
    elif "LED LIGHT BULB" in p_name:
        tokens.append("LED BULB")
    elif "COMPOSITE DECK" in p_name:
        tokens.append("DECK BRD")
    else:
        tokens.append(p_name[:14])

    # Append real specs if present
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

    if attrs.get('sound_level', ('', ''))[0]:
        tokens.append(f"{attrs['sound_level'][0]}DBA")

    if attrs.get('pack_qty'):
        tokens.append(f"{attrs['pack_qty']}PC")

    result = " ".join(tokens).upper()
    if len(result) > 40:
        result = result[:40].strip()
    return result

def build_mobile_desc(mfg_name: str, brand_name: str, product_name: str, series: str, mpn: str, attrs: dict) -> str:
    """
    Constructs Mobile Description: strictly targeted 60–80 chars.
    Formula: [Manufacturer] [Brand], [Product Type], [Series / Key Attribute], [MPN]
    """
    clean_brand = brand_name.replace('®', '').replace('™', '').strip()
    clean_mfg = mfg_name.replace('®', '').replace('™', '').strip()
    
    brand_lead = f"{clean_mfg} {clean_brand}".strip() if clean_mfg and clean_mfg != clean_brand and len(clean_mfg) < 30 else clean_brand
    p_type = product_name or "Product"
    
    parts = []
    if brand_lead:
        parts.append(brand_lead)
    parts.append(p_type)
    if series:
        parts.append(series)
    if mpn:
        parts.append(mpn)
        
    cand = ", ".join([p for p in parts if p])
    
    # Expand with real attributes if < 60 chars
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

    # If still below 60 chars, add full manufacturer prefix if room permits
    if len(cand) < 60 and clean_mfg and clean_mfg not in cand:
        cand_plus = f"{clean_mfg}, {cand}"
        if len(cand_plus) <= 80:
            cand = cand_plus

    # If longer than 80 chars, trim at comma or word
    if len(cand) > 80:
        cand = cand[:80].rsplit(',', 1)[0]
        if len(cand) > 80:
            cand = cand[:80].strip()

    return cand

def build_short_desc(brand_name: str, series: str, mpn: str, product_name: str, with_modifier: str, attrs: dict) -> str:
    """
    Constructs Product Title / Short Desc formula:
    [Brand®] [Series] [MPN] [Item Type] [With Modifier], [Key Real Attributes]
    """
    title_lead_parts = [brand_name]
    if series:
        title_lead_parts.append(series)
    if mpn:
        title_lead_parts.append(mpn)
    title_lead_parts.append(product_name)
    if with_modifier:
        title_lead_parts.append(with_modifier)
        
    title_main = " ".join([p for p in title_lead_parts if p]).strip()
    
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
    Constructs Long Description: comprehensive attribute sentence with all real normalized values and UOMs.
    Never fabricates values that were not extracted or legitimately deduced.
    """
    lead = f"{brand_name} {product_name}".strip()
    if with_modifier:
        lead += f" {with_modifier}"
        
    clauses = [lead]
    if series:
        clauses.append(series)
    if attrs.get('voltage', ('', ''))[0]:
        clauses.append(f"{attrs['voltage'][0]} {attrs['voltage'][1]}")
    if attrs.get('amperage', ('', ''))[0]:
        clauses.append(f"{attrs['amperage'][0]} {attrs['amperage'][1]}")
    if attrs.get('wattage', ('', ''))[0]:
        clauses.append(f"{attrs['wattage'][0]} {attrs['wattage'][1]}")
    if attrs.get('mounting'):
        clauses.append(f"{attrs['mounting']} Mounting")
    if attrs.get('dimensions'):
        clauses.append(attrs['dimensions'])
    if attrs.get('sound_level', ('', ''))[0]:
        clauses.append(f"{attrs['sound_level'][0]} {attrs['sound_level'][1]} Sound Level")
    if attrs.get('material'):
        clauses.append(attrs['material'])
    if attrs.get('color'):
        clauses.append(attrs['color'])
    if attrs.get('additional_info'):
        clauses.append(f"Additional Information: {attrs['additional_info']}")
        
    return ", ".join([c for c in clauses if c])

def build_retail_desc(series: str, product_name: str, attrs: dict) -> str:
    """Constructs Retail Description: concise product summary."""
    lead = f"{series} {product_name}" if series else product_name
    parts = [lead]
    if attrs.get('mounting'):
        parts.append(f"{attrs['mounting']} Mounting")
    if attrs.get('material'):
        parts.append(attrs['material'])
    elif attrs.get('color'):
        parts.append(attrs['color'])
    return ", ".join(parts)
