"""
UniEnrich Multi-Factor Confidence, Provenance & Audit Engine
Calculates empirical signal-weighted confidence scores based on underlying classifier
metrics, penalizes fallbacks, and strictly enforces human-in-the-loop review triggers.
"""

def generate_audit_trace(row_input: dict, resolved_brand: dict, taxonomy: dict, attrs: dict, descriptions: dict) -> dict:
    """
    Generates an empirical explainability trace and quality audit report.
    Directly consumes empirical confidence scores from:
    1. Brand Resolver (Exact Alias = 1.0, Fuzzy = token_set_ratio, Fallback = 0.50)
    2. Taxonomy Classifier (Regex Specificity Score or TF-IDF Cosine Similarity)
    3. Grounded Attribute Extraction (Verified feature count)
    """
    is_tax_fallback = taxonomy.get('is_fallback', False)
    brand_prov = resolved_brand.get('provenance', 'FALLBACK_RAW')
    brand_conf = resolved_brand.get('confidence', 0.50)
    
    # 1. Base Taxonomy Confidence (Read directly from underlying classifier's own empirical score!)
    tax_conf = taxonomy.get('confidence', 0.35 if is_tax_fallback else 0.80)

    # 2. Attribute Extraction Confidence (Proportional to verified grounded features)
    attr_count = len(attrs.get('attribute_triplets', []))
    if attr_count >= 4:
        attr_conf = 0.95
    elif attr_count >= 2:
        attr_conf = 0.85
    elif attr_count >= 1:
        attr_conf = 0.70
    else:
        attr_conf = 0.40

    # 3. Calibrated Empirical Confidence Calculation: Multi-factor weighted formula
    raw_confidence = (brand_conf * 0.40) + (tax_conf * 0.40) + (attr_conf * 0.20)
    
    # Severe penalties for fallbacks
    if is_tax_fallback:
        raw_confidence = min(raw_confidence, 0.45)
    if brand_prov == 'FALLBACK_RAW' or resolved_brand.get('BRAND_NAME') in ['Unbranded', '', '-- Unbranded --']:
        raw_confidence = min(raw_confidence, 0.50)

    from .trust_engine import calibrate_confidence_score
    overall_confidence = calibrate_confidence_score(raw_confidence)

    invoice_desc = descriptions.get('INVOICE_DESC', '')
    mobile_desc = descriptions.get('MOBILE_DESC', '')
    brand_name = resolved_brand.get('BRAND_NAME', '')

    # Rule compliance audits
    audit_checks = {
        "invoice_length_valid": len(invoice_desc) <= 40,
        "invoice_casing_valid": invoice_desc.isupper() or len(invoice_desc) == 0,
        "mobile_length_valid": len(mobile_desc) <= 80,
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
            "resolved_manufacturer": resolved_brand.get('MANUFACTURER_NAME', ''),
            "resolved_brand": brand_name
        },
        "taxonomy_classification": {
            "source": taxonomy.get('provenance', 'DETERMINISTIC_RULES'),
            "confidence": tax_conf,
            "product_type": taxonomy.get('Product Name', ''),
            "assigned_classpath": taxonomy.get('Classpath', ''),
            "assigned_unspsc": taxonomy.get('UNSPSC', '')
        },
        "attribute_extraction": {
            "extracted_count": attr_count,
            "confidence": attr_conf,
            "extracted_labels": [t['label'] for t in attrs.get('attribute_triplets', [])]
        }
    }

    return {
        "status": status,
        "overall_confidence": overall_confidence,
        "is_fallback": is_tax_fallback,
        "audit_checks": audit_checks,
        "provenance_trail": provenance_trail
    }
