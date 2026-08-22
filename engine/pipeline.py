"""
UniEnrich Master Pipeline Orchestrator
Neuro-Symbolic Architecture: AI Cognitive Reasoning Engine + Deterministic Safety Rails

Pipeline Cascade:
  Input (Sparse/Messy Supplier Record)
    ↓
  Stage 1: AI Research & Discovery Agent (Manufacturer Evidence Retrieval)
    ↓
  Stage 2: AI Cognitive Reasoning Engine (LLM / Scikit-Learn TF-IDF N-Gram Vectorizer)
    ↓
  Stage 3: Deep Physical Specification Inference (Factual Knowledge Grounding)
    ↓
  Stage 4: Deterministic Industrial Safety Rails (LOV Table, Master UOM, Hard Character Ceilings)
    ↓
  Stage 5: Multi-Channel Commerce Copywriting Synthesis (Unilog Formula Standards)
    ↓
  Stage 6: Explainability, Cell-Level Provenance & Human-in-the-Loop Governance
    ↓
  Output: 252-Column Commerce-Ready Product Intelligence
"""
import os
import pandas as pd
from .sanitizer import sanitize_text, clean_placeholder
from .brand_resolver import resolve_brand
from .taxonomy_classifier import classify_product
from .attribute_extractor import extract_attributes
from .web_enricher import query_external_mfr_data
from .research_agent import query_agentic_research
from .inference_engine import infer_deep_specifications
from .ai_agent import run_generative_enrichment
from .copy_synthesizer import (
    build_invoice_desc, build_mobile_desc, build_short_desc,
    build_long_desc, build_retail_desc
)
from .asset_mapper import map_digital_assets
from .explainability import generate_audit_trace

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

HEADERS_FILE = os.path.join(DATA_DIR, 'expected_output_headers.csv')
if os.path.exists(HEADERS_FILE):
    DELIVERY_HEADERS = pd.read_csv(HEADERS_FILE, nrows=0).columns.tolist()
else:
    DELIVERY_HEADERS = []

