"""
Quick test script to run UniEnrich on sample input and verify ground truth consistency.
"""
import os
import pandas as pd
from engine.pipeline import enrich_single_record, enrich_dataset

data_dir = os.path.join(os.path.dirname(__file__), 'data')
sample_file = os.path.join(data_dir, 'sample_input.csv')

df_sample = pd.read_csv(sample_file)
print(f"Loaded {len(df_sample)} sample rows.")

# Test single item 0
item0 = df_sample.iloc[0].to_dict()
rec0, audit0 = enrich_single_record(item0)

print("\n--- Single Item 0 Test (Diablo Sanding Belt) ---")
print("Input:", item0)
print("\nEnriched Fields:")
print("BRAND_NAME:", rec0["BRAND_NAME"])
print("MANUFACTURER_NAME:", rec0["MANUFACTURER_NAME"])
print("Classpath:", rec0["Classpath"])
print("INVOICE_DESC (len={}): {}".format(len(rec0["INVOICE_DESC"]), rec0["INVOICE_DESC"]))
print("MOBILE_DESC (len={}): {}".format(len(rec0["MOBILE_DESC"]), rec0["MOBILE_DESC"]))
print("SHORT_DESC:", rec0["SHORT_DESC"])
print("LONG_DESC1:", rec0["LONG_DESC1"])
print("Product Image:", rec0["Product Image"])
print("Confidence:", audit0["overall_confidence"])
print("Status:", audit0["status"])

# Test batch enrichment on first 50 rows
print("\n--- Running Batch Enrichment on 50 rows ---")
df_sub = df_sample.head(50)
df_enriched, audits = enrich_dataset(df_sub)
print("Output Shape:", df_enriched.shape)

invoice_lens = df_enriched['INVOICE_DESC'].apply(len)
print(f"Max Invoice Desc Length: {invoice_lens.max()} (All <=40? {invoice_lens.max() <= 40})")
print(f"All Invoice Upper? {all(df_enriched['INVOICE_DESC'].str.isupper())}")

mobile_lens = df_enriched['MOBILE_DESC'].apply(len)
print(f"Mobile Desc Avg Length: {mobile_lens.mean():.1f} chars (Min: {mobile_lens.min()}, Max: {mobile_lens.max()})")
print("Test completed successfully.")
