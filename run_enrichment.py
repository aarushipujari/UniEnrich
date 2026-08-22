"""
UniEnrich Batch CLI Enrichment Tool
Processes raw catalog datasets and exports 252-column commerce-ready Excel and CSV files.
"""
import os
import argparse
import pandas as pd
from engine.pipeline import enrich_dataset

def main():
    parser = argparse.ArgumentParser(description="UniEnrich Industrial Catalog Batch Enrichment Engine")
    parser.add_argument("--input", type=str, default="data/sample_input.csv", help="Path to input raw dataset CSV")
    parser.add_argument("--output_csv", type=str, default="data/UniEnrich_Delivered_Catalog_252_Cols.csv", help="Path for output CSV")
    parser.add_argument("--output_xlsx", type=str, default="data/UniEnrich_Delivered_Catalog_252_Cols.xlsx", help="Path for output Excel")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    in_path = os.path.join(base_dir, args.input)
    out_csv = os.path.join(base_dir, args.output_csv)
    out_xlsx = os.path.join(base_dir, args.output_xlsx)

    print(f"Loading raw input dataset from: {in_path}")
    df_raw = pd.read_csv(in_path)
    print(f"Input records: {len(df_raw)} rows, {len(df_raw.columns)} columns")

    print("\nRunning UniEnrich Pipeline...")
    df_enriched, audits = enrich_dataset(df_raw)

    print(f"\nEnrichment complete! Output Shape: {df_enriched.shape}")

    print(f"Saving CSV export to: {out_csv}")
    df_enriched.to_csv(out_csv, index=False)

    print(f"Saving Excel XLSX export to: {out_xlsx}")
    with pd.ExcelWriter(out_xlsx, engine='openpyxl') as writer:
        df_enriched.to_excel(writer, index=False, sheet_name="Delivery_Format")

    print("\n[SUCCESS] Both commerce-ready export files generated successfully.")

if __name__ == "__main__":
    main()