def enrich_single_record(raw: dict, enable_web_sourcing: bool = True, enable_ai_reasoning: bool = True) -> tuple[dict, dict]:
    """
    Transforms a single messy input row into a 252-column delivery format record + audit trace
    via the 7-stage Neuro-Symbolic Cognitive Architecture:
    AI Discovery & Reasoning -> Evidence Verification -> Deterministic Industrial Safety Rails.
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

    # Stage 1: AI Cognitive Brand & Entity Discovery
    brand_res = resolve_brand(e1_brand, unilog_brand, dib_brand, part_manuf, part_desc, mfg_part_num)
    mfg_name = brand_res.get('MANUFACTURER_NAME', '')
    brand_name = brand_res.get('BRAND_NAME', '')

    # Stage 2: Autonomous Agentic Research Loop (Manufacturer Sourcing & Evidence Retrieval)
    research_data = {"is_verified": False, "mfr_url": "", "ref_url_1": "", "extracted_specs": {}, "provenance": "LOCAL_GROUNDING"}
    if enable_web_sourcing:
        research_data = query_agentic_research(mfg_part_num, part_desc, brand_name)

    # Legacy adapter compatibility
    web_data = {
        "enriched_via_web": research_data.get("is_verified", False),
        "mfr_url": research_data.get("mfr_url", ""),
        "ref_url_1": research_data.get("ref_url_1", ""),
        "raw_snippet": str(research_data.get("extracted_specs", {}))
    }

    # Stage 3: AI Cognitive Taxonomy Reasoning
    tax_res = classify_product(part_desc, mfg_part_num, raw_dept, raw_class, raw_fine)
    
    # If taxonomy is ambiguous, query Generative AI / Scikit-Learn TF-IDF vector reasoner
    if tax_res.get("is_fallback") and enable_ai_reasoning:
        ai_res = run_generative_enrichment(part_desc, mfg_part_num, part_manuf, brand_name)
        if ai_res and ai_res.get("product_type"):
            tax_res = {
                "cat_key": ai_res.get("product_type", "").lower().replace(' ', '_'),
                "Dept": raw_dept or ai_res.get("dept", "Industrial Supplies"),
                "Class": raw_class or ai_res.get("class_name", "General Hardware"),
                "Fine": raw_fine or ai_res.get("fine_name", "Hardware Supplies"),
                "Classpath": ai_res.get("classpath", "Industrial Supplies>General Hardware"),
                "UNSPSC": ai_res.get("unspsc", ""),
                "Product Name": ai_res.get("product_type", "Product"),
                "is_fallback": False,
                "provenance": ai_res.get("provenance", "AI_GENAI_REASONING")
            }

    # Stage 4: Attribute Extraction & Grounding
    attrs = extract_attributes(part_desc, mfg_part_num, tax_res)

    # Stage 5: Deep Technical Dependency & Physics Imputation (Cross-verified with Research Agent)
    deep_inf = infer_deep_specifications(part_desc, mfg_part_num, tax_res.get('cat_key', ''), attrs, web_data, brand_name)
    
    # Merge research agent & inferred specs into attribute triplets
    existing_labels = {t['label'] for t in attrs.get('attribute_triplets', [])}
    
    # Add agent-verified specs
    for spec_k, spec_v in research_data.get("extracted_specs", {}).items():
        if spec_k not in existing_labels:
            attrs['attribute_triplets'].append({'label': spec_k, 'value': str(spec_v), 'uom': ''})
            existing_labels.add(spec_k)

    for inf_trip in deep_inf.get('inferred_triplets', []):
        if inf_trip['label'] not in existing_labels:
            attrs['attribute_triplets'].append(inf_trip)
            existing_labels.add(inf_trip['label'])
            if len(attrs.get('features', [])) < 10:
                attrs['features'].append(f"{inf_trip['label']}: {inf_trip['value']} {inf_trip['uom']}".strip())

    # Stage 6: Deterministic Industrial Safety Rails & Copywriting Synthesis
    invoice_desc = build_invoice_desc(tax_res['Product Name'], mfg_part_num, attrs)
    mobile_desc = build_mobile_desc(mfg_name, brand_name, tax_res['Product Name'], attrs['series'], mfg_part_num, attrs)
    short_desc = build_short_desc(brand_name, attrs['series'], mfg_part_num, tax_res['Product Name'], attrs['with_modifier'], attrs)
    long_desc = build_long_desc(brand_name, tax_res['Product Name'], attrs['with_modifier'], attrs['series'], mfg_part_num, attrs)
    retail_desc = build_retail_desc(attrs['series'], tax_res['Product Name'], attrs)

    # Digital Asset Standardization
    assets = map_digital_assets(brand_name, mfg_part_num, web_data)

    # Stage 7: Explainability, Evidence Graph & Confidence Auditing
    descs = {
        'INVOICE_DESC': invoice_desc,
        'MOBILE_DESC': mobile_desc,
        'SHORT_DESC': short_desc,
        'LONG_DESC1': long_desc
    }
    audit = generate_audit_trace(raw, brand_res, tax_res, attrs, descs)
    if research_data.get("is_verified"):
        audit["overall_confidence"] = min(1.0, audit["overall_confidence"] + 0.05)
        
    from .evidence_graph import build_product_evidence_graph
    ev_graph = build_product_evidence_graph(mfg_part_num, brand_name, tax_res['Product Name'], attrs, audit, research_data)
    
    audit["evidence_graph"] = ev_graph
    audit["agentic_research"] = {
        "trajectory": research_data.get("research_trajectory", ["DIRECT_GROUNDING"]),
        "has_conflict": research_data.get("has_conflict", False),
        "source": research_data.get("provenance", "LOCAL_GROUNDING")
    }

    # Construct complete 252-column dictionary
    record = {col: "" for col in DELIVERY_HEADERS}
    
    record["PART_NUMBER"] = sku
    record["SKU - MY_PART_NUMBER"] = sku
    record["Mfg_Part_Num"] = mfg_part_num
    record["Part_Desc"] = part_desc
    record["Dept"] = raw_dept or tax_res.get("Dept", "")
    record["Class"] = raw_class or tax_res.get("Class", "")
    record["Fine"] = raw_fine or tax_res.get("Fine", "")
    record["E1_Brand"] = e1_brand or "-- Unbranded --"
    record["Unilog_Brand"] = unilog_brand or "-- No Unilog Brand --"
    record["DIB_Brand"] = dib_brand or "-- No DIB Brand --"
    record["Part_Manuf"] = part_manuf or mfg_name

    record["MANUFACTURER_NAME"] = mfg_name
    record["BRAND_NAME"] = brand_name
    record["MANUFACTURER_PART_NUMBER"] = mfg_part_num
    record["Classpath"] = tax_res.get("Classpath", "")

    record["MOBILE_DESC"] = mobile_desc
    record["INVOICE_DESC"] = invoice_desc
    record["SHORT_DESC"] = short_desc
    record["LONG_DESC1"] = long_desc
    record["RETAIL_DESC"] = retail_desc
    record["MARKETING_DESCRIPTION"] = web_data.get("raw_snippet", "")

    for idx, feat in enumerate(attrs.get('features', [])[:20], 1):
        record[f"ITEM_FEATURES_{idx}"] = feat

    record["With"] = attrs.get("with_modifier", "")
    record["Standard/Approvals"] = attrs.get("standards", "")
    record["Product Name"] = tax_res.get("Product Name", "")
    record["UNSPSC"] = tax_res.get("UNSPSC", "")

    for idx, trip in enumerate(attrs.get('attribute_triplets', [])[:50], 1):
        record[f"ATTRIBUTE_LABEL {idx}"] = trip.get('label', '')
        record[f"ATTRIBUTE_VALUE {idx}"] = trip.get('value', '')
        record[f"ATTRIBUTE_UOM {idx}"] = trip.get('uom', '')

    record["Product Image"] = assets.get("Product Image", "")
    record["Alternate Image 1"] = assets.get("Alternate Image 1", "")
    record["Alternate Image 2"] = assets.get("Alternate Image 2", "")
    record["Alternate Image 3"] = assets.get("Alternate Image 3", "")
    record["Alternate Image 4"] = assets.get("Alternate Image 4", "")
    record["Specification Sheet"] = assets.get("Specification Sheet", "")
    record["Instruction/Installation Manual"] = assets.get("Instruction/Installation Manual", "")
    record["Owners/User Manual"] = assets.get("Owners/User Manual", "")
    record["Actual Image (Yes/No)"] = assets.get("Actual Image (Yes/No)", "No")

    return record, audit

def enrich_dataset(df_input: pd.DataFrame, enable_web_sourcing: bool = True, enable_ai_reasoning: bool = True, parallel_workers: int | None = None) -> tuple[pd.DataFrame, list[dict]]:
    """
    Enriches a catalog batch. Supports parallel worker threads for high-throughput enterprise scale.
    """
    if parallel_workers and parallel_workers > 1:
        from .batch_scale_engine import ParallelBatchScaleEngine
        engine = ParallelBatchScaleEngine(max_workers=parallel_workers)
        df_out, audits, _ = engine.process_catalog_parallel(df_input)
        return df_out, audits

    rows_out = []
    audits = []
    
    for _, row in df_input.iterrows():
        row_dict = row.to_dict()
        rec, audit = enrich_single_record(row_dict, enable_web_sourcing=enable_web_sourcing, enable_ai_reasoning=enable_ai_reasoning)
        rows_out.append(rec)
        audits.append(audit)
        
    df_result = pd.DataFrame(rows_out)
    if DELIVERY_HEADERS:
        for col in DELIVERY_HEADERS:
            if col not in df_result.columns:
                df_result[col] = ""
        df_result = df_result[DELIVERY_HEADERS]
        
    return df_result, audits
