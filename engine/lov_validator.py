"""
UniEnrich Strict LOV (List of Values) & Controlled-Value Enforcement Gate
Implements the final validation, canonicalization, and review-routing gate:
1. Category / Classpath LOV Validation against data/category_lovs.json.
2. Brand & Manufacturer Canonicalization against data/master_brands.json.
3. Unit of Measure (UOM) Validation & Alias Normalization against data/uom_standards.json.
4. Decimal-to-Fraction Standardization against data/decimal_fraction.json.
5. Manufacturer URL & Sourcing Integrity Validation (Distributor != Manufacturer).
6. Hard Character Ceiling & Schema Integrity Enforcement (Exact 252 Columns).
"""
import os
import json
import re
import pandas as pd
from .uom_normalizer import decimal_to_fraction

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# Load Reference LOVs
with open(os.path.join(DATA_DIR, 'category_lovs.json'), 'r', encoding='utf-8') as f:
    CATEGORY_LOVS = json.load(f)

with open(os.path.join(DATA_DIR, 'master_brands.json'), 'r', encoding='utf-8') as f:
    MASTER_BRANDS = json.load(f)

with open(os.path.join(DATA_DIR, 'uom_standards.json'), 'r', encoding='utf-8') as f:
    UOM_DATA = json.load(f)

HEADERS_FILE = os.path.join(DATA_DIR, 'expected_output_headers.csv')
if os.path.exists(HEADERS_FILE):
    DELIVERY_HEADERS = pd.read_csv(HEADERS_FILE, nrows=0).columns.tolist()
else:
    DELIVERY_HEADERS = []

APPROVED_UOMS = set(UOM_DATA.get('approved_units', []))
UOM_ALIASES = {k.lower(): v for k, v in UOM_DATA.get('unit_aliases', {}).items()}

BRAND_ALIASES = {k.lower().strip(): v for k, v in MASTER_BRANDS.get('aliases', {}).items()}
CANONICAL_BRANDS = MASTER_BRANDS.get('canonical', {})

# Precompute approved categories mapping
# Maps normalized classpath / product type / cat key to approved category dictionary
APPROVED_CATEGORIES_BY_PATH = {}
APPROVED_CATEGORIES_BY_TYPE = {}
APPROVED_CATEGORIES_BY_KEY = {}

for cat_k, cat_data in CATEGORY_LOVS.items():
    APPROVED_CATEGORIES_BY_KEY[cat_k.lower()] = cat_data
    if 'classpath' in cat_data:
        APPROVED_CATEGORIES_BY_PATH[cat_data['classpath'].lower().strip()] = cat_data
    if 'product_type' in cat_data:
        APPROVED_CATEGORIES_BY_TYPE[cat_data['product_type'].lower().strip()] = cat_data

DISTRIBUTOR_DOMAINS = {
    "grainger.com", "mscdirect.com", "fastenal.com", "homedepot.com",
    "lowes.com", "amazon.com", "ebay.com", "walmart.com", "zoro.com", "ferguson.com"
}

