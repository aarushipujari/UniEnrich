"""
UniEnrich Digital Asset & Documentation Mapper
Formats product image filenames, manual URLs, and specification sheets according to Unilog standards.
"""
import re

def clean_brand_for_filename(brand_name: str) -> str:
    """Strips legal symbols and spaces for asset filenames (e.g. 'FRIGIDAIRE®' -> 'FRIGIDAIRE')."""
    if not brand_name:
        return "PRODUCT"
    s = brand_name.replace('®', '').replace('™', '').strip()
    s = re.sub(r'[^A-Za-z0-9_-]', '_', s)
    return s.strip('_')

def map_digital_assets(brand_name: str, mpn: str) -> dict:
    """
    Constructs canonical asset filenames and documentation references.
    """
    clean_brand = clean_brand_for_filename(brand_name)
    clean_mpn = re.sub(r'[^A-Za-z0-9_-]', '_', mpn.strip())
    
    base_name = f"{clean_brand}_{clean_mpn}"
    
    # Specific MFR URL domain heuristics
    b_lower = clean_brand.lower()
    if "frigidaire" in b_lower:
        mfr_url = f"https://www.frigidaire.com/en/p/owner-center/product-support/{mpn}"
    elif "whirlpool" in b_lower:
        mfr_url = f"https://learnwhirlpool.com/smartsearchresults?searchtext={mpn}"
    elif "dewalt" in b_lower:
        mfr_url = f"https://www.dewalt.com/product/{mpn.lower()}"
    elif "milwaukee" in b_lower:
        mfr_url = f"https://www.milwaukeetool.com/Products/{mpn}"
    elif "makita" in b_lower:
        mfr_url = f"https://www.makitatools.com/products/details/{mpn}"
    elif "diablo" in b_lower:
        mfr_url = f"https://www.diablotools.com/products/{mpn}"
    else:
        mfr_url = f"https://www.{b_lower}.com/product/{mpn}"

    return {
        "MFR URL": mfr_url,
        "Product Image": f"{base_name}.jpg",
        "Alternate Image 1": f"{base_name}_1.jpg",
        "Alternate Image 2": f"{base_name}_2.jpg",
        "Alternate Image 3": f"{base_name}_3.jpg",
        "Alternate Image 4": f"{base_name}_4.jpg",
        "Specification Sheet": f"{base_name}_Specification_Sheet.pdf",
        "Instruction/Installation Manual": f"{base_name}_Installation_Instructions.pdf",
        "Owners/User Manual": f"{base_name}_Owners_Manual.pdf",
        "Actual Image (Yes/No)": "Yes"
    }
