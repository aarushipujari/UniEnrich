"""
UniEnrich UOM & Decimal-to-Fraction Normalization Engine
Enforces Unilog Master UOM Standards, 63 exact inch fraction conversions, and spacing rules.
"""
import os
import json
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

with open(os.path.join(DATA_DIR, 'decimal_fraction.json'), 'r') as f:
    DECIMAL_FRACTION_MAP = {float(k): v for k, v in json.load(f).items()}

with open(os.path.join(DATA_DIR, 'uom_standards.json'), 'r') as f:
    UOM_DATA = json.load(f)

APPROVED_UNITS = set(UOM_DATA.get('approved_units', []))
UNIT_ALIASES = UOM_DATA.get('unit_aliases', {})

def decimal_to_fraction(val) -> str:
    """
    Converts decimal inch values to compound fractional representations:
    e.g. 50.25 -> "50-1/4", 0.5 -> "1/2", 0.045 -> "3/64", 33.4375 -> "33-7/16".
    If already a fraction or string, normalizes it.
    """
    if val is None or val == "":
        return ""
    
    # If already formatted fraction like "50-1/4" or "1/2"
    s_val = str(val).strip().replace('"', '').replace("''", '')
    if "/" in s_val:
        return s_val
    
    try:
        f_val = float(s_val)
    except ValueError:
        return s_val

    # Separate whole part and fractional part
    whole = int(f_val)
    frac = round(f_val - whole, 6)

    if frac == 0.0:
        return str(whole)

    # Find closest match in decimal_fraction_map
    best_match = None
    min_diff = 0.015 # threshold
    for dec, frac_str in DECIMAL_FRACTION_MAP.items():
        diff = abs(frac - dec)
        if diff < min_diff:
            min_diff = diff
            best_match = frac_str

    if best_match:
        if whole > 0:
            return f"{whole}-{best_match}"
        else:
            return best_match
    
    return str(val)

def normalize_uom(unit_str: str) -> str:
    """Normalizes raw unit string into approved single canonical form (e.g. inches -> in)."""
    if not unit_str:
        return ""
    u = unit_str.strip().lower()
    if u in UNIT_ALIASES:
        return UNIT_ALIASES[u]
    for k, v in UNIT_ALIASES.items():
        if u == k.lower():
            return v
    # Check if exact match in approved units (case preserving)
    for app in APPROVED_UNITS:
        if u == app.lower():
            return app
    return unit_str.strip()

def format_measurement(num, unit: str) -> str:
    """Formats number and unit with strict single space and normalized unit (e.g. '24 in', '120 V')."""
    if num is None or str(num).strip() == "":
        return ""
    num_str = decimal_to_fraction(num)
    norm_u = normalize_uom(unit)
    if not norm_u:
        return num_str
    return f"{num_str} {norm_u}"

def parse_dimension_string(dim_str: str) -> str:
    """
    Parses dimension strings like '1/2""x18""', '4-1/2""x.045""x7/8""', '24x24'
    and returns standardized fraction inch string with proper 'x' and 'in'.
    """
    if not dim_str:
        return ""
    s = dim_str.replace('"', '').replace("''", '').strip()
    parts = re.split(r'\s*[xX]\s*', s)
    norm_parts = []
    for p in parts:
        p_clean = p.strip()
        if p_clean:
            norm_parts.append(decimal_to_fraction(p_clean))
    return " x ".join(norm_parts)
