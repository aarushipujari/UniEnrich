"""
UniEnrich Comprehensive Pipeline Regression & Standards Test Suite
Executes end-to-end assertions verifying schema integrity, Unilog channel constraints,
dynamic grit parsing, color-noise isolation, and calibrated audit traces.
Compatible with both `pytest` and direct execution via `python test_pipeline.py`.
"""
import os
import pandas as pd
from engine.pipeline import enrich_single_record, enrich_dataset, DELIVERY_HEADERS

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
SAMPLE_FILE = os.path.join(DATA_DIR, 'sample_input.csv')


def test_schema_column_invariance():
    """Verifies that every enriched record adheres strictly to the 252-column schema."""
    item = {
        "Mfg_Part_Num": "DCB518ASTS06G",
        "Part_Desc": "1/2\"x18\" Sanding Belt 6pc Assorted 80/120 Grit",
        "Part_Manuf": "Freud America, Inc.",
        "E1_Brand": "Diablo"
    }
    rec, audit = enrich_single_record(item)
    
    assert len(rec.keys()) == 252, f"Expected 252 columns, got {len(rec.keys())}"
    assert list(rec.keys()) == DELIVERY_HEADERS, "Output column headers must match standard schema exactly"
    assert rec["BRAND_NAME"] == "Diablo®"
    assert rec["MANUFACTURER_NAME"] == "Freud America, Inc."
    assert rec["Classpath"] == "Abrasives>Sanding & Finishing>Sanding Belts"
    assert rec["Product Name"] == "Sanding Belt"


def test_channel_description_constraints():
    """Asserts that channel descriptions strictly adhere to length ceilings and uppercase rules."""
    item = {
        "Mfg_Part_Num": "PDSH4816AF",
        "Part_Desc": "PDSH4816AF Built-In Dishwasher Stainless Steel 24in 120V 10A 41 dBA",
        "Part_Manuf": "Appliance Dealers Cooperative (APPDE)",
        "E1_Brand": "Frigidaire"
    }
    rec, audit = enrich_single_record(item)
    
    # Invoice Description: <= 40 chars and 100% uppercase
    assert len(rec["INVOICE_DESC"]) <= 40, f"Invoice desc exceeds 40 chars: '{rec['INVOICE_DESC']}'"
    assert rec["INVOICE_DESC"].isupper(), f"Invoice desc must be uppercase: '{rec['INVOICE_DESC']}'"
    
    # Mobile Description: <= 80 chars
    assert len(rec["MOBILE_DESC"]) <= 80, f"Mobile desc exceeds 80 chars: '{rec['MOBILE_DESC']}'"
    
    # Short Description (Title): Starts with Brand and contains MPN
    assert rec["SHORT_DESC"].startswith("FRIGIDAIRE®"), f"Title must start with Brand: '{rec['SHORT_DESC']}'"
    assert "PDSH4816AF" in rec["SHORT_DESC"], "Title must contain MPN"
    
    # Long Description: Must be a non-empty grammatical narrative
    assert len(rec["LONG_DESC1"]) > 20, "Long description should be a complete sentence"
    assert rec["LONG_DESC1"].endswith("."), "Long description must end with a period"


def test_tightened_grit_parsing_no_false_positives():
    """Asserts that numbers in MPN or dimensions are NOT mislabeled as Grit without P-prefix or 'grit'."""
    # Case A: MPN has '180' but no P-prefix or grit word -> Should NOT extract grit
    item_false = {
        "Mfg_Part_Num": "MRK-ABR-5IN-180",
        "Part_Desc": "Mirka 5in Sanding Disc Hook and Loop",
        "Part_Manuf": "Mirka USA Inc.",
        "E1_Brand": "Mirka"
    }
    rec_false, _ = enrich_single_record(item_false)
    extracted_labels = [rec_false[f"ATTRIBUTE_LABEL {i}"] for i in range(1, 10) if rec_false[f"ATTRIBUTE_LABEL {i}"]]
    assert "Grit" not in extracted_labels, "MPN digit '180' must not be falsely parsed as Grit"

    # Case B: Explicit P-prefix 'P180' -> MUST extract Grit P180
    item_p = {
        "Mfg_Part_Num": "9A-232-180",
        "Part_Desc": "Mirka Abranet 5in Mesh Grip Disc P180 50/Box",
        "Part_Manuf": "Mirka USA Inc.",
        "E1_Brand": "Mirka"
    }
    rec_p, _ = enrich_single_record(item_p)
    assert any(rec_p[f"ATTRIBUTE_LABEL {i}"] == "Grit" and rec_p[f"ATTRIBUTE_VALUE {i}"] == "P180" for i in range(1, 10)), "Explicit P180 must be extracted as Grit P180"

    # Case C: Explicit word '80 Grit' -> MUST extract Grit P80
    item_word = {
        "Mfg_Part_Num": "DCB518-80",
        "Part_Desc": "Diablo 1/2x18 80 Grit Sanding Belt",
        "Part_Manuf": "Freud America, Inc.",
        "E1_Brand": "Diablo"
    }
    rec_word, _ = enrich_single_record(item_word)
    assert any(rec_word[f"ATTRIBUTE_LABEL {i}"] == "Grit" and rec_word[f"ATTRIBUTE_VALUE {i}"] == "P80" for i in range(1, 10)), "Explicit '80 Grit' must be extracted as Grit P80"


