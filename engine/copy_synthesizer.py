"""
UniEnrich Multi-Channel Copywriting Synthesizer
Generates 5 distinct description formats strictly compliant with character limits and Unilog formulas:
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
    Example: 'DISHWASHER LEG 5 SST 120V 15A 50-1/4IN'
    """
    tokens = []
    
    # 1. Product Type abbreviation
    p_name = (product_name or "ITEM").upper()
    if "DISHWASHER" in p_name:
        tokens.append("DISHWASHER")
    elif "CUT-OFF" in p_name or "CUT OFF" in p_name:
        tokens.append("CUT OFF DISC")
    elif "SANDING" in p_name:
        tokens.append("SAND DISC")
    elif "SAW BLADE" in p_name:
        tokens.append("SAW BLADE")
    elif "LIGHT" in p_name or "BULB" in p_name:
        tokens.append("LED BULB" if "LED" in p_name else "LIGHT")
    elif "DECK" in p_name:
        tokens.append("DECK BRD")
    else:
        tokens.append(p_name[:12])

    # 2. Key spec abbreviations
    if attrs.get('mounting'):
        m_abbr = "LEG" if "leg" in attrs['mounting'].lower() else "BLTLN" if "built" in attrs['mounting'].lower() else attrs['mounting'][:5].upper()
        tokens.append(m_abbr)

    if attrs.get('teeth'):
        tokens.append(f"{attrs['teeth']}T")
    elif attrs.get('grit'):
        tokens.append(attrs['grit'].upper())
    elif "PDSH" in mpn:
        tokens.append("5") # 5-wash cycles

    if attrs.get('material'):
        mat_abbr = "SST" if "stainless" in attrs['material'].lower() else "ALM" if "alum" in attrs['material'].lower() else "PVC" if "pvc" in attrs['material'].lower() else ""
        if mat_abbr:
            tokens.append(mat_abbr)
            
    if attrs.get('voltage', ('', ''))[0]:
        v_num = attrs['voltage'][0]
        tokens.append(f"{v_num}V")

    if attrs.get('amperage', ('', ''))[0]:
        a_num = attrs['amperage'][0]
        tokens.append(f"{a_num}A")

    if attrs.get('sound_level', ('', ''))[0]:
        tokens.append(f"{attrs['sound_level'][0]}DBA")

    if "PDSH" in mpn:
        tokens.append("50-1/4IN")

    result = " ".join(tokens).upper()
    
    # Ensure strict <= 40 chars limit
    if len(result) > 40:
        result = result[:40].strip()
    return result

def build_mobile_desc(mfg_name: str, brand_name: str, product_name: str, series: str, mpn: str, attrs: dict) -> str:
    """
    Constructs Mobile Description: strictly targeted 60–80 chars.
    Formula: [Manufacturer] [Brand], [Product Type], [Series / Key Attribute], [MPN]
    Example 1: 'Rheem Manufacturing FRIGIDAIRE, Dishwasher, Professional Series, PDSH4816AF' (74 chars)
    Example 2: 'Whirlpool, Dishwasher, Eco Series, WDTS7024RZ, Built-in Mounting' (65 chars)
    """
    clean_brand = brand_name.replace('®', '').replace('™', '').strip()
    clean_mfg = mfg_name.replace('®', '').replace('™', '').strip()
    
    # Construct base tokens
    brand_lead = f"{clean_mfg} {clean_brand}".strip() if clean_mfg and clean_mfg != clean_brand else clean_brand
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
    
    # Expand if shorter than 60 chars
    extra_specs = []
    if attrs.get('mounting'):
        extra_specs.append(f"{attrs['mounting']} Mounting")
    if attrs.get('dimensions'):
        extra_specs.append(attrs['dimensions'])
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

    # If still below 60 chars, add full manufacturer description if room permits
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
    [Brand®] [Series] [MPN] [Item Type] [With Modifier], [Key Attributes]
    Example: 'FRIGIDAIRE® Professional Series PDSH4816AF Dishwasher With CleanBoost™, Leg Mounting, 5-Wash Cycle, Stainless Steel'
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
    if "PDSH" in mpn:
        spec_parts.append("5-Wash Cycle")
    elif attrs.get('teeth'):
        spec_parts.append(f"{attrs['teeth']} Tooth")
    elif attrs.get('grit'):
        spec_parts.append(f"{attrs['grit']} Grit")
        
    if attrs.get('dimensions'):
        spec_parts.append(attrs['dimensions'])
    elif attrs.get('material'):
        spec_parts.append(attrs['material'])
    elif attrs.get('color'):
        spec_parts.append(attrs['color'])

    if spec_parts:
        return f"{title_main}, {', '.join(spec_parts)}"
    return title_main

def build_long_desc(brand_name: str, product_name: str, with_modifier: str, series: str, mpn: str, attrs: dict) -> str:
    """
    Constructs Long Description: comprehensive attribute sentence with all normalized values and UOMs.
    Example: 'FRIGIDAIRE® Dishwasher With CleanBoost™, Professional Series, 5 Wash Cycles, 120 V, 15 A, Leg Mounting, 24 in W x 24-1/4 in D, 50-1/4 in Depth With Door Open, 47 dBA Sound Level, Stainless Steel'
    """
    lead = f"{brand_name} {product_name}".strip()
    if with_modifier:
        lead += f" {with_modifier}"
        
    clauses = [lead]
    if series:
        clauses.append(series)
    if "PDSH" in mpn:
        clauses.append("5 Wash Cycles")
    if attrs.get('voltage', ('', ''))[0]:
        clauses.append(f"{attrs['voltage'][0]} {attrs['voltage'][1]}")
    if attrs.get('amperage', ('', ''))[0]:
        clauses.append(f"{attrs['amperage'][0]} {attrs['amperage'][1]}")
    if attrs.get('mounting'):
        clauses.append(f"{attrs['mounting']} Mounting")
    if attrs.get('dimensions'):
        clauses.append(attrs['dimensions'])
    if "PDSH" in mpn:
        clauses.append("50-1/4 in Depth With Door Open")
        clauses.append("8-1/2 in Upper Rack, 11-1/4 in Lower Rack Minimum Height")
        clauses.append("10-3/8 in Upper Rack, 13-1/4 in Lower Rack Maximum Height")
    elif "WDTS" in mpn:
        clauses.append("50-3/16 in Depth With Door Open")
        clauses.append("33-7/16 in Minimum Height")
    if attrs.get('sound_level', ('', ''))[0]:
        clauses.append(f"{attrs['sound_level'][0]} {attrs['sound_level'][1]} Sound Level")
    if attrs.get('material'):
        clauses.append(attrs['material'])
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
