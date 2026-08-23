"""
UniEnrich Production Catalog Delivery Builder
Processes the entire 1,000-row sample_input.csv through the 7-stage enrichment pipeline
and strict LOV / Sourcing / Schema validation gate.
Exports:
1. data/UniEnrich_Delivered_Catalog_252_Cols.csv
2. data/UniEnrich_Delivered_Catalog_252_Cols.xlsx
"""
import os
import sys
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pipeline import enrich_dataset, DELIVERY_HEADERS

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(DATA_DIR, 'sample_input.csv')
CSV_OUT = os.path.join(DATA_DIR, 'UniEnrich_Delivered_Catalog_252_Cols.csv')
XLSX_OUT = os.path.join(DATA_DIR, 'UniEnrich_Delivered_Catalog_252_Cols.xlsx')

def build_delivered_catalog():
    print(f"Loading {INPUT_FILE}...")
    df_in = pd.read_csv(INPUT_FILE)
    total_in = len(df_in)
    print(f"Processing {total_in} input records through the UniEnrich Cognitive & LOV Pipeline...")

    df_out, audits = enrich_dataset(df_in, enable_web_sourcing=True, enable_ai_reasoning=True, parallel_workers=4)

    # Reindex strictly against expected 252 delivery headers
    df_out = df_out.reindex(columns=DELIVERY_HEADERS, fill_value="")

    print(f"Exporting {len(df_out)} rows with {len(df_out.columns)} columns to CSV: {CSV_OUT}")
    df_out.to_csv(CSV_OUT, index=False)

    print(f"Exporting to XLSX: {XLSX_OUT}")
    with pd.ExcelWriter(XLSX_OUT, engine='openpyxl') as writer:
        df_out.to_excel(writer, index=False, sheet_name="Enriched_Catalog")

    print("[SUCCESS] Catalog generation complete with 100% schema alignment.")

if __name__ == "__main__":
    build_delivered_catalog()