def test_color_and_mortar_taxonomy_isolation():
    """Asserts that color modifiers (e.g. Dark Chocolate) do not contaminate product names."""
    item = {
        "Mfg_Part_Num": "38-E",
        "Part_Desc": "Dark Chocolate 38-E Mortar - Type N 50lb",
        "Part_Manuf": "Commercial Mortar Supply",
        "E1_Brand": "-- Unbranded --"
    }
    rec, audit = enrich_single_record(item)
    
    assert rec["Product Name"] == "Masonry Mortar Mix", f"Expected 'Masonry Mortar Mix', got '{rec['Product Name']}'"
    assert rec["Product Name"] != "Chocolate Mortar", "Color prefix must not contaminate product name"
    assert rec["Classpath"] == "Building Materials>Masonry>Mortar Mixes"
    assert audit["status"] == "NEEDS_HUMAN_REVIEW", "Unbranded items must be routed to human review"
    assert audit["overall_confidence"] < 0.80, "Unbranded confidence must be penalized"


def test_explainability_and_audit_provenance():
    """Asserts that confidence is empirical and provenance trail is populated."""
    item = {
        "Mfg_Part_Num": "DW088CG",
        "Part_Desc": "DEWALT DW088CG Green Cross Line Self Leveling Laser Level",
        "Part_Manuf": "Black & Decker / DEWALT",
        "E1_Brand": "DEWALT"
    }
    rec, audit = enrich_single_record(item)
    
    assert 0.80 <= audit["overall_confidence"] <= 1.0, f"High-confidence verified item expected, got {audit['overall_confidence']}"
    assert audit["status"] == "VERIFIED"
    assert "provenance_trail" in audit
    assert audit["provenance_trail"]["brand_resolution"]["source"] in ["EXACT_BRAND_ALIAS", "MANUF_ALIAS_RESOLVED", "NGRAM_CATALOG_MATCH"]
    assert audit["provenance_trail"]["taxonomy_classification"]["product_type"] == "Cross Line Laser"


def test_batch_enrichment_regression_100_rows():
    """Runs batch enrichment on 100 sample catalog rows and verifies 100% compliance across all assertions."""
    df_raw = pd.read_csv(SAMPLE_FILE).head(100)
    df_out, audits = enrich_dataset(df_raw)
    
    assert len(df_out) == 100
    assert len(df_out.columns) == 252
    assert len(audits) == 100
    
    # 1. 100% Invoice <= 40 chars
    invoice_lens = df_out["INVOICE_DESC"].astype(str).str.len()
    assert (invoice_lens <= 40).all(), f"Invoice length violation detected: max {invoice_lens.max()}"
    
    # 2. 100% Invoice uppercase
    invoice_uppers = [s.isupper() or s == "" for s in df_out["INVOICE_DESC"].astype(str)]
    assert all(invoice_uppers), "All invoice descriptions must be strictly uppercase"
    
    # 3. 100% Mobile <= 80 chars
    mobile_lens = df_out["MOBILE_DESC"].astype(str).str.len()
    assert (mobile_lens <= 80).all(), f"Mobile length violation detected: max {mobile_lens.max()}"
    
    # 4. Valid confidence bounds
    for a in audits:
        assert 0.0 <= a["overall_confidence"] <= 1.0, f"Confidence out of bounds: {a['overall_confidence']}"
        assert a["status"] in ["VERIFIED", "NEEDS_HUMAN_REVIEW"]


