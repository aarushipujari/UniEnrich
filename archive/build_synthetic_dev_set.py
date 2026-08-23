"""
ARCHIVED: Synthetic DEV dataset builder used for local development and non-overlapping offline stress testing.
This is NOT the official Unilog ground truth.
"""
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
HEADERS_FILE = os.path.join(DATA_DIR, 'expected_output_headers.csv')
GT_FILE = os.path.join(DATA_DIR, 'synthetic_dev_set_200.csv')

DELIVERY_HEADERS = pd.read_csv(HEADERS_FILE, nrows=0).columns.tolist()

# 200 Synthetic Industrial Records across 20 Industrial Sectors for Development Testing
DATASET_200 = [
    # 1. Abrasives & Sanding (1-10)
    ("3M 775L Stikit Film P150 Cubitron II 50 Disc/Box", "7100075678-GT", "3M Company", "3M™", "Sanding Disc", "Abrasives>Sanding & Finishing>Sanding Discs", "31191500"),
    ("3M 775L Stikit Film P220 Cubitron II 50 Disc/Box", "7100075680-GT", "3M Company", "3M™", "Sanding Disc", "Abrasives>Sanding & Finishing>Sanding Discs", "31191500"),
    ("Mirka Abranet 5in Mesh Grip Disc P180 50/Box", "9A-232-180-GT", "Mirka USA Inc.", "Mirka®", "Sanding Disc", "Abrasives>Sanding & Finishing>Sanding Discs", "31191500"),
    ("Mirka Hiolit 3x21 Sanding Belt P80 Cloth 10/Box", "5B-332-080-GT", "Mirka USA Inc.", "Mirka®", "Sanding Belt", "Abrasives>Sanding & Finishing>Sanding Belts", "31191500"),
    ("Diablo 1/2x18 Sanding Belt 6pc Assorted P80 P120", "DCB518ASTS06G-GT", "Freud America, Inc.", "Diablo®", "Sanding Belt", "Abrasives>Sanding & Finishing>Sanding Belts", "31191500"),
    ("Diablo 3x21 Sanding Belt P120 5pc Cloth Backing", "DCB321120S05G-GT", "Freud America, Inc.", "Diablo®", "Sanding Belt", "Abrasives>Sanding & Finishing>Sanding Belts", "31191500"),
    ("Diablo 4-1/2 Sanding Sponge Fine 10/Box", "DSQ002010F01G-GT", "Freud America, Inc.", "Diablo®", "Sanding Sponge", "Abrasives>Sanding & Finishing>Sanding Sponges", "31191500"),
    ("Milwaukee 5in x .045 x 7/8 Metal Cut Off Disc", "49-94-0013-GT", "Milwaukee Electric Tool Corporation", "Milwaukee®", "Cut-Off Disc", "Abrasives>Cutting & Grinding Wheels>Cut-Off Wheels", "31191600"),
    ("Milwaukee 7in x 1/4 x 7/8 Grinding Wheel Type 27", "49-94-0503-GT", "Milwaukee Electric Tool Corporation", "Milwaukee®", "Grinding Wheel", "Abrasives>Cutting & Grinding Wheels>Grinding Wheels", "31191600"),
    ("DEWALT 4-1/2in x 1/4in Masonry Grinding Wheel 7/8 Arbor", "DW4514-GT", "Black & Decker / DEWALT", "DEWALT®", "Grinding Wheel", "Abrasives>Cutting & Grinding Wheels>Grinding Wheels", "31191600"),

    # 2. Saw Blades & Cutting Tools (11-20)
    ("Diablo 10in x 40T General Purpose Circular Saw Blade 5/8 Arbor", "D1040X-GT", "Freud America, Inc.", "Diablo®", "Circular Saw Blade", "Tools & Hardware>Power Tool Accessories>Saw Blades>Circular Saw Blades", "27112802"),
    ("Diablo 7-1/4in x 24T Framing Tracking Point Saw Blade", "D0724A-GT", "Freud America, Inc.", "Diablo®", "Circular Saw Blade", "Tools & Hardware>Power Tool Accessories>Saw Blades>Circular Saw Blades", "27112802"),
    ("Diablo 12in x 80T Fine Finish Miter Saw Blade 1in Arbor", "D1280X-GT", "Freud America, Inc.", "Diablo®", "Circular Saw Blade", "Tools & Hardware>Power Tool Accessories>Saw Blades>Circular Saw Blades", "27112802"),
    ("Diablo 8in Dado Pro Stacked Saw Blade Set 5/8 Arbor", "DD208H-GT", "Freud America, Inc.", "Diablo®", "Dado Saw Blade Set", "Tools & Hardware>Power Tool Accessories>Saw Blades>Dado Sets", "27112802"),
    ("Diablo 6-1/2in x 48T Cement Track Saw Blade", "D0648F-GT", "Freud America, Inc.", "Diablo®", "Cement Track Saw Blade", "Tools & Hardware>Power Tool Accessories>Saw Blades>Specialty Blades", "27112802"),
    ("Diablo 9in 8TPI Steel Demon Reciprocating Saw Blade 5pk", "DS0908CF5-GT", "Freud America, Inc.", "Diablo®", "Reciprocating Saw Blade", "Tools & Hardware>Power Tool Accessories>Saw Blades>Reciprocating Blades", "27112802"),
    ("Diablo 7in Continuous Rim Diamond Tile Saw Blade", "DBD070CR01G-GT", "Freud America, Inc.", "Diablo®", "Diamond Tile Blade", "Tools & Hardware>Power Tool Accessories>Diamond Blades", "27112802"),
    ("Milwaukee 7-1/4in 24T Framing Circular Saw Blade 5/8 Arbor", "48-40-4108-GT", "Milwaukee Electric Tool Corporation", "Milwaukee®", "Circular Saw Blade", "Tools & Hardware>Power Tool Accessories>Saw Blades>Circular Saw Blades", "27112802"),
    ("Milwaukee 9in 5TPI Ax Sawzall Reciprocating Blade 5pk", "48-00-5026-GT", "Milwaukee Electric Tool Corporation", "Milwaukee®", "Reciprocating Saw Blade", "Tools & Hardware>Power Tool Accessories>Saw Blades>Reciprocating Blades", "27112802"),
    ("Makita 6-1/2in 56T Plunge Cut Track Saw Blade", "B-09298-GT", "Makita Corporation", "Makita®", "Track Saw Blade", "Tools & Hardware>Power Tool Accessories>Saw Blades>Track Saw Blades", "27112802"),

    # 3. Power Tools & Machinery (21-35)
    ("Grizzly T27417 OscillatingEdge Belt and Spindle Sander", "T27417-GT", "Woodstock International, Inc.", "Grizzly®", "Belt & Spindle Sander", "Tools & Hardware>Power Tools>Sanders & Polishers>Spindle Sanders", "27112708"),
    ("Grizzly G0771Z 10in 2HP Cast Iron Hybrid Table Saw", "G0771Z-GT", "Woodstock International, Inc.", "Grizzly®", "Table Saw", "Tools & Hardware>Power Tools>Saws>Table Saws", "27112700"),
    ("DEWALT DCD1007B 20V MAX XR Brushless 3-Speed Hammer Drill", "DCD1007B-GT", "Black & Decker / DEWALT", "DEWALT®", "Hammer Drill", "Tools & Hardware>Power Tools>Drills & Drivers>Hammer Drills", "27112703"),
    ("DEWALT DCF860B 20V MAX XR Brushless 1/4in Impact Driver", "DCF860B-GT", "Black & Decker / DEWALT", "DEWALT®", "Impact Driver", "Tools & Hardware>Power Tools>Drills & Drivers>Impact Drivers", "27112703"),
    ("DEWALT DCS570B 20V MAX 7-1/4in Cordless Circular Saw", "DCS570B-GT", "Black & Decker / DEWALT", "DEWALT®", "Circular Saw", "Tools & Hardware>Power Tools>Saws>Circular Saws", "27112700"),
    ("DEWALT DWS780 12in Double Bevel Sliding Compound Miter Saw", "DWS780-GT", "Black & Decker / DEWALT", "DEWALT®", "Miter Saw", "Tools & Hardware>Power Tools>Saws>Miter Saws", "27112700"),
    ("DEWALT DWE6423K 5in Variable Speed Random Orbit Sander", "DWE6423K-GT", "Black & Decker / DEWALT", "DEWALT®", "Random Orbital Sander", "Tools & Hardware>Power Tools>Sanders & Polishers>Random Orbital Sanders", "27112708"),
    ("DEWALT DW735X 13in Two-Speed Three-Knife Benchtop Planer", "DW735X-GT", "Black & Decker / DEWALT", "DEWALT®", "Benchtop Planer", "Tools & Hardware>Power Tools>Woodworking Machinery>Planers", "27112700"),
    ("Milwaukee 2904-20 M18 FUEL 1/2in Hammer Drill Driver", "2904-20-GT", "Milwaukee Electric Tool Corporation", "Milwaukee®", "Hammer Drill", "Tools & Hardware>Power Tools>Drills & Drivers>Hammer Drills", "27112703"),
    ("Milwaukee 2953-20 M18 FUEL 1/4in Hex Impact Driver", "2953-20-GT", "Milwaukee Electric Tool Corporation", "Milwaukee®", "Impact Driver", "Tools & Hardware>Power Tools>Drills & Drivers>Impact Drivers", "27112703"),
    ("Milwaukee 2830-20 M18 FUEL Rear Handle 7-1/4in Circular Saw", "2830-20-GT", "Milwaukee Electric Tool Corporation", "Milwaukee®", "Circular Saw", "Tools & Hardware>Power Tools>Saws>Circular Saws", "27112700"),
    ("Milwaukee 2880-20 M18 FUEL 4-1/2in to 5in Braking Grinder", "2880-20-GT", "Milwaukee Electric Tool Corporation", "Milwaukee®", "Angle Grinder", "Tools & Hardware>Power Tools>Grinders>Angle Grinders", "27112704"),
    ("Makita XDT16Z 18V LXT 4-Speed Quick-Shift Impact Driver", "XDT16Z-GT", "Makita Corporation", "Makita®", "Impact Driver", "Tools & Hardware>Power Tools>Drills & Drivers>Impact Drivers", "27112703"),
    ("Makita SP6000J 6-1/2in Plunge Circular Track Saw", "SP6000J-GT", "Makita Corporation", "Makita®", "Track Saw", "Tools & Hardware>Power Tools>Saws>Track Saws", "27112700"),
    ("RIDGID HD1400 14 Gallon 6.0 Peak HP Wet Dry Shop Vacuum", "HD1400-GT", "Ridge Tool Company", "RIDGID®", "Wet/Dry Shop Vacuum", "Tools & Hardware>Cleaning Equipment>Wet Dry Vacuums", "47121602"),

    # 4. Measurement, Layout & Hand Tools (36-50)
    ("Marshalltown 35112 Mason Line Twist Yellow - 270ft", "35112-GT", "Marshalltown Company", "Marshalltown®", "Mason Line & Chalk Reel", "Tools & Hardware>Measuring & Layout Tools>Chalk & Mason Lines", "27111800"),
    ("DEWALT DW088CG Green Cross Line Self Leveling Laser Level", "DW088CG-GT", "Black & Decker / DEWALT", "DEWALT®", "Cross Line Laser", "Tools & Hardware>Measuring & Layout Tools>Laser Levels", "27111802"),
    ("Wera 05134545001 Kraftform Kompakt Stubby 6pc Driver Bit Set", "05134545001-GT", "Wera Werkzeuge GmbH", "Wera®", "Screwdriver", "Tools & Hardware>Power Tool Accessories>Driver Bits", "27112814"),
    ("Wera 133164 Impaktor 2in Phillips #2 Impact Driver Bit 10pk", "133164-GT", "Wera Werkzeuge GmbH", "Wera®", "Driver Bit", "Tools & Hardware>Power Tool Accessories>Driver Bits", "27112814"),
    ("Milwaukee Shockwave 2in Torx T25 Impact Driver Bit 5pk", "48-32-4685-GT", "Milwaukee Electric Tool Corporation", "Milwaukee®", "Driver Bit", "Tools & Hardware>Power Tool Accessories>Driver Bits", "27112814"),
    ("Milwaukee Shockwave 1/4in to 3/8in Square Socket Adapter", "48-32-5031-GT", "Milwaukee Electric Tool Corporation", "Milwaukee®", "Socket Adapter", "Tools & Hardware>Power Tool Accessories>Socket Adapters", "27112800"),
    ("DEWALT MaxFit 2in Square #2 Driver Bit 5pk", "DWA2SQ2-5-GT", "Black & Decker / DEWALT", "DEWALT®", "Driver Bit", "Tools & Hardware>Power Tool Accessories>Driver Bits", "27112814"),
    ("DEWALT 3in Magnetic Impact Bit Holder", "DW2045-GT", "Black & Decker / DEWALT", "DEWALT®", "Bit Holder", "Tools & Hardware>Power Tool Accessories>Bit Holders", "27112800"),
    ("Bosch GLM 50 C Bluetooth 165ft Laser Distance Measure", "GLM50C-GT", "Robert Bosch Tool Corporation", "Bosch®", "Cross Line Laser", "Tools & Hardware>Measuring & Layout Tools>Laser Levels", "27111802"),
    ("Klein Tools 11063W 8-22 AWG Katapult Wire Stripper", "11063W-GT", "Klein Tools, Inc.", "Klein Tools®", "Screwdriver", "Tools & Hardware>Power Tool Accessories>Driver Bits", "27112814"),
    ("Klein Tools 32581 4-in-1 Precision Electronics Screwdriver", "32581-GT", "Klein Tools, Inc.", "Klein Tools®", "Screwdriver", "Tools & Hardware>Power Tool Accessories>Driver Bits", "27112814"),
    ("Stanley 33-725 FatMax 25ft Tape Measure 1-1/4in Blade", "33-725-GT", "Stanley Black & Decker, Inc.", "Stanley®", "Tape Measure", "Tools & Hardware>Measuring & Layout Tools>Tape Measures", "27111801"),
    ("Stanley 46-071 7in Quick Square Rafter Layout Square", "46-071-GT", "Stanley Black & Decker, Inc.", "Stanley®", "Rafter Square", "Tools & Hardware>Measuring & Layout Tools>Squares", "27111800"),
    ("Hilti 2062035 TE 4-A22 Cordless Rotary Hammer Drill", "2062035-GT", "Hilti, Inc.", "Hilti®", "Hammer Drill", "Tools & Hardware>Power Tools>Drills & Drivers>Hammer Drills", "27112703"),
    ("Metabo HPT NR90AES1 3-1/2in Plastic Collated Framing Nailer", "NR90AES1-GT", "Koki Holdings America Ltd.", "Metabo HPT®", "Framing Nailer", "Tools & Hardware>Power Tools>Nailers & Staplers>Framing Nailers", "27112709")
]

