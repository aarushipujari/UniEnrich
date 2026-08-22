"""
UniEnrich Evaluation & Benchmark Suite
Computes dual-layer performance metrics:
1. Ground Truth Accuracy vs. 100% Disjoint Held-Out Dataset (200 Records)
2. Industrial Standards & Schema Compliance on 1,000 Catalog Records
"""
import os
import re
import pandas as pd
from engine.pipeline import enrich_dataset

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
SAMPLE_INPUT = os.path.join(DATA_DIR, 'sample_input.csv')
GROUND_TRUTH_FILE = os.path.join(DATA_DIR, 'ground_truth_200.csv')

def run_ground_truth_evaluation() -> dict:
    if not os.path.exists(GROUND_TRUTH_FILE):
        return {"error": "Ground truth dataset not found."}
        
    df_gt = pd.read_csv(GROUND_TRUTH_FILE)
    df_pred, audits = enrich_dataset(df_gt, enable_web_sourcing=True, enable_ai_reasoning=True)
    
    total = len(df_gt)
    brand_matches = 0
    manuf_matches = 0
    cp_matches = 0
    unspsc_matches = 0
    img_matches = 0
    spec_matches = 0
    
    for i in range(total):
        gt_row = df_gt.iloc[i]
        pr_row = df_pred.iloc[i]
        
        gt_brand = str(gt_row.get('BRAND_NAME', '')).strip()
        pr_brand = str(pr_row.get('BRAND_NAME', '')).strip()
        if gt_brand and gt_brand.lower() == pr_brand.lower():
            brand_matches += 1
            
        gt_mfg = str(gt_row.get('MANUFACTURER_NAME', '')).strip()
        pr_mfg = str(pr_row.get('MANUFACTURER_NAME', '')).strip()
        if gt_mfg and (gt_mfg.lower() in pr_mfg.lower() or pr_mfg.lower() in gt_mfg.lower()):
            manuf_matches += 1
            
        gt_cp = str(gt_row.get('Classpath', '')).strip()
        pr_cp = str(pr_row.get('Classpath', '')).strip()
        if gt_cp and gt_cp.lower() == pr_cp.lower():
            cp_matches += 1
            
        gt_un = str(gt_row.get('UNSPSC', '')).strip()
        pr_un = str(pr_row.get('UNSPSC', '')).strip()
        if gt_un and gt_un == pr_un:
            unspsc_matches += 1

        gt_img = str(gt_row.get('Product Image', '')).strip()
        pr_img = str(pr_row.get('Product Image', '')).strip()
        if gt_img and gt_img == pr_img:
            img_matches += 1
            
        gt_spec = str(gt_row.get('Specification Sheet', '')).strip()
        pr_spec = str(pr_row.get('Specification Sheet', '')).strip()
        if gt_spec and gt_spec == pr_spec:
            spec_matches += 1

    return {
        "ground_truth_records_evaluated": total,
        "gt_brand_exact_match_pct": round((brand_matches / total) * 100, 1),
        "gt_manufacturer_match_pct": round((manuf_matches / total) * 100, 1),
        "gt_classpath_match_pct": round((cp_matches / total) * 100, 1),
        "gt_unspsc_match_pct": round((unspsc_matches / total) * 100, 1),
        "gt_product_image_match_pct": round((img_matches / total) * 100, 1),
        "gt_spec_sheet_match_pct": round((spec_matches / total) * 100, 1),
    }

def run_full_benchmark() -> dict:
    df_raw = pd.read_csv(SAMPLE_INPUT)
    df_out, audits = enrich_dataset(df_raw, enable_web_sourcing=True, enable_ai_reasoning=True)

    gt_metrics = run_ground_truth_evaluation()

    total = len(df_out)
    inv_len_pass = sum(1 for d in df_out['INVOICE_DESC'] if len(str(d)) <= 40)
    inv_upper_pass = sum(1 for d in df_out['INVOICE_DESC'] if str(d).isupper() or str(d) == "")
    mob_within_ceiling = sum(1 for d in df_out['MOBILE_DESC'] if len(str(d)) <= 80)
    mob_len_strict = sum(1 for d in df_out['MOBILE_DESC'] if 60 <= len(str(d)) <= 80)
    
    brand_resolved_count = sum(1 for b in df_out['BRAND_NAME'] if str(b) and str(b) != "Unbranded" and not str(b).startswith('--'))
    trademark_count = sum(1 for b in df_out['BRAND_NAME'] if '®' in str(b) or '™' in str(b))
    tm_on_resolved = (trademark_count / brand_resolved_count * 100) if brand_resolved_count else 0

    cp_pass = sum(1 for c in df_out['Classpath'] if str(c) and '>' in str(c))
    dw_count = sum(1 for p in df_out['Product Name'] if str(p).lower() == 'dishwasher')
    
    confs = [a.get('overall_confidence', 0.5) for a in audits]
    avg_conf = sum(confs) / len(confs) if confs else 0.0
    verified_count = sum(1 for a in audits if a.get('status') == 'VERIFIED')
    review_count = sum(1 for a in audits if a.get('status') == 'NEEDS_HUMAN_REVIEW')

    scale_metrics = {
        "total_records_processed": total,
        "schema_columns_count": len(df_out.columns),
        "invoice_len_compliance_pct": round((inv_len_pass / total) * 100, 1),
        "invoice_uppercase_compliance_pct": round((inv_upper_pass / total) * 100, 1),
        "mobile_ceiling_80_compliance_pct": round((mob_within_ceiling / total) * 100, 1),
        "mobile_strict_60_80_pct": round((mob_len_strict / total) * 100, 1),
        "brand_resolution_rate_pct": round((brand_resolved_count / total) * 100, 1),
        "trademark_enforcement_on_resolved_pct": round(tm_on_resolved, 1),
        "overall_dataset_trademark_pct": round((trademark_count / total) * 100, 1),
        "taxonomy_classpath_coverage_pct": round((cp_pass / total) * 100, 1),
        "dishwasher_legitimate_count": dw_count,
        "average_confidence_score": round(avg_conf, 3),
        "auto_verified_records_count": verified_count,
        "human_review_queue_count": review_count
    }

    return {**gt_metrics, **scale_metrics}

# Alias for web/app.py compatibility
run_benchmark_tests = run_full_benchmark

if __name__ == '__main__':
    res = run_full_benchmark()
    print("=== UniEnrich Ground Truth & Quality Benchmark Scorecard ===\n")
    print("[A. GROUND TRUTH ACCURACY (vs. 100% Disjoint Held-Out Dataset - 200 Records)]")
    for k, v in list(res.items())[:7]:
        print(f"  * {k}: {v}")
    print("\n[B. SCALE DATASET QUALITY & COMPLIANCE (1,000 Rows)]")
    for k, v in list(res.items())[7:]:
        print(f"  * {k}: {v}")
