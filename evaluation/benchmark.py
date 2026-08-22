"""
UniEnrich Benchmark & Evaluation Suite
Performs dual evaluation:
1. Ground Truth Accuracy Scoring (Compares predicted records against ground_truth_200.csv)
2. 1,000 Catalog Scale & Guideline Compliance Scoring (Strict character limits, UOM standards, zero false fallbacks)
"""
import os
import pandas as pd
from engine.pipeline import enrich_single_record, enrich_dataset

def run_benchmark_tests():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    sample_file = os.path.join(data_dir, 'sample_input.csv')
    gt_file = os.path.join(data_dir, 'ground_truth_200.csv')
    
    # -------------------------------------------------------------
    # 1. GROUND TRUTH ACCURACY SCORING
    # -------------------------------------------------------------
    gt_report = {
        "ground_truth_records_evaluated": 0,
        "gt_brand_exact_match_pct": 0.0,
        "gt_manufacturer_match_pct": 0.0,
        "gt_classpath_match_pct": 0.0,
        "gt_unspsc_match_pct": 0.0,
        "gt_product_image_match_pct": 0.0,
        "gt_spec_sheet_match_pct": 0.0
    }

    if os.path.exists(gt_file):
        df_gt = pd.read_csv(gt_file)
        gt_count = len(df_gt)
        if gt_count > 0:
            brand_matches = 0
            mfg_matches = 0
            classpath_matches = 0
            unspsc_matches = 0
            image_matches = 0
            spec_matches = 0

            for _, row_gt in df_gt.iterrows():
                # Prepare raw input
                raw_in = {
                    "Mfg_Part_Num": row_gt.get("Mfg_Part_Num", row_gt.get("MANUFACTURER_PART_NUMBER", "")),
                    "Part_Desc": row_gt.get("Part_Desc", ""),
                    "E1_Brand": row_gt.get("E1_Brand", ""),
                    "Unilog_Brand": row_gt.get("Unilog_Brand", ""),
                    "DIB_Brand": row_gt.get("DIB_Brand", ""),
                    "Part_Manuf": row_gt.get("Part_Manuf", "")
                }
                pred_rec, _ = enrich_single_record(raw_in, enable_web_sourcing=False)
                
                # Compare Brand
                if str(pred_rec.get("BRAND_NAME", "")).strip() == str(row_gt.get("BRAND_NAME", "")).strip():
                    brand_matches += 1
                if str(pred_rec.get("MANUFACTURER_NAME", "")).strip() == str(row_gt.get("MANUFACTURER_NAME", "")).strip():
                    mfg_matches += 1
                if str(pred_rec.get("Classpath", "")).strip() == str(row_gt.get("Classpath", "")).strip():
                    classpath_matches += 1
                if str(pred_rec.get("UNSPSC", "")).strip() == str(row_gt.get("UNSPSC", "")).strip():
                    unspsc_matches += 1
                if str(pred_rec.get("Product Image", "")).strip() == str(row_gt.get("Product Image", "")).strip():
                    image_matches += 1
                if str(pred_rec.get("Specification Sheet", "")).strip() == str(row_gt.get("Specification Sheet", "")).strip():
                    spec_matches += 1

            gt_report = {
                "ground_truth_records_evaluated": gt_count,
                "gt_brand_exact_match_pct": round((brand_matches / gt_count) * 100, 2),
                "gt_manufacturer_match_pct": round((mfg_matches / gt_count) * 100, 2),
                "gt_classpath_match_pct": round((classpath_matches / gt_count) * 100, 2),
                "gt_unspsc_match_pct": round((unspsc_matches / gt_count) * 100, 2),
                "gt_product_image_match_pct": round((image_matches / gt_count) * 100, 2),
                "gt_spec_sheet_match_pct": round((spec_matches / gt_count) * 100, 2)
            }

    # -------------------------------------------------------------
    # 2. 1,000-CATALOG SCALE & RULE COMPLIANCE AUDIT
    # -------------------------------------------------------------
    df_sample = pd.read_csv(sample_file)
    total_rows = len(df_sample)
    df_enriched, audits = enrich_dataset(df_sample, enable_web_sourcing=False)
    
    # 1. Invoice Description Audits (<= 40 chars, UPPERCASE)
    inv_lens = df_enriched['INVOICE_DESC'].apply(len)
    inv_len_pass = (inv_lens <= 40).sum()
    inv_case_pass = df_enriched['INVOICE_DESC'].str.isupper().sum()
    
    # 2. Mobile Description Audits (Strict 60-80 chars target)
    mob_lens = df_enriched['MOBILE_DESC'].apply(len)
    mob_strict_pass = ((mob_lens >= 60) & (mob_lens <= 80)).sum()
    
    # 3. Brand Resolution Audits
    brands_resolved = (df_enriched['BRAND_NAME'] != 'Unbranded').sum()
    trademark_present = df_enriched['BRAND_NAME'].apply(lambda x: '®' in str(x) or '™' in str(x)).sum()
    
    # 4. Classpath Completeness
    classpath_present = (df_enriched['Classpath'].str.len() > 0).sum()
    
    # 5. Non-Hallucination & Fallback Audit (Ensures zero dishwashers on non-dishwashers)
    dishwasher_count = df_enriched['Product Name'].apply(lambda x: x == 'Dishwasher').sum()
    
    # 6. Overall Confidence & Human-in-the-Loop Flags
    confidences = [a['overall_confidence'] for a in audits]
    avg_conf = sum(confidences) / len(confidences)
    verified_count = sum(1 for a in audits if a['status'] == 'VERIFIED')
    review_queue_count = total_rows - verified_count

    scale_report = {
        "total_records_processed": total_rows,
        "schema_columns_count": len(df_enriched.columns),
        "invoice_len_compliance_pct": round((inv_len_pass / total_rows) * 100, 2),
        "invoice_uppercase_compliance_pct": round((inv_case_pass / total_rows) * 100, 2),
        "mobile_strict_60_80_pct": round((mob_strict_pass / total_rows) * 100, 2),
        "brand_resolution_rate_pct": round((brands_resolved / total_rows) * 100, 2),
        "trademark_symbol_enforcement_pct": round((trademark_present / total_rows) * 100, 2),
        "taxonomy_classpath_coverage_pct": round((classpath_present / total_rows) * 100, 2),
        "dishwasher_legitimate_count": int(dishwasher_count),
        "average_confidence_score": round(avg_conf, 3),
        "auto_verified_records_count": verified_count,
        "human_review_queue_count": review_queue_count
    }

    full_report = {**gt_report, **scale_report}

    print("=== UniEnrich Ground Truth & Quality Benchmark Scorecard ===")
    print("\n[A. GROUND TRUTH ACCURACY (vs. Known Labeled Rows)]")
    for k in gt_report:
        print(f"  * {k}: {gt_report[k]}")

    print("\n[B. SCALE DATASET QUALITY & COMPLIANCE (1,000 Rows)]")
    for k in scale_report:
        print(f"  * {k}: {scale_report[k]}")
        
    return full_report

if __name__ == '__main__':
    run_benchmark_tests()
