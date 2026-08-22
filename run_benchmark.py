"""
CLI Benchmark Runner
"""
from evaluation.benchmark import run_full_benchmark

if __name__ == "__main__":
    res = run_full_benchmark()
    print("=== UniEnrich Ground Truth & Quality Benchmark Scorecard ===\n")
    print("[A. GROUND TRUTH ACCURACY (vs. 100% Disjoint Held-Out Dataset - 200 Records)]")
    for k, v in list(res.items())[:7]:
        print(f"  * {k}: {v}")
    print("\n[B. SCALE DATASET QUALITY & COMPLIANCE (1,000 Rows)]")
    for k, v in list(res.items())[7:]:
        print(f"  * {k}: {v}")
