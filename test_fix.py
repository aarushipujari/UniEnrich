from engine.pipeline import enrich_single_record

test_items = [
    {
        "Mfg_Part_Num": "T27417",
        "Part_Desc": "T27417 Grizzly OscillatingEdge - Belt and Spindle Sander",
        "Part_Manuf": "Woodstock Intl (3658)",
        "E1_Brand": "-- Unbranded --"
    },
    {
        "Mfg_Part_Num": "DW088CG",
        "Part_Desc": "DW088CG Dewalt Laser - Green Cross Line",
        "Part_Manuf": "Black & Decker/dewlt (2585)",
        "E1_Brand": "DEWALT"
    },
    {
        "Mfg_Part_Num": "DCB518ASTS06G",
        "Part_Desc": 'DCB518ASTS06G Diablo 1/2"x18" - Sanding Belt 6pc',
        "Part_Manuf": "Freud Inc (2435)",
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
    print("Short Desc (Title):", rec["SHORT_DESC"])
    print("Invoice Desc (<=40):", rec["INVOICE_DESC"])
    print("Mobile Desc (60-80):", rec["MOBILE_DESC"])
    print("Long Desc:", rec["LONG_DESC1"])
    print("Audit Status:", audit["status"])
    print()
