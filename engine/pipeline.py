"""
UniEnrich Master Pipeline Orchestrator
Transforms raw messy input rows into complete 252-column commerce-ready delivery records,
with automated external manufacturer web intelligence for sparse items.
"""
import os
import pandas as pd
from .sanitizer import sanitize_text, clean_placeholder
from .brand_resolver import resolve_brand
from .taxonomy_classifier import classify_product
from .attribute_extractor import extract_attributes
from .web_enricher import query_external_mfr_data
from .copy_synthesizer import (
    build_invoice_desc, build_mobile_desc, build_short_desc,
    build_long_desc, build_retail_desc
)
from .asset_mapper import map_digital_assets
from .explainability import generate_audit_trace

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# Load the exact 252 static headers
HEADERS_FILE = os.path.join(DATA_DIR, 'expected_output_headers.csv')
if os.path.exists(HEADERS_FILE):
    DELIVERY_HEADERS = pd.read_csv(HEADERS_FILE, nrows=0).columns.tolist()
else:
    DELIVERY_HEADERS = []

def enrich_single_record(raw: dict, enable_web_sourcing: bool = True) -> tuple[dict, dict]:
    """
    Enriches a single input dictionary into a 252-column delivery format record + audit trace.
    Supports dynamic live web sourcing for sparse industrial rows.
    """
    mfg_part_num = sanitize_text(str(raw.get('Mfg_Part_Num', raw.get('MANUFACTURER_PART_NUMBER', ''))))
    part_desc = sanitize_text(str(raw.get('Part_Desc', '')))
    e1_brand = clean_placeholder(str(raw.get('E1_Brand', '')))
    unilog_brand = clean_placeholder(str(raw.get('Unilog_Brand', '')))
    dib_brand = clean_placeholder(str(raw.get('DIB_Brand', '')))
    part_manuf = clean_placeholder(str(raw.get('Part_Manuf', '')))
    
    raw_dept = str(raw.get('Dept', ''))
    raw_class = str(raw.get('Class', ''))
    raw_fine = str(raw.get('Fine', ''))
    sku = str(raw.get('SKU - MY_PART_NUMBER', raw.get('PART_NUMBER', '')))

    # 1. Resolve Brand & Manufacturer
    brand_res = resolve_brand(e1_brand, unilog_brand, dib_brand, part_manuf, part_desc, mfg_part_num)
    mfg_name = brand_res.get('MANUFACTURER_NAME', '')
    brand_name = brand_res.get('BRAND_NAME', '')

    # 2. External Web Intelligence Query (if enabled and row is sparse)
    web_data = {"enriched_via_web": False}
    if enable_web_sourcing:
        web_data = query_external_mfr_data(mfg_part_num, part_desc, brand_name)

    # 3. Classify Taxonomy & UNSPSC
    tax_res = classify_product(part_desc, mfg_part_num, raw_dept, raw_class, raw_fine)

    # 4. Extract Attributes & UOMs
    attrs = extract_attributes(part_desc, mfg_part_num, tax_res)

    # Merge web-extracted specs into attrs if present
    if web_data.get("enriched_via_web"):
        for spec_k, spec_v in web_data.get("extracted_specs", {}).items():
            if spec_k == "Voltage" and not attrs['voltage'][0]:
                attrs['voltage'] = (spec_v.replace('V', '').strip(), 'V')
            elif spec_k == "Wattage" and not attrs['wattage'][0]:
                attrs['wattage'] = (spec_v.replace('W', '').strip(), 'W')
            elif spec_k == "Application":
                attrs['additional_info'] = f"Application: {spec_v}"
            # Add to attribute triplets
            attrs['attribute_triplets'].append({
                'label': spec_k,
                'value': spec_v.split()[0] if ' ' in spec_v else spec_v,
                'uom': spec_v.split()[-1] if ' ' in spec_v and len(spec_v.split()) > 1 else ''
            })

    # 5. Synthesize 5-Tier Descriptions
    invoice_desc = build_invoice_desc(tax_res['Product Name'], mfg_part_num, attrs)
    mobile_desc = build_mobile_desc(mfg_name, brand_name, tax_res['Product Name'], attrs['series'], mfg_part_num, attrs)
    short_desc = build_short_desc(brand_name, attrs['series'], mfg_part_num, tax_res['Product Name'], attrs['with_modifier'], attrs)
    long_desc = build_long_desc(brand_name, tax_res['Product Name'], attrs['with_modifier'], attrs['series'], mfg_part_num, attrs)
    retail_desc = build_retail_desc(attrs['series'], tax_res['Product Name'], attrs)

    # 6. Map Digital Assets
    assets = map_digital_assets(brand_name, mfg_part_num)

    # 7. Generate Explainability Trace
    descs = {
        'INVOICE_DESC': invoice_desc,
        'MOBILE_DESC': mobile_desc,
        'SHORT_DESC': short_desc,
        'LONG_DESC1': long_desc
    }
    audit = generate_audit_trace(raw, brand_res, tax_res, attrs, descs)
    
    # Inject Web Provenance into Audit Trace if retrieved
    if web_data.get("enriched_via_web"):
        audit["overall_confidence"] = min(1.0, audit["overall_confidence"] + 0.05)
        audit["provenance_trail"]["external_web_sourcing"] = {
            "source_url": web_data.get("source_url", ""),
            "external_title": web_data.get("external_title", ""),
            "evidence_snippet": web_data.get("raw_snippet", ""),
            "extracted_specs": web_data.get("extracted_specs", {})
        }
        audit["status"] = "VERIFIED"

    # 8. Assemble Complete 252-Column Dictionary
    record = {h: "" for h in DELIVERY_HEADERS}

    # Populate direct metadata & URLs
    record["MFR URL"] = web_data.get("source_url") or assets.get("MFR URL", "")
    if web_data.get("source_url"):
        record["Ref URL 1"] = web_data["source_url"]
    record["PART_NUMBER"] = sku or mfg_part_num
    record["Dept"] = tax_res.get("Dept", "")
    record["Class"] = tax_res.get("Class", "")
    record["Fine"] = tax_res.get("Fine", "")
    record["SKU - MY_PART_NUMBER"] = sku
    record["Mfg_Part_Num"] = mfg_part_num
    record["Part_Desc"] = part_desc
    record["E1_Brand"] = e1_brand or "-- Unbranded --"
    record["Unilog_Brand"] = unilog_brand or "-- No Unilog Brand --"
    record["DIB_Brand"] = dib_brand or "-- No DIB Brand --"
    record["Part_Manuf"] = part_manuf or mfg_name

    # Master Resolved Columns
    record["MANUFACTURER_NAME"] = mfg_name
    record["BRAND_NAME"] = brand_name
    record["MANUFACTURER_PART_NUMBER"] = mfg_part_num
    record["Classpath"] = tax_res.get("Classpath", "")

    # 5 Description Tiers
    record["MOBILE_DESC"] = mobile_desc
    record["INVOICE_DESC"] = invoice_desc
    record["SHORT_DESC"] = short_desc
    record["LONG_DESC1"] = long_desc
    record["RETAIL_DESC"] = retail_desc
    record["MARKETING_DESCRIPTION"] = web_data.get("raw_snippet", "")

    # Item Features (1..20)
    for idx, feat in enumerate(attrs.get('features', [])[:20], 1):
        record[f"ITEM_FEATURES_{idx}"] = feat

    # Modifiers & Standards
    record["With"] = attrs.get("with_modifier", "")
    record["Standard/Approvals"] = attrs.get("standards", "")
    record["Product Name"] = tax_res.get("Product Name", "")
    record["UNSPSC"] = tax_res.get("UNSPSC", "")

    # Attribute Triplets (1..50)
    for idx, trip in enumerate(attrs.get('attribute_triplets', [])[:50], 1):
        record[f"ATTRIBUTE_LABEL {idx}"] = trip.get('label', '')
        record[f"ATTRIBUTE_VALUE {idx}"] = trip.get('value', '')
        record[f"ATTRIBUTE_UOM {idx}"] = trip.get('uom', '')

    # Dimensions & Digital Assets
    record["Product Image"] = assets.get("Product Image", "")
    record["Alternate Image 1"] = assets.get("Alternate Image 1", "")
    record["Alternate Image 2"] = assets.get("Alternate Image 2", "")
    record["Alternate Image 3"] = assets.get("Alternate Image 3", "")
    record["Alternate Image 4"] = assets.get("Alternate Image 4", "")
    record["Specification Sheet"] = assets.get("Specification Sheet", "")
    record["Instruction/Installation Manual"] = assets.get("Instruction/Installation Manual", "")
    record["Owners/User Manual"] = assets.get("Owners/User Manual", "")
    record["Actual Image (Yes/No)"] = "Yes"

    return record, audit

def enrich_dataset(df_input: pd.DataFrame, enable_web_sourcing: bool = False) -> tuple[pd.DataFrame, list[dict]]:
    """
    Enriches an entire pandas DataFrame of input items into the 252-column delivery format.
    """
    rows_out = []
    audits = []
    
    for _, row in df_input.iterrows():
        row_dict = row.to_dict()
        rec, audit = enrich_single_record(row_dict, enable_web_sourcing=enable_web_sourcing)
        rows_out.append(rec)
        audits.append(audit)
        
    df_result = pd.DataFrame(rows_out)
    if DELIVERY_HEADERS:
        for col in DELIVERY_HEADERS:
            if col not in df_result.columns:
                df_result[col] = ""
        df_result = df_result[DELIVERY_HEADERS]
        
    return df_result, audits
