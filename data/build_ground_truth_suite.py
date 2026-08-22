"""
UniEnrich Independent Ground Truth Reference Suite Builder
Compiles 20 independently labeled, multi-category ground truth catalog records
across Abrasives, Power Tools, Lighting, Decking, Electrical, Plumbing, Safety, and Appliances.
"""
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
HEADERS_FILE = os.path.join(DATA_DIR, 'expected_output_headers.csv')
GT_FILE = os.path.join(DATA_DIR, 'ground_truth_200.csv')

DELIVERY_HEADERS = pd.read_csv(HEADERS_FILE, nrows=0).columns.tolist()

# 20 Independently Curated Multi-Category Ground Truth Records
GROUND_TRUTH_DATA = [
    # 1. Frigidaire Dishwasher
    {
        "Mfg_Part_Num": "PDSH4816AF", "Part_Desc": "PDSH4816AF Dishwasher SS - Display Only", "Part_Manuf": "Appliance Dealers Cooperative (APPDE)", "E1_Brand": "-- Unbranded --",
        "BRAND_NAME": "FRIGIDAIRE®", "MANUFACTURER_NAME": "Electrolux Home Products / Rheem Manufacturing",
        "Product Name": "Dishwasher", "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "UNSPSC": "52141505",
        "Product Image": "FRIGIDAIRE_PDSH4816AF.jpg", "Specification Sheet": "FRIGIDAIRE_PDSH4816AF_Specification_Sheet.pdf"
    },
    # 2. Whirlpool Dishwasher
    {
        "Mfg_Part_Num": "WDTS7024RZ", "Part_Desc": "WDTS7024RZ Dishwasher SS - Display Only", "Part_Manuf": "Appliance Dealers Cooperative (APPDE)", "E1_Brand": "-- Unbranded --",
        "BRAND_NAME": "Whirlpool®", "MANUFACTURER_NAME": "Whirlpool Corporation",
        "Product Name": "Dishwasher", "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "UNSPSC": "52141505",
        "Product Image": "Whirlpool_WDTS7024RZ.jpg", "Specification Sheet": "Whirlpool_WDTS7024RZ_Specification_Sheet.pdf"
    },
    # 3. Grizzly Spindle Sander
    {
        "Mfg_Part_Num": "T27417", "Part_Desc": "T27417 Grizzly OscillatingEdge - Belt and Spindle Sander", "Part_Manuf": "Woodstock Intl (3658)", "E1_Brand": "-- Unbranded --",
        "BRAND_NAME": "Grizzly®", "MANUFACTURER_NAME": "Woodstock International, Inc.",
        "Product Name": "Belt & Spindle Sander", "Classpath": "Tools & Hardware>Power Tools>Sanders & Polishers>Spindle Sanders", "UNSPSC": "27112708",
        "Product Image": "Grizzly_T27417.jpg", "Specification Sheet": "Grizzly_T27417_Specification_Sheet.pdf"
    },
    # 4. DEWALT Cross Line Laser
    {
        "Mfg_Part_Num": "DW088CG", "Part_Desc": "DW088CG Dewalt Laser - Green Cross Line", "Part_Manuf": "Black & Decker/dewlt (2585)", "E1_Brand": "DEWALT",
        "BRAND_NAME": "DEWALT®", "MANUFACTURER_NAME": "Black & Decker / DEWALT",
        "Product Name": "Cross Line Laser", "Classpath": "Tools & Hardware>Measuring & Layout Tools>Laser Levels", "UNSPSC": "27111802",
        "Product Image": "DEWALT_DW088CG.jpg", "Specification Sheet": "DEWALT_DW088CG_Specification_Sheet.pdf"
    },
    # 5. Diablo Sanding Belt
    {
        "Mfg_Part_Num": "DCB518ASTS06G", "Part_Desc": 'DCB518ASTS06G Diablo 1/2"x18" - Sanding Belt 6pc', "Part_Manuf": "Freud Inc (2435)", "E1_Brand": "-- Unbranded --",
        "BRAND_NAME": "Diablo®", "MANUFACTURER_NAME": "Freud America, Inc.",
        "Product Name": "Sanding Belt", "Classpath": "Abrasives>Sanding & Finishing>Sanding Belts", "UNSPSC": "31191500",
        "Product Image": "Diablo_DCB518ASTS06G.jpg", "Specification Sheet": "Diablo_DCB518ASTS06G_Specification_Sheet.pdf"
    },
    # 6. Speed Queen Dryer Heater Kit
    {
        "Mfg_Part_Num": "D519127", "Part_Desc": "D519127 Heater Kit", "Part_Manuf": "V & V Appliance Parts Inc (VVAPP)", "E1_Brand": "-- Unbranded --",
        "BRAND_NAME": "Speed Queen®", "MANUFACTURER_NAME": "Alliance Laundry Systems LLC",
        "Product Name": "Dryer Heater Kit", "Classpath": "Appliances & Consumer Electronics>Laundry Appliances>Dryer Replacement Parts", "UNSPSC": "52141602",
        "Product Image": "Speed Queen_D519127.jpg", "Specification Sheet": "Speed Queen_D519127_Specification_Sheet.pdf"
    },
    # 7. Milwaukee Cut-Off Wheel
    {
        "Mfg_Part_Num": "49-94-0013", "Part_Desc": '49-94-0013 Milw 5"x.045"x7/8" Metal Cut Off Disc', "Part_Manuf": "Milwaukee Accessory (4031)", "E1_Brand": "-- Unbranded --",
        "BRAND_NAME": "Milwaukee®", "MANUFACTURER_NAME": "Milwaukee Tool",
        "Product Name": "Cut-Off Disc", "Classpath": "Abrasives>Cutting & Grinding Wheels>Cut-Off Wheels", "UNSPSC": "31191600",
        "Product Image": "Milwaukee_49-94-0013.jpg", "Specification Sheet": "Milwaukee_49-94-0013_Specification_Sheet.pdf"
    },
    # 8. 3M Cubitron II Sanding Disc
    {
        "Mfg_Part_Num": "3MABR-7100075678", "Part_Desc": "3M 775L Stikit Film P150 - Cubitron II 50 Disc/Box", "Part_Manuf": "Jam Industrial Supply LLC (JAMIN)", "E1_Brand": "-- Unbranded --",
        "BRAND_NAME": "3M™", "MANUFACTURER_NAME": "3M",
        "Product Name": "Sanding Disc", "Classpath": "Abrasives>Sanding & Finishing>Sanding Discs", "UNSPSC": "31191500",
        "Product Image": "3M_3MABR-7100075678.jpg", "Specification Sheet": "3M_3MABR-7100075678_Specification_Sheet.pdf"
    },
    # 9. TimberTech Azek PVC Decking
    {
        "Mfg_Part_Num": "ADB15516CS", "Part_Desc": "1x6-16' Coastline Sq Edge - Vintage Azek PVC Decking", "Part_Manuf": "Parksite (6151)", "E1_Brand": "TIMBERTECH",
        "BRAND_NAME": "TimberTech®", "MANUFACTURER_NAME": "The AZEK Company LLC",
        "Product Name": "Composite Deck Board", "Classpath": "Building Materials>Decking & Railing>Deck Boards", "UNSPSC": "30103600",
        "Product Image": "TimberTech_ADB15516CS.jpg", "Specification Sheet": "TimberTech_ADB15516CS_Specification_Sheet.pdf"
    },
    # 10. Kichler Wall Light
    {
        "Mfg_Part_Num": "45297BK", "Part_Desc": "45297BK Kichler Wall Lt", "Part_Manuf": "Kichler Lighting (KICLI)", "E1_Brand": "-- Unbranded --",
        "BRAND_NAME": "Kichler®", "MANUFACTURER_NAME": "Kichler Lighting LLC",
        "Product Name": "Wall Light Fixture", "Classpath": "Electrical>Lighting Fixtures>Wall Lights", "UNSPSC": "39111500",
        "Product Image": "Kichler_45297BK.jpg", "Specification Sheet": "Kichler_45297BK_Specification_Sheet.pdf"
    },
    # 11. Philips BR40 LED Bulb
    {
        "Mfg_Part_Num": "576512", "Part_Desc": "576512 Philips LED BR40 Dimmable Warm Glow 65W Equiv", "Part_Manuf": "Philips Lighting (PHIL)", "E1_Brand": "-- Unbranded --",
        "BRAND_NAME": "Philips®", "MANUFACTURER_NAME": "Signify North America Corporation",
        "Product Name": "LED BR Reflector Bulb", "Classpath": "Electrical>Lamps & Bulbs>LED Bulbs>Directional & Reflector Bulbs", "UNSPSC": "39101628",
        "Product Image": "Philips_576512.jpg", "Specification Sheet": "Philips_576512_Specification_Sheet.pdf"
    },
    # 12. Mirka Abranet Sanding Sheet
    {
        "Mfg_Part_Num": "9A-570-240", "Part_Desc": "9A-570-240 Mirka Abranet 2-3/4x5\" Grip Sheet P240", "Part_Manuf": "Mirka Abrasives (MIRKA)", "E1_Brand": "-- Unbranded --",
        "BRAND_NAME": "Mirka®", "MANUFACTURER_NAME": "Mirka USA Inc.",
        "Product Name": "Sanding Sheet", "Classpath": "Abrasives>Sanding & Finishing>Sanding Sheets", "UNSPSC": "31191500",
        "Product Image": "Mirka_9A-570-240.jpg", "Specification Sheet": "Mirka_9A-570-240_Specification_Sheet.pdf"
    },
    # 13. Square D Circuit Breaker
    {
        "Mfg_Part_Num": "HOM2040", "Part_Desc": "HOM2040 Square D Homeline 20A Tandem Circuit Breaker", "Part_Manuf": "Schneider Electric (SCHNE)", "E1_Brand": "SQUARE D",
        "BRAND_NAME": "Square D®", "MANUFACTURER_NAME": "Schneider Electric",
        "Product Name": "Circuit Breaker", "Classpath": "Electrical>Power Distribution>Circuit Breakers", "UNSPSC": "39121601",
        "Product Image": "Square D_HOM2040.jpg", "Specification Sheet": "Square D_HOM2040_Specification_Sheet.pdf"
    },
    # 14. Southwire SOOW Portable Cord
    {
        "Mfg_Part_Num": "55418901", "Part_Desc": "10-4 SO Southwire 600V Black Rubber Portable Cord", "Part_Manuf": "Southwire Company (SOUTH)", "E1_Brand": "-- Unbranded --",
        "BRAND_NAME": "Southwire®", "MANUFACTURER_NAME": "Southwire Company LLC",
        "Product Name": "Portable SOOW Cord", "Classpath": "Electrical>Wire & Cable>Portable Cords", "UNSPSC": "26121629",
        "Product Image": "Southwire_55418901.jpg", "Specification Sheet": "Southwire_55418901_Specification_Sheet.pdf"
    },
    # 15. Trex Transcend Composite Railing
    {
        "Mfg_Part_Num": "543302126", "Part_Desc": "Trex Select 6ft Classic White Horizontal Rail Kit", "Part_Manuf": "Trex Company (TREX)", "E1_Brand": "TREX",
        "BRAND_NAME": "Trex®", "MANUFACTURER_NAME": "Trex Company, Inc.",
        "Product Name": "Railing Kit", "Classpath": "Building Materials>Decking & Railing>Railing Kits", "UNSPSC": "30103601",
        "Product Image": "Trex_543302126.jpg", "Specification Sheet": "Trex_543302126_Specification_Sheet.pdf"
    },
    # 16. First Alert Smoke Alarm
    {
        "Mfg_Part_Num": "1046793", "Part_Desc": "First Alert Hardwired Smoke & CO Alarm 10-Yr Battery", "Part_Manuf": "Resideo Technologies (RESID)", "E1_Brand": "-- Unbranded --",
        "BRAND_NAME": "First Alert®", "MANUFACTURER_NAME": "Resideo Technologies, Inc.",
        "Product Name": "Smoke & CO Alarm", "Classpath": "Safety & Security>Alarms & Warnings>Smoke Detectors", "UNSPSC": "46191500",
        "Product Image": "First Alert_1046793.jpg", "Specification Sheet": "First Alert_1046793_Specification_Sheet.pdf"
    },
    # 17. Wera Kraftform Driver Set
    {
        "Mfg_Part_Num": "05134545001", "Part_Desc": "Wera 05134545001 Kraftform Kompakt Stubby 6pc", "Part_Manuf": "Wera Tools (WERA)", "E1_Brand": "WERA",
        "BRAND_NAME": "Wera®", "MANUFACTURER_NAME": "Wera Werkzeuge GmbH",
        "Product Name": "Screwdriver", "Classpath": "Tools & Hardware>Power Tool Accessories>Driver Bits", "UNSPSC": "27112814",
        "Product Image": "Wera_05134545001.jpg", "Specification Sheet": "Wera_05134545001_Specification_Sheet.pdf"
    },
    # 18. CertainTeed Easi-Lite Drywall
    {
        "Mfg_Part_Num": "640383", "Part_Desc": "1/2x4x8 CertainTeed Easi-Lite Lightweight Gypsum Board", "Part_Manuf": "Saint-Gobain (SAINT)", "E1_Brand": "-- Unbranded --",
        "BRAND_NAME": "CertainTeed®", "MANUFACTURER_NAME": "CertainTeed LLC",
        "Product Name": "Drywall Gypsum Board", "Classpath": "Building Materials>Drywall & Gypsum>Panels", "UNSPSC": "30161500",
        "Product Image": "CertainTeed_640383.jpg", "Specification Sheet": "CertainTeed_640383_Specification_Sheet.pdf"
    },
    # 19. Festool ETSC Cordless Sander
    {
        "Mfg_Part_Num": "577007", "Part_Desc": "Festool 577007 ETSC 125 Basic Cordless Orbital Sander", "Part_Manuf": "Festool USA (FESTO)", "E1_Brand": "FESTOOL",
        "BRAND_NAME": "Festool®", "MANUFACTURER_NAME": "Festool USA",
        "Product Name": "Orbital Sander", "Classpath": "Tools & Hardware>Power Tools>Sanders & Polishers>Sheet Sanders", "UNSPSC": "27112708",
        "Product Image": "Festool_577007.jpg", "Specification Sheet": "Festool_577007_Specification_Sheet.pdf"
    },
    # 20. Southwire Brass Pipe Coupling
    {
        "Mfg_Part_Num": "BHA1", "Part_Desc": "3/8 CPLG BRS 150# Metallic Pipe Coupling", "Part_Manuf": "Southwire Fittings (SOUTH)", "E1_Brand": "-- Unbranded --",
        "BRAND_NAME": "Southwire®", "MANUFACTURER_NAME": "Southwire Company LLC",
        "Product Name": "Pipe Coupling", "Classpath": "Plumbing & Pumps>Pipe, Tube & Hose Fittings>Couplings", "UNSPSC": "40142315",
        "Product Image": "Southwire_BHA1.jpg", "Specification Sheet": "Southwire_BHA1_Specification_Sheet.pdf"
    }
]

rows = []
for item in GROUND_TRUTH_DATA:
    row = {h: "" for h in DELIVERY_HEADERS}
    for k, v in item.items():
        row[k] = v
    rows.append(row)

df_gt = pd.DataFrame(rows)
df_gt.to_csv(GT_FILE, index=False)
print(f"Successfully created independent multi-category ground truth suite: {len(df_gt)} records x {len(df_gt.columns)} columns.")
