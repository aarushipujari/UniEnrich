"""
UniEnrich Constrained Attribute Extractor & Normalizer
Extracts dimensional, electrical, physical, and functional attributes adhering strictly to LOV vocabularies.
Never fabricates unstated specs.
"""
import re
from .uom_normalizer import decimal_to_fraction, normalize_uom, format_measurement, parse_dimension_string

# Canonical series terms
KNOWN_SERIES = [
    "Professional Series", "Eco Series", "Gallery Series", "Transcend Lineage", "Enhance Naturals",
    "Enhance Basics", "Select 2.0", "Vintage Azek", "Landmark Azek", "Harvest Azek",
    "Steel Demon", "Speed Demon", "Cubitron II", "Hiolit", "Abranet", "Iridium",
    "Perform+", "Performance+", "Ceramic+", "Fuel", "Packout", "Surge", "Atomic 20V",
    "Flexvolt", "Max XR", "Starfish", "Quik-Lock", "T-Glide", "Slyde King"
]

# Canonical color/finish values
KNOWN_COLORS = {
    "ss": "Stainless Steel", "sst": "Stainless Steel", "stainless steel": "Stainless Steel",
    "wh": "White", "white": "White",
    "bk": "Black", "black": "Black", "blk": "Black",
    "bss": "Black Stainless Steel", "black stainless": "Black Stainless Steel",
    "mb": "Matte Black", "matte black": "Matte Black",
    "mw": "Matte White", "matte white": "Matte White",
    "ni": "Brushed Nickel", "nickel": "Brushed Nickel",
    "cpz": "Champagne Bronze", "bz": "Bronze", "dbz": "Dark Bronze",
    "ch": "Chrome", "clr": "Clear",
    "coastline": "Coastline", "english walnut": "English Walnut", "mahogany": "Mahogany",
    "weathered teak": "Weathered Teak", "american walnut": "American Walnut", "castle gate": "Castle Gate",
    "french white oak": "French White Oak", "brownstone": "Brownstone", "slate gray": "Slate Gray",
    "biscayne": "Biscayne", "carmel": "Carmel", "island mist": "Island Mist", "jasper": "Jasper",
    "rainier": "Rainier", "hatteras": "Hatteras", "salt flat": "Salt Flat", "honey grove": "Honey Grove",
    "tide pool": "Tide Pool", "cinnamon cove": "Cinnamon Cove", "golden hour": "Golden Hour",
    "pebble beach": "Pebble Beach", "malted barley": "Malted Barley", "millstone": "Millstone",
    "whiskey barrel": "Whiskey Barrel", "juniper": "Juniper"
}

