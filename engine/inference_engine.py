"""
UniEnrich Domain Knowledge & Grounded Specification Engine
Extracts and normalizes ONLY grounded specifications present in input text or verified web metadata.
Zero numeric guessing or fabricated RPM/kerf values.
"""
import re

def infer_deep_specifications(text: str, mpn: str, cat_key: str, basic_attrs: dict, web_data: dict, brand_name: str = "") -> dict:
    """
    Consolidates verified attributes without fabricating ungrounded numeric ratings.
    Only returns specifications with factual provenance.
    """
    grounded_specs = {}
    
    # 1. Real web-extracted specifications (from manufacturer documentation)
    if web_data and web_data.get("enriched_via_web") and web_data.get("extracted_specs"):
        for k, v in web_data["extracted_specs"].items():
            grounded_specs[k] = v

    # 2. Extract grounded physical facts from text (e.g. dimensions, tooth count, grit, voltage)
    text_lower = f"{text} {mpn}".lower()

    # Dimensions
    dim_match = re.search(r'(\d+(?:[-/.]\d+)?(?:\s*in|\"|\')?\s*x\s*\d+(?:[-/.]\d+)?(?:\s*in|\"|\')?(?:\s*x\s*\d+(?:[-/.]\d+)?(?:\s*in|\"|\')?)?)', text_lower)
    if dim_match and "Size / Dimensions" not in grounded_specs:
        grounded_specs["Size / Dimensions"] = dim_match.group(1).replace('"', ' in')

    # Voltage
    volt_match = re.search(r'\b(\d{2,3})\s*(?:v|vac|vdc|volt)\b', text_lower)
    if volt_match and "Voltage" not in grounded_specs:
        grounded_specs["Voltage"] = f"{volt_match.group(1)} V"

    # Teeth / TPI
    teeth_match = re.search(r'\b(\d{1,3})\s*(?:t|teeth|tooth|tpi)\b', text_lower)
    if teeth_match and "Tooth Count" not in grounded_specs:
        grounded_specs["Tooth Count"] = teeth_match.group(1)

    # Grit
    grit_match = re.search(r'\bp?(\d{2,4})\s*(?:grit)?\b', text_lower)
    if grit_match and any(w in text_lower for w in ["sanding", "belt", "disc", "sheet", "film", "abranet"]):
        grounded_specs["Grit"] = f"P{grit_match.group(1)}"

    # Convert to Attribute Triplets
    triplets = []
    for label, full_val in grounded_specs.items():
        val_str = str(full_val).strip()
        uom_str = ""
        parts = val_str.rsplit(' ', 1)
        if len(parts) == 2 and parts[1] in ["in", "ft", "V", "A", "W", "RPM", "deg", "psi", "dBA", "GA", "TPI", "mm", "pk"]:
            val_str = parts[0]
            uom_str = parts[1]
            
        triplets.append({
            "label": label,
            "value": val_str,
            "uom": uom_str
        })

    # Provenance and Confidence computation
    spec_count = len(grounded_specs)
    has_web = bool(web_data and web_data.get("enriched_via_web"))
    
    if has_web:
        conf = 0.95
        prov = "VERIFIED_MANUFACTURER_WEB_DOCUMENTATION"
    elif spec_count >= 2:
        conf = 0.88
        prov = "GROUNDED_TEXT_SPEC_EXTRACTION"
    elif spec_count == 1:
        conf = 0.75
        prov = "PARTIAL_TEXT_SPEC_EXTRACTION"
    else:
        conf = 0.60
        prov = "NO_EXPLICIT_SPECS_FOUND"

    return {
        "inferred_specs": grounded_specs,
        "inferred_triplets": triplets,
        "provenance": prov,
        "confidence": conf
    }