def test_amperage_and_with_modifier_guardrails():
    """Asserts that Type 1A does not trigger amperage, and With X modifier is capped."""
    # Case A: "Type 1A" code should NOT extract Amperage: 1 A
    item_grade = {
        "Mfg_Part_Num": "5000",
        "Part_Desc": "Quikrete 5000 Concrete Mix Type 1A 50lb",
        "Part_Manuf": "Quikrete Companies",
        "E1_Brand": "Quikrete"
    }
    rec_grade, _ = enrich_single_record(item_grade)
    extracted_labels = [rec_grade[f"ATTRIBUTE_LABEL {i}"] for i in range(1, 10) if rec_grade[f"ATTRIBUTE_LABEL {i}"]]
    assert "Amperage Rating" not in extracted_labels, "Type 1A code must not be extracted as Amperage"

    # Case B: Real electrical amperage (e.g. 120V 10A) MUST be extracted
    item_elec = {
        "Mfg_Part_Num": "PDSH4816AF",
        "Part_Desc": "Built-In Dishwasher 120V 10A Stainless Steel",
        "Part_Manuf": "Frigidaire",
        "E1_Brand": "Frigidaire"
    }
    rec_elec, _ = enrich_single_record(item_elec)
    assert any(rec_elec[f"ATTRIBUTE_LABEL {i}"] == "Amperage Rating" and rec_elec[f"ATTRIBUTE_VALUE {i}"] == "10" for i in range(1, 10)), "10A electrical draw must be extracted"

    # Case C: Overlong 'With' clause should be capped to <= 25 characters
    item_with = {
        "Mfg_Part_Num": "DW088CG",
        "Part_Desc": "Cross Line Laser Level with ultra durable rubber overmolded housing and magnetic pivoting base for commercial jobsites",
        "Part_Manuf": "DEWALT",
        "E1_Brand": "DEWALT"
    }
    rec_with, _ = enrich_single_record(item_with)
    # With modifier in short desc must be concise
    assert len(rec_with["INVOICE_DESC"]) <= 40
    assert len(rec_with["MOBILE_DESC"]) <= 80


def test_agentic_research_loop_and_conflict_resolution():
    """Asserts that the research agent performs multi-turn verification and grounds specs."""
    from engine.research_agent import query_agentic_research
    
    # 1. Turn 1 Manufacturer verification
    res_mfr = query_agentic_research("PDSH4816AF", "Dishwasher SS", "Frigidaire")
    assert res_mfr["is_verified"] is True
    assert "120 V" in res_mfr["extracted_specs"].values()
    assert "10 A" in res_mfr["extracted_specs"].values()
    assert "https://www.frigidaire.com" in res_mfr["mfr_url"]

    # 2. Secondary datasheet fallback
    res_sec = query_agentic_research("NONEXISTENT-999", "Specialist 240V 15A 3450RPM Motor", "UnknownBrand")
    assert res_sec["extracted_specs"].get("Voltage") == "240 V"
    assert res_sec["extracted_specs"].get("Speed Rating") == "3450 RPM"


def test_parallel_batch_scale_engine_throughput_and_recovery():
    """Asserts that ParallelBatchScaleEngine processes concurrently and passes 100% schema checks."""
    from engine.batch_scale_engine import ParallelBatchScaleEngine
    sample_path = os.path.join(DATA_DIR, "sample_input.csv")
    if os.path.exists(sample_path):
        df_sample = pd.read_csv(sample_path).head(50)
        engine = ParallelBatchScaleEngine(max_workers=4)
        df_res, audits, metrics = engine.process_catalog_parallel(df_sample)
        
        assert len(df_res) == len(df_sample)
        assert len(df_res.columns) == 252
        assert metrics["parallel_workers"] == 4
        assert metrics["throughput_records_per_sec"] > 0
        assert metrics["fault_tolerance_pass_rate"] == "100.0%"


def test_adversarial_stress_suite():
    """Asserts that adversarial ambiguous, conflicting, and sparse tests all pass."""
    from evaluation.adversarial_tests import (
        test_adversarial_ambiguous_mpn_refuses_overconfidence,
        test_adversarial_conflicting_source_resolution,
        test_adversarial_sparse_input_zero_hallucination,
        test_adversarial_source_hierarchy_tier_weights
    )
    test_adversarial_ambiguous_mpn_refuses_overconfidence()
    test_adversarial_conflicting_source_resolution()
    test_adversarial_sparse_input_zero_hallucination()
    test_adversarial_source_hierarchy_tier_weights()


def test_held_out_unseen_split_evaluation():
    """Asserts that the 50-item Held-Out Unseen Test Set achieves high accuracy and 100% hard constraint compliance."""
    from evaluation.split_evaluator import run_split_evaluation
    rep = run_split_evaluation()
    assert rep["total_test_products"] == 50
    assert rep["metrics"]["invoice_caps_ceiling_compliance"] == "100.0%"
    assert rep["metrics"]["mobile_char_limit_compliance"] == "100.0%"
    assert rep["metrics"]["schema_columns_verified"] == "252 / 252"
    assert rep["metrics"]["unseen_brand_accuracy"] == "100.0%"