def extract_attributes(part_desc: str, mfg_part_num: str, tax_res: dict) -> dict:
    """
    Extracts structured attributes from description and MPN.
    Returns: {
        'series': str,
        'model': str,
        'voltage': (val, uom),
        'amperage': (val, uom),
        'wattage': (val, uom),
        'mounting': str,
        'dimensions': str,
        'sound_level': (val, uom),
        'material': str,
        'color': str,
        'pack_qty': str,
        'grit': str,
        'teeth': str,
        'with_modifier': str,
        'additional_info': str,
        'features': list[str],
        'attribute_triplets': list[dict]
    }
    """
    text = f"{part_desc} {mfg_part_num}".strip()
    res = {
        'series': '',
        'model': mfg_part_num,
        'voltage': ('', ''),
        'amperage': ('', ''),
        'wattage': ('', ''),
        'mounting': '',
        'dimensions': '',
        'sound_level': ('', ''),
        'material': '',
        'color': '',
        'pack_qty': '',
        'grit': '',
        'teeth': '',
        'with_modifier': '',
        'additional_info': '',
        'features': [],
        'standards': ''
    }

    # 1. Series Extraction
    for s in KNOWN_SERIES:
        if re.search(rf"\b{re.escape(s)}\b", text, re.IGNORECASE):
            res['series'] = s
            break
    if not res['series']:
        if "pro" in text.lower() and "dishwasher" in text.lower():
            res['series'] = "Professional Series"
        elif "eco" in text.lower() and "dishwasher" in text.lower():
            res['series'] = "Eco Series"
        elif "m18" in text.lower():
            res['series'] = "M18™"
        elif "m12" in text.lower():
            res['series'] = "M12™"
        elif "20v" in text.lower() and "dewalt" in text.lower():
            res['series'] = "20V MAX*"

    # 2. Voltage (Extract ONLY if explicitly in text)
    volt_match = re.search(r'\b(\d+)\s*(?:V|VAC|VDC|Volt)\b', text, re.IGNORECASE)
    if volt_match:
        res['voltage'] = (volt_match.group(1), 'V')

    # 3. Amperage (Extract ONLY if explicitly in text)
    amp_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:A|Amp|Amps|Amperes)\b', text, re.IGNORECASE)
    if amp_match:
        res['amperage'] = (amp_match.group(1), 'A')

    # 4. Wattage (Extract ONLY if explicitly in text)
    watt_match = re.search(r'\b(\d+)\s*(?:W|Watt|Watts)\b', text, re.IGNORECASE)
    if watt_match:
        res['wattage'] = (watt_match.group(1), 'W')

    # 5. Sound Level (Extract ONLY if explicitly in text)
    sound_match = re.search(r'\b(\d+)\s*(?:dBA|db|decibel)\b', text, re.IGNORECASE)
    if sound_match:
        res['sound_level'] = (sound_match.group(1), 'dBA')

    # 6. Color & Material Extraction (Extract ONLY if in text)
    for k_col, canon_col in KNOWN_COLORS.items():
        if re.search(rf"\b{re.escape(k_col)}\b", text, re.IGNORECASE):
            res['color'] = canon_col
            if "stainless steel" in canon_col.lower():
                res['material'] = "Stainless Steel"
            break

    # 7. Mounting Type
    if re.search(r'\bbuilt[- ]?in\b', text, re.IGNORECASE):
        res['mounting'] = "Built-in"
    elif re.search(r'\bleg\b', text, re.IGNORECASE):
        res['mounting'] = "Leg"
    elif re.search(r'\bsq\s*edge\b', text, re.IGNORECASE):
        res['mounting'] = "Square Edge"
    elif re.search(r'\bgrooved\b', text, re.IGNORECASE):
        res['mounting'] = "Grooved"
    elif re.search(r'\bwall\b', text, re.IGNORECASE):
        res['mounting'] = "Wall"
    elif re.search(r'\bceiling\b', text, re.IGNORECASE):
        res['mounting'] = "Ceiling"

    # 8. Dimensions Extraction (Extract ONLY if in text)
    dim_match = re.search(r'(\d+(?:[-/.]\d+)?(?:\s*in|\"|\')?\s*x\s*\d+(?:[-/.]\d+)?(?:\s*in|\"|\')?(?:\s*x\s*\d+(?:[-/.]\d+)?(?:\s*in|\"|\')?)?)', text, re.IGNORECASE)
    if dim_match:
        res['dimensions'] = parse_dimension_string(dim_match.group(1))

    # 9. Grit & Teeth / TPI
    grit_match = re.search(r'\bP?(\d{2,4})\s*(?:Grit|P\d+)?\b', text, re.IGNORECASE)
    if grit_match and any(term in text.lower() for term in ['film', 'hiolit', 'abranet', 'sponge', 'sanding', 'disc', 'belt']):
        res['grit'] = f"P{grit_match.group(1)}"

    teeth_match = re.search(r'\b(\d{1,3})\s*(?:T|Teeth|Tooth|TPI)\b', text, re.IGNORECASE)
    if teeth_match:
        res['teeth'] = teeth_match.group(1)

    # 10. Pack Qty
    pack_match = re.search(r'\b(\d+)\s*(?:pc|pk|ct|pack|disc/box|piece|sheets/box)\b', text, re.IGNORECASE)
    if pack_match:
        res['pack_qty'] = pack_match.group(1)

    # 11. Modifiers & Features (Extract ONLY if mentioned in text)
    if "cleanboost" in text.lower():
        res['with_modifier'] = "With CleanBoost™"
    elif "3rd rack" in text.lower():
        res['with_modifier'] = "With Washing 3rd Rack"

    # Dynamic feature highlights based on real extracted attributes
    if res['series']:
        res['features'].append(f"{res['series']} construction")
    if res['dimensions']:
        res['features'].append(f"Dimensions: {res['dimensions']}")
    if res['voltage'][0]:
        res['features'].append(f"{res['voltage'][0]} {res['voltage'][1]} voltage rating")
    if res['amperage'][0]:
        res['features'].append(f"{res['amperage'][0]} {res['amperage'][1]} amperage rating")
    if res['sound_level'][0]:
        res['features'].append(f"{res['sound_level'][0]} {res['sound_level'][1]} sound level")
    if res['color']:
        res['features'].append(f"Finish: {res['color']}")
    if res['material']:
        res['features'].append(f"Material: {res['material']}")
    if res['teeth']:
        res['features'].append(f"{res['teeth']} Tooth Configuration")
    if res['grit']:
        res['features'].append(f"{res['grit']} Grit Abrasive")
    if res['pack_qty']:
        res['features'].append(f"{res['pack_qty']} Count Package")

    # Build the ATTRIBUTE triplets (up to 50)
    triplets = []
    if res['series']:
        triplets.append({'label': 'Series', 'value': res['series'], 'uom': ''})
    if res['model']:
        triplets.append({'label': 'Model', 'value': res['model'], 'uom': ''})
    if res['teeth']:
        triplets.append({'label': 'Number of Teeth', 'value': res['teeth'], 'uom': ''})
    if res['grit']:
        triplets.append({'label': 'Grit', 'value': res['grit'], 'uom': ''})
    if res['voltage'][0]:
        triplets.append({'label': 'Voltage Rating', 'value': res['voltage'][0], 'uom': res['voltage'][1]})
    if res['amperage'][0]:
        triplets.append({'label': 'Amperage Rating', 'value': res['amperage'][0], 'uom': res['amperage'][1]})
    if res['wattage'][0]:
        triplets.append({'label': 'Wattage', 'value': res['wattage'][0], 'uom': res['wattage'][1]})
    if res['mounting']:
        triplets.append({'label': 'Mounting Type', 'value': res['mounting'], 'uom': ''})
    if res['dimensions']:
        triplets.append({'label': 'Size', 'value': res['dimensions'], 'uom': ''})
    if res['sound_level'][0]:
        triplets.append({'label': 'Sound Level', 'value': res['sound_level'][0], 'uom': res['sound_level'][1]})
    if res['material']:
        triplets.append({'label': 'Material', 'value': res['material'], 'uom': ''})
    if res['color']:
        triplets.append({'label': 'Color', 'value': res['color'], 'uom': ''})
    if res['pack_qty']:
        triplets.append({'label': 'Package Quantity', 'value': res['pack_qty'], 'uom': 'pk'})

    res['attribute_triplets'] = triplets
    return res
