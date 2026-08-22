"""
UniEnrich Digital Asset & Documentation Schema Mapper
Generates standardized digital asset filenames following Unilog content guidelines.
Zero speculative URL guessing: URLs are populated ONLY when grounded or verified via live web sourcing.
Actual Image presence is strictly reported as 'No' unless physically verified.
"""
import re

def clean_brand_for_filename(brand_name: str) -> str:
    """Strips legal symbols and spaces for asset filenames (e.g. 'FRIGIDAIRE®' -> 'FRIGIDAIRE')."""
    if not brand_name or brand_name in ["Unbranded", "-- Unbranded --"]:
        return "PRODUCT"
    s = brand_name.replace('®', '').replace('™', '').strip()
    s = re.sub(r'[^A-Za-z0-9_-]', '_', s)
    return s.strip('_')

def map_digital_assets(brand_name: str, mpn: str, verified_image_url: str = "", verified_source_url: str = "") -> dict:
    """
    Constructs standardized asset filenames according to Unilog catalog specifications.
    Does NOT invent fake URLs or claim image existence without verification.
    """
    clean_brand = clean_brand_for_filename(brand_name)
    clean_mpn = re.sub(r'[^A-Za-z0-9_-]', '_', (mpn or "").strip())
    
    if clean_mpn:
        base_name = f"{clean_brand}_{clean_mpn}"
        return {
            "MFR URL": verified_source_url,
            "Product Image": f"{base_name}.jpg",
            "Alternate Image 1": f"{base_name}_1.jpg",
            "Alternate Image 2": f"{base_name}_2.jpg",
            "Alternate Image 3": f"{base_name}_3.jpg",
            "Alternate Image 4": f"{base_name}_4.jpg",
            "Specification Sheet": f"{base_name}_Specification_Sheet.pdf",
            "Instruction/Installation Manual": f"{base_name}_Installation_Instructions.pdf",
            "Owners/User Manual": f"{base_name}_Owners_Manual.pdf",
            "Actual Image (Yes/No)": "Yes" if verified_image_url else "No"
        }
    else:
        return {
            "MFR URL": verified_source_url,
            "Product Image": "",
            "Alternate Image 1": "",
            "Alternate Image 2": "",
            "Alternate Image 3": "",
            "Alternate Image 4": "",
            "Specification Sheet": "",
            "Instruction/Installation Manual": "",
            "Owners/User Manual": "",
            "Actual Image (Yes/No)": "No"
        }
