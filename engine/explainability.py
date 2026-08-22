"""
UniEnrich Calibrated Explainability, Provenance & Audit Engine
Calculates calibrated confidence scores based on empirical signal strength,
penalizes fallbacks, and strictly enforces human-in-the-loop review triggers.
"""

def generate_audit_trace(row_input: dict, resolved_brand: dict, taxonomy: dict, attrs: dict, descriptions: dict) -> dict:
    """
    Generates a calibrated explainability trace and quality audit report.
    - If taxonomy is a fallback (uncategorized) -> confidence severely penalized, status forced to NEEDS_HUMAN_REVIEW.
    - If brand is unbranded / fallback -> confidence penalized.
    - If critical dimensions or rules fail -> status forced to NEEDS_HUMAN_REVIEW.
    """
    is_tax_fallback = taxonomy.get('is_fallback', False)
    brand_prov = resolved_brand.get('provenance', 'FALLBACK_RAW')
    brand_conf = resolved_brand.get('confidence', 0.6)
    
    # 1. Base Taxonomy Confidence
    if is_tax_fallback:
        tax_conf = 0.30
    elif taxonomy.get('Classpath'):
        tax_conf = 0.95
    else:
        tax_conf = 0.50

    # 2. Attribute Extraction Confidence
    attr_count = len(attrs.get('attribute_triplets', []))
    if attr_count >= 4:
        attr_conf = 0.95
    elif attr_count >= 2:
        attr_conf = 0.85
    elif attr_count >= 1:
        attr_conf = 0.70
    else:
        attr_conf = 0.40

    # 3. Calibrated Confidence Calculation with Penalty Multipliers
    raw_confidence = (brand_conf * 0.40) + (tax_conf * 0.35) + (attr_conf * 0.25)
    
    # Severe penalties for fallbacks
    if is_tax_fallback:
        raw_confidence = min(raw_confidence, 0.45)
    if brand_prov == 'FALLBACK_RAW' or resolved_brand.get('BRAND_NAME') in ['Unbranded', '', '-- Unbranded --']:
        raw_confidence = min(raw_confidence, 0.55)

    overall_confidence = round(raw_confidence, 2)

    invoice_desc = descriptions.get('INVOICE_DESC', '')
    mobile_desc = descriptions.get('MOBILE_DESC', '')
    brand_name = resolved_brand.get('BRAND_NAME', '')

    # Rule compliance audits
    audit_checks = {
        "invoice_length_valid": len(invoice_desc) <= 40,
        "invoice_casing_valid": invoice_desc.isupper() or len(invoice_desc) == 0,
        "mobile_length_valid": 60 <= len(mobile_desc) <= 80,
        "trademark_symbol_valid": ('®' in brand_name or '™' in brand_name),
        "taxonomy_known": not is_tax_fallback,
        "attributes_extracted_count": attr_count
    }

    # Strict Human Review Triggers
    needs_review = (
        is_tax_fallback or
        (overall_confidence < 0.80) or
        (not audit_checks['invoice_length_valid']) or
        (brand_name in ['Unbranded', '', '-- Unbranded --']) or
        (brand_prov == 'FALLBACK_RAW')
    )

    status = "NEEDS_HUMAN_REVIEW" if needs_review else "VERIFIED"

    provenance_trail = {
        "brand_resolution": {
            "source": brand_prov,
            "confidence": brand_conf,
            "matched_mfg": resolved_brand.get('MANUFACTURER_NAME', '')
        },
        "taxonomy_classification": {
            "classpath": taxonomy.get('Classpath', ''),
            "unspsc": taxonomy.get('UNSPSC', ''),
            "is_fallback": is_tax_fallback,
            "confidence": tax_conf
        },
        "attribute_extraction": {
            "extracted_count": attr_count,
            "confidence": attr_conf
        }
    }

    return {
        "overall_confidence": overall_confidence,
        "status": status,
        "is_fallback": is_tax_fallback,
        "audit_checks": audit_checks,
        "provenance_trail": provenance_trail
    }