class LOVValidatorGate:
    """
    Final Validation and Normalization Gate for UniEnrich Catalog Records.
    Ensures 100% constrained, compliant, non-fabricated product intelligence.
    """

    @classmethod
    def normalize_uom(cls, raw_uom: str) -> tuple[str, bool, bool]:
        """
        Validates and canonicalizes a Unit of Measure.
        Returns: (canonical_uom, is_valid, was_canonicalized)
        """
        if not raw_uom or not str(raw_uom).strip():
            return "", True, False

        clean_uom = str(raw_uom).strip()
        
        # Exact match in approved units
        if clean_uom in APPROVED_UOMS:
            return clean_uom, True, False

        # Match in aliases (case-insensitive)
        clean_lower = clean_uom.lower()
        if clean_lower in UOM_ALIASES:
            canonical = UOM_ALIASES[clean_lower]
            return canonical, True, True

        # Punctuation stripped check
        stripped = re.sub(r'[^a-zA-Z0-9]', '', clean_lower)
        if stripped in UOM_ALIASES:
            return UOM_ALIASES[stripped], True, True

        # Unapproved / invalid UOM
        return "", False, False

    @classmethod
    def validate_category(cls, classpath: str, product_type: str) -> tuple[dict | None, bool]:
        """
        Validates category/classpath against approved Category LOVs.
        Returns: (matched_category_dict, is_approved)
        """
        clean_path = (classpath or "").strip().lower()
        clean_type = (product_type or "").strip().lower()

        # 1. Exact classpath lookup
        if clean_path in APPROVED_CATEGORIES_BY_PATH:
            return APPROVED_CATEGORIES_BY_PATH[clean_path], True

        # 2. Product type lookup
        if clean_type in APPROVED_CATEGORIES_BY_TYPE:
            return APPROVED_CATEGORIES_BY_TYPE[clean_type], True

        # 3. Normalized path partial matching
        for path_key, cat_val in APPROVED_CATEGORIES_BY_PATH.items():
            if clean_type and clean_type in path_key:
                return cat_val, True
            if clean_path and (path_key in clean_path or clean_path in path_key):
                return cat_val, True

        return None, False

    @classmethod
    def validate_brand_and_mfr(cls, raw_brand: str, raw_mfr: str, part_desc: str = "") -> tuple[str, str, str, bool, bool]:
        """
        Validates and canonicalizes brand and manufacturer against Master Brands.
        Returns: (canonical_brand, canonical_mfr, provenance, is_valid, was_canonicalized)
        """
        clean_b = (raw_brand or "").strip()
        clean_m = (raw_mfr or "").strip()

        # Check for placeholder brand
        if clean_b in ["-- Unbranded --", "-- No Unilog Brand --", "-- No DIB Brand --", "Unbranded", ""]:
            # Check if brand is deterministically resolvable from manufacturer or description
            m_lower = clean_m.lower()
            for alias, canon_key in BRAND_ALIASES.items():
                if len(alias) >= 3 and (alias in m_lower or (part_desc and alias in part_desc.lower())):
                    canon = CANONICAL_BRANDS.get(canon_key, {})
                    b_name = canon.get("brand_name", f"{canon_key}®")
                    m_name = canon.get("mfg_name", clean_m)
                    return b_name, m_name, "LOV_CANONICAL_RESOLVED", True, True

            return "-- Unbranded --", clean_m or "Unknown", "UNBRANDED_CONFIRMED", True, False

        # Direct canonical match
        for canon_k, canon_v in CANONICAL_BRANDS.items():
            if clean_b == canon_v.get("brand_name") or clean_b.replace('®', '').replace('™', '').strip().lower() == canon_k.lower():
                return canon_v.get("brand_name"), canon_v.get("mfg_name", clean_m), "LOV_CANONICAL_EXACT", True, False

        # Alias lookup
        b_lower = clean_b.replace('®', '').replace('™', '').strip().lower()
        if b_lower in BRAND_ALIASES:
            canon_k = BRAND_ALIASES[b_lower]
            canon = CANONICAL_BRANDS.get(canon_k, {})
            return canon.get("brand_name", f"{canon_k}®"), canon.get("mfg_name", clean_m), "LOV_ALIAS_CANONICALIZED", True, True

        # Unresolved brand
        return clean_b, clean_m, "UNRESOLVED_FREEFORM", False, False

    @classmethod
    def validate_and_normalize_record(cls, record: dict, audit: dict, raw_input: dict | None = None) -> tuple[dict, dict, dict]:
        """
        Executes the entire final validation and normalization gate across a 252-column record.
        Returns: (validated_record, updated_audit, validation_stats)
        """
        raw = raw_input or {}
        val_stats = {
            "category_valid": False,
            "category_canonicalized": False,
            "brand_valid": False,
            "brand_canonicalized": False,
            "mfr_valid": False,
            "uom_checks_total": 0,
            "uom_checks_valid": 0,
            "uom_checks_canonicalized": 0,
            "uom_checks_invalid": 0,
            "manufacturer_source_verified": False,
            "distributor_source_rerouted": False
        }

        # 1. Category & Classpath LOV Validation
        cat_match, cat_ok = cls.validate_category(record.get("Classpath", ""), record.get("Product Name", ""))
        if cat_ok and cat_match:
            record["Dept"] = cat_match.get("dept", record.get("Dept", ""))
            record["Class"] = cat_match.get("class", record.get("Class", ""))
            record["Fine"] = cat_match.get("fine", record.get("Fine", ""))
            record["Classpath"] = cat_match.get("classpath", record.get("Classpath", ""))
            record["UNSPSC"] = cat_match.get("unspsc", record.get("UNSPSC", ""))
            record["Product Name"] = cat_match.get("product_type", record.get("Product Name", ""))
            val_stats["category_valid"] = True
            val_stats["category_canonicalized"] = True
        else:
            val_stats["category_valid"] = False
            audit["is_fallback"] = True
            audit["category_lov_unresolved"] = True

        # 2. Brand & Manufacturer LOV Validation
        part_desc = record.get("Part_Desc", raw.get("Part_Desc", ""))
        canon_b, canon_m, b_prov, b_ok, b_canon = cls.validate_brand_and_mfr(
            record.get("BRAND_NAME", ""),
            record.get("MANUFACTURER_NAME", record.get("Part_Manuf", "")),
            part_desc
        )
        if b_ok:
            record["BRAND_NAME"] = canon_b
            record["MANUFACTURER_NAME"] = canon_m
        else:
            # Reject invalid freeform brand value -> never silently invent/keep free-form value
            record["BRAND_NAME"] = "-- Unbranded --"
            record["MANUFACTURER_NAME"] = canon_m or "Unknown"
            audit["brand_lov_unresolved"] = True

        val_stats["brand_valid"] = b_ok
        val_stats["brand_canonicalized"] = b_canon
        val_stats["mfr_valid"] = bool(canon_m and canon_m != "Unknown")

        # 3. UOM Validation across standard UOM columns
        uom_fields = ["Selling UOM", "LENGTH_UOM", "HEIGHT_UOM", "WIDTH_UOM", "WEIGHT_UOM", "VOLUME_UOM"]
        for u_col in uom_fields:
            if u_col in record and record[u_col]:
                val_stats["uom_checks_total"] += 1
                c_uom, is_v, was_c = cls.normalize_uom(record[u_col])
                if is_v:
                    record[u_col] = c_uom
                    val_stats["uom_checks_valid"] += 1
                    if was_c:
                        val_stats["uom_checks_canonicalized"] += 1
                else:
                    record[u_col] = ""
                    val_stats["uom_checks_invalid"] += 1

        # 4. Attribute Triplets UOM & Value Decimal-to-Fraction Validation (1 to 50)
        for idx in range(1, 51):
            val_k = f"ATTRIBUTE_VALUE {idx}"
            uom_k = f"ATTRIBUTE_UOM {idx}"
            lbl_k = f"ATTRIBUTE_LABEL {idx}"

            # Format fractions in numeric attribute values
            if val_k in record and record[val_k]:
                record[val_k] = decimal_to_fraction(record[val_k])

            # Enforce LOV on attribute UOMs
            if uom_k in record and record[uom_k]:
                val_stats["uom_checks_total"] += 1
                c_uom, is_v, was_c = cls.normalize_uom(record[uom_k])
                if is_v:
                    record[uom_k] = c_uom
                    val_stats["uom_checks_valid"] += 1
                    if was_c:
                        val_stats["uom_checks_canonicalized"] += 1
                else:
                    record[uom_k] = ""
                    val_stats["uom_checks_invalid"] += 1

        # 5. Manufacturer Sourcing & Evidence Integrity
        mfr_url = str(record.get("MFR URL", "")).strip()
        if mfr_url:
            is_distributor = any(d in mfr_url.lower() for d in DISTRIBUTOR_DOMAINS)
            if is_distributor:
                # Never present distributor as manufacturer evidence!
                record["MFR URL"] = ""
                if not record.get("Ref URL 1"):
                    record["Ref URL 1"] = mfr_url
                val_stats["distributor_source_rerouted"] = True
            else:
                val_stats["manufacturer_source_verified"] = True

        # 6. Strict Description Constraints
        inv_desc = str(record.get("INVOICE_DESC", ""))
        if len(inv_desc) > 40 or not inv_desc.isupper():
            record["INVOICE_DESC"] = inv_desc[:40].upper()

        mob_desc = str(record.get("MOBILE_DESC", ""))
        if len(mob_desc) > 80:
            record["MOBILE_DESC"] = mob_desc[:80]

        # 7. Final Review Decision & Confidence Guardrails
        needs_review = (
            not val_stats["category_valid"] or
            (not val_stats["brand_valid"] and record.get("BRAND_NAME") not in ["-- Unbranded --", "Unbranded"]) or
            audit.get("is_fallback", False) or
            float(audit.get("overall_confidence", 0.0)) < 0.70
        )

        if needs_review:
            audit["status"] = "NEEDS_HUMAN_REVIEW"
            audit["readiness_tier"] = "TIER_C_MANDATORY_REVIEW"
            audit["overall_confidence"] = min(float(audit.get("overall_confidence", 0.70)), 0.65)
        elif float(audit.get("overall_confidence", 0.0)) >= 0.85 and val_stats["category_valid"] and val_stats["brand_valid"]:
            audit["status"] = "VERIFIED"
            audit["readiness_tier"] = "TIER_A_DIRECT_PUBLICATION"
        else:
            audit["status"] = "ASSISTED_REVIEW"
            audit["readiness_tier"] = "TIER_B_ASSISTED_REVIEW"

        # 8. Exact 252-Column Output Alignment
        validated_record = {}
        for h in DELIVERY_HEADERS:
            validated_record[h] = record.get(h, "")

        audit["lov_validation"] = val_stats
        return validated_record, audit, val_stats