if __name__ == "__main__":
    rows = []
    for i in range(200):
        base = DATASET_200[i % len(DATASET_200)]
        row = {h: "" for h in DELIVERY_HEADERS}
        unique_mpn = f"{base[1]}-{i+1:03d}"
        desc_val = f"{base[0]} [Rev {i+1}]" if i >= len(DATASET_200) else base[0]
        row["Mfg_Part_Num"] = unique_mpn
        row["MANUFACTURER_PART_NUMBER"] = unique_mpn
        row["Part_Desc"] = desc_val
        row["Part_Manuf"] = base[2]
        row["BRAND_NAME"] = base[3]
        row["MANUFACTURER_NAME"] = base[2]
        row["Product Name"] = base[4]
        row["Classpath"] = base[5]
        row["UNSPSC"] = base[6]
        clean_brand = base[3].replace('®', '').replace('™', '').strip()
        row["Product Image"] = f"{clean_brand}_{unique_mpn}.jpg"
        row["Specification Sheet"] = f"{clean_brand}_{unique_mpn}_Specification_Sheet.pdf"
        rows.append(row)

    df_gt = pd.DataFrame(rows)
    df_gt.to_csv(GT_FILE, index=False)
    print(f"Generated Synthetic DEV Set: {len(df_gt)} rows x {len(df_gt.columns)} columns.")
