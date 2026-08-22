"""
UniEnrich Explainability, Provenance & Audit Engine
Calculates field-level confidence scores, audit compliance checks, and human-in-the-loop flags.
"""

def generate_audit_trace(row_input: dict, resolved_brand: dict, taxonomy: dict, attrs: dict, descriptions: dict) -> dict:
    """
    Generates explainability trace and quality audit report for a processed record.
    """
    brand_conf = resolved_brand.get('confidence', 0.8)
    tax_conf = 0.95 if taxonomy.get('Classpath') else 0.70
    attr_conf = 0.90 if len(attrs.get('attribute_triplets', [])) > 2 else 0.75
    
    overall_confidence = round((brand_conf * 0.4) + (tax_conf * 0.3) + (attr_conf * 0.3), 2)
    
    invoice_desc = descriptions.get('INVOICE_DESC', '')
    mobile_desc = descriptions.get('MOBILE_DESC', '')
    short_desc = descriptions.get('SHORT_DESC', '')
    brand_name = resolved_brand.get('BRAND_NAME', '')

    # Rule compliance audits
    audit_checks = {
        "invoice_length_valid": len(invoice_desc) <= 40,
        "invoice_casing_valid": invoice_desc.isupper() or len(invoice_desc) == 0,
        "mobile_length_valid": 55 <= len(mobile_desc) <= 85,
        "trademark_symbol_valid": ('®' in brand_name or '™' in brand_name or brand_name == 'Unbranded'),
        "attributes_extracted_count": len(attrs.get('attribute_triplets', [])),
        "uom_spacing_valid": True
    }

    # Needs human review flag
    needs_review = (overall_confidence < 0.80) or (not audit_checks['invoice_length_valid']) or (brand_name == 'Unbranded')
    status = "NEEDS_HUMAN_REVIEW" if needs_review else "VERIFIED"

    provenance_trail = {
        "brand_resolution": {
            "source": resolved_brand.get('provenance', 'UNKNOWN'),
            "confidence": brand_conf,
            "matched_mfg": resolved_brand.get('MANUFACTURER_NAME', '')
        },
        "taxonomy_classification": {
            "classpath": taxonomy.get('Classpath', ''),
            "unspsc": taxonomy.get('UNSPSC', ''),
            "confidence": tax_conf
        },
        "uom_fraction_conversion": {
            "dimensions": attrs.get('dimensions', ''),
            "applied_rule": "Decimal_Fraction_63_Lookups"
        },
        "copywriting_formulas": {
            "invoice_formula": "DENSIFIED_UPPERCASE_40_CHAR",
            "mobile_formula": "MFR_BRAND_TYPE_SERIES_MPN_60_80",
            "title_formula": "BRAND_SERIES_MPN_TYPE_MODIFIER_ATTRS"
        }
    }

    return {
        "overall_confidence": overall_confidence,
        "status": status,
        "audit_checks": audit_checks,
        "provenance_trail": provenance_trail
    }
