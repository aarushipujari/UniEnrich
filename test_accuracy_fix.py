from engine.pipeline import enrich_single_record

test_items = [
    {
        "Mfg_Part_Num": "1046793",
        "Part_Desc": "First Alert Hardwired Smoke & CO Alarm 10-Yr Battery",
        "Part_Manuf": "Resideo Technologies (RESID)",
        "E1_Brand": "-- Unbranded --"
    },
    {
        "Mfg_Part_Num": "640383",
        "Part_Desc": "1/2x4x8 CertainTeed Easi-Lite Lightweight Gypsum Board",
        "Part_Manuf": "Saint-Gobain (SAINT)",
        "E1_Brand": "-- Unbranded --"
    }
]

for idx, item in enumerate(test_items, 1):
    rec, audit = enrich_single_record(item)
    print(f"=== ITEM {idx}: {item['Part_Desc']} ===")
    print("Product Name:", rec["Product Name"])
    print("Brand Name:", rec["BRAND_NAME"])
    print("Manufacturer Name:", rec["MANUFACTURER_NAME"])
    print("Classpath:", rec["Classpath"])
    print("Invoice Desc:", rec["INVOICE_DESC"])
    print("Short Desc (Title):", rec["SHORT_DESC"])
    print("Confidence Score:", audit["overall_confidence"])
    print("Audit Status:", audit["status"])
    print("Provenance:", audit["provenance_trail"]["taxonomy_classification"])
    print()