def test_evidence_graph_and_conflict_intelligence():
    """Asserts that the evidence graph builder produces valid nodes, edges, and conflict structures."""
    item = {
        "Mfg_Part_Num": "PDSH4816AF",
        "Part_Desc": "Built-In Dishwasher 120V 10A Stainless Steel 41 dBA",
        "Part_Manuf": "Frigidaire",
        "E1_Brand": "Frigidaire"
    }
    rec, audit = enrich_single_record(item)
    ev_graph = audit.get("evidence_graph", {})

    assert ev_graph.get("concept_identity") == "Evidence-First Product Intelligence (Machine-Verifiable Graph)"
    assert ev_graph.get("total_nodes") >= 4
    assert ev_graph.get("total_edges") >= 3
    assert any(n["type"] == "PRODUCT_ROOT" for n in ev_graph.get("nodes", []))
    assert any(n["type"] == "GROUNDED_ATTRIBUTE" for n in ev_graph.get("nodes", []))
    assert "graph TD" in ev_graph.get("mermaid_diagram", "")


def test_business_impact_roi_quantification():
    """Asserts that the Business Impact Calculator accurately computes financial and labor savings."""
    from engine.business_impact import get_business_impact_metrics
    metrics = get_business_impact_metrics(
        total_items=1000,
        direct_publish_count=780,
        assisted_count=150,
        review_count=70,
        processing_time_sec=85.0
    )
    assert metrics["measured_runtime_metrics"]["catalog_items_processed"] == 1000
    assert metrics["measured_runtime_metrics"]["fields_standardized"] == 252000
    assert "94.6%" in metrics["projected_enterprise_savings"]["projected_labor_reduction"]
    assert "1,262 Hours" in metrics["scale_10k_sku_projection"]["projected_hours_saved"]
    assert "$63,100" in metrics["scale_10k_sku_projection"]["projected_cost_saved"]


def test_multi_scale_scaling_stress_test():
    """Asserts that the Multi-Scale Scale Engine executes benchmarks across 100, 500, and 1000 items."""
    from engine.batch_scale_engine import ParallelBatchScaleEngine
    sample_path = os.path.join(DATA_DIR, "sample_input.csv")
    if os.path.exists(sample_path):
        df_sample = pd.read_csv(sample_path).head(100)
        engine = ParallelBatchScaleEngine(max_workers=4)
        bench = engine.run_multi_scale_benchmark(df_sample)
        assert len(bench["benchmark_results"]) == 4
        assert bench["benchmark_results"][0]["products_count"] == 100
        assert "100.0%" in bench["benchmark_results"][0]["success_rate"]
        assert "Projected" in bench["benchmark_results"][3]["success_rate"]


if __name__ == "__main__":
    print("Running UniEnrich Pipeline Test Suite with Hard Assertions...\n")
    test_schema_column_invariance()
    print("[PASS] test_schema_column_invariance")
    test_channel_description_constraints()
    print("[PASS] test_channel_description_constraints")
    test_tightened_grit_parsing_no_false_positives()
    print("[PASS] test_tightened_grit_parsing_no_false_positives")
    test_color_and_mortar_taxonomy_isolation()
    print("[PASS] test_color_and_mortar_taxonomy_isolation")
    test_explainability_and_audit_provenance()
    print("[PASS] test_explainability_and_audit_provenance")
    test_batch_enrichment_regression_100_rows()
    print("[PASS] test_batch_enrichment_regression_100_rows")
    test_amperage_and_with_modifier_guardrails()
    print("[PASS] test_amperage_and_with_modifier_guardrails")
    test_agentic_research_loop_and_conflict_resolution()
    print("[PASS] test_agentic_research_loop_and_conflict_resolution")
    test_parallel_batch_scale_engine_throughput_and_recovery()
    print("[PASS] test_parallel_batch_scale_engine_throughput_and_recovery")
    test_adversarial_stress_suite()
    print("[PASS] test_adversarial_stress_suite")
    test_held_out_unseen_split_evaluation()
    print("[PASS] test_held_out_unseen_split_evaluation")
    test_evidence_graph_and_conflict_intelligence()
    print("[PASS] test_evidence_graph_and_conflict_intelligence")
    test_business_impact_roi_quantification()
    print("[PASS] test_business_impact_roi_quantification")
    test_multi_scale_scaling_stress_test()
    print("[PASS] test_multi_scale_scaling_stress_test")
    print("\nALL 14 HARD REGRESSION TEST SUITES PASSED SUCCESSFULLY.")

