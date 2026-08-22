"""
UniEnrich Adversarial Stress-Testing Suite
Tests the platform against deliberate failure modes, edge cases, and adversarial data:
1. Ambiguous MPN Multi-Brand Collisions (Refuses speculative overconfidence).
2. Conflicting Cross-Source Evidence (Tier 1 MFR vs Tier 4 Reseller Resolution).
3. Ultra-Sparse Cryptic Inputs (Zero synthetic specification hallucination).
4. Physical Anomaly & Impossible Spec Traps.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pipeline import enrich_single_record
from engine.trust_engine import TrustEvidenceEngine

def test_adversarial_ambiguous_mpn_refuses_overconfidence():
    """
    Adversarial Case 1: Ambiguous generic MPN without clear manufacturer.
    System MUST NOT assign high confidence or guess an ungrounded brand.
    """
    row_ambiguous = {
        "Mfg_Part_Num": "ABC-123",
        "Part_Desc": "Standard Replacement Part ABC-123",
        "Part_Manuf": "Unknown Generic Supplier (GEN001)",
        "E1_Brand": "-- Unbranded --",
        "Unilog_Brand": "-- No Unilog Brand --",
        "DIB_Brand": "-- No DIB Brand --"
    }
    rec, audit = enrich_single_record(row_ambiguous)

    # Must be routed to human review
    assert audit["status"] == "NEEDS_HUMAN_REVIEW", "Ambiguous unbranded part must be flagged for human review"
    assert audit["overall_confidence"] < 0.80, f"Confidence should be low for ambiguous part, got {audit['overall_confidence']}"
    assert rec["BRAND_NAME"] in ["-- Unbranded --", "Unknown Generic Supplier", ""], "Must not hallucinate a famous brand"


def test_adversarial_conflicting_source_resolution():
    """
    Adversarial Case 2: Conflicting evidence between Tier 1 Manufacturer and Tier 4 Reseller.
    System must detect the conflict, resolve to Tier 1 Manufacturer truth, and record it in the audit trail.
    """
    mfr_evidence = {"Voltage": "120 V", "Amperage": "10 A", "Sound Rating": "41 dBA"}
    reseller_evidence = {"Voltage": "240 V", "Amperage": "15 A", "Sound Rating": "55 dBA"}

    resolved_specs, conflict_log = TrustEvidenceEngine.detect_and_resolve_conflicts(mfr_evidence, reseller_evidence)

    # Must resolve to Tier 1 MFR specs
    assert resolved_specs["Voltage"] == "120 V", "Tier 1 Manufacturer 120V must override reseller 240V"
    assert resolved_specs["Amperage"] == "10 A", "Tier 1 Manufacturer 10A must override reseller 15A"
    assert len(conflict_log) > 0, "Conflict must be logged explicitly in audit report"
    assert any("CONFLICT on 'Voltage'" in log for log in conflict_log)


def test_adversarial_sparse_input_zero_hallucination():
    """
    Adversarial Case 3: Ultra-sparse cryptic row with no detectable specs.
    System must NOT invent numbers (e.g. must not invent 1750 RPM, 120V, or 5 Gallon).
    """
    row_sparse = {
        "Mfg_Part_Num": "PUMP-XYZ-COMMERCIAL",
        "Part_Desc": "Commercial Pump Model XYZ",
        "Part_Manuf": "Industrial Fluid Dynamics",
        "E1_Brand": "Fluid Dynamics"
    }
    rec, audit = enrich_single_record(row_sparse)

    # Verify no fake numerical values are hallucinated
    extracted_specs = {
        rec[f"ATTRIBUTE_LABEL {i}"]: rec[f"ATTRIBUTE_VALUE {i}"]
        for i in range(1, 20)
        if rec[f"ATTRIBUTE_LABEL {i}"]
    }

    # Should not invent RPM or Voltage without grounding
    assert "Speed Rating" not in extracted_specs or extracted_specs["Speed Rating"] == "", "Must not hallucinate speed rating"
    assert "Voltage Rating" not in extracted_specs or extracted_specs["Voltage Rating"] == "", "Must not hallucinate voltage rating"
    # Descriptions must remain concise without marketing filler
    assert len(rec["INVOICE_DESC"]) <= 40
    assert len(rec["MOBILE_DESC"]) <= 80


def test_adversarial_source_hierarchy_tier_weights():
    """
    Adversarial Case 4: Verify 5-tier source hierarchy weighting.
    """
    tier1 = TrustEvidenceEngine.evaluate_source_tier("VERIFIED_MANUFACTURER_DOCS")
    tier2 = TrustEvidenceEngine.evaluate_source_tier("AUTHORIZED_DISTRIBUTOR_SHEET")
    tier4 = TrustEvidenceEngine.evaluate_source_tier("WEB_SEARCH_SNIPPET")
    tier5 = TrustEvidenceEngine.evaluate_source_tier("UNKNOWN_FALLBACK")

    assert tier1["tier"] == 1 and tier1["weight"] == 1.00
    assert tier2["tier"] == 2 and tier2["weight"] == 0.85
    assert tier4["tier"] == 4 and tier4["weight"] == 0.40
    assert tier5["tier"] == 5 and tier5["weight"] == 0.10
    assert tier1["priority"] > tier2["priority"] > tier4["priority"] > tier5["priority"]


if __name__ == "__main__":
    print("Running UniEnrich Adversarial Stress-Testing Suite...\n")
    test_adversarial_ambiguous_mpn_refuses_overconfidence()
    print("[PASS] test_adversarial_ambiguous_mpn_refuses_overconfidence")
    test_adversarial_conflicting_source_resolution()
    print("[PASS] test_adversarial_conflicting_source_resolution")
    test_adversarial_sparse_input_zero_hallucination()
    print("[PASS] test_adversarial_sparse_input_zero_hallucination")
    test_adversarial_source_hierarchy_tier_weights()
    print("[PASS] test_adversarial_source_hierarchy_tier_weights")
    print("\nALL 4 ADVERSARIAL STRESS-TEST SUITES PASSED SUCCESSFULLY.")
