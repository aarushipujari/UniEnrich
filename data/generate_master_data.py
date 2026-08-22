"""
Script to create master reference data files:
- decimal_fraction.json
- uom_standards.json
- master_brands.json
- category_lovs.json
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '')
os.makedirs(DATA_DIR, exist_ok=True)

# 1. Decimal to Fraction Lookup Table (all 63 64ths + compound decimals)
decimal_fraction_map = {
    0.015625: "1/64", 0.03125: "1/32", 0.046875: "3/64", 0.0625: "1/16",
    0.078125: "5/64", 0.09375: "3/32", 0.109375: "7/64", 0.125: "1/8",
    0.140625: "9/64", 0.15625: "5/32", 0.171875: "11/64", 0.1875: "3/16",
    0.203125: "13/64", 0.21875: "7/32", 0.234375: "15/64", 0.25: "1/4",
    0.265625: "17/64", 0.28125: "9/32", 0.296875: "19/64", 0.3125: "5/16",
    0.328125: "21/64", 0.34375: "11/32", 0.359375: "23/64", 0.375: "3/8",
    0.390625: "25/64", 0.40625: "13/32", 0.421875: "27/64", 0.4375: "7/16",
    0.453125: "29/64", 0.46875: "15/32", 0.484375: "31/64", 0.5: "1/2",
    0.515625: "33/64", 0.53125: "17/32", 0.546875: "35/64", 0.5625: "9/16",
    0.578125: "37/64", 0.59375: "19/32", 0.609375: "39/64", 0.625: "5/8",
    0.640625: "41/64", 0.65625: "21/32", 0.671875: "43/64", 0.6875: "11/16",
    0.703125: "45/64", 0.71875: "23/32", 0.734375: "47/64", 0.75: "3/4",
    0.765625: "49/64", 0.78125: "25/32", 0.796875: "51/64", 0.8125: "13/16",
    0.828125: "53/64", 0.84375: "27/32", 0.859375: "55/64", 0.875: "7/8",
    0.890625: "57/64", 0.90625: "29/32", 0.921875: "59/64", 0.9375: "15/16",
    0.953125: "61/64", 0.96875: "31/32", 0.984375: "63/64",
    # common decimal abbreviations in industrial catalogs (e.g. .045, .040, .131)
    0.04: "3/64", 0.045: "3/64", 0.131: "1/8", 0.109: "7/64", 0.437: "7/16", 0.438: "7/16"
}

with open(os.path.join(DATA_DIR, 'decimal_fraction.json'), 'w') as f:
    json.dump({str(k): v for k, v in decimal_fraction_map.items()}, f, indent=2)

# 2. Approved Master UOM Standards & Normalization Rules
uom_standards = {
    "approved_units": [
        "in", "ft", "yd", "mm", "cm", "m",
        "V", "A", "W", "kW", "kW-hr", "Hz", "dBA", "deg", "CCT", "K", "lm",
        "oz", "lb", "ton", "g", "kg",
        "CF", "gal", "qt", "pt", "L", "ml",
        "psi", "bar", "RPM", "TPI", "GA", "Ah", "HP",
        "pc", "pk", "ct", "box", "bdl", "set", "pair", "roll"
    ],
    "unit_aliases": {
        "inch": "in", "inches": "in", "in.": "in", "\"": "in",
        "feet": "ft", "foot": "ft", "ft.": "ft", "'": "ft",
        "volt": "V", "volts": "V", "v": "V", "VAC": "V", "VDC": "V",
        "amp": "A", "amps": "A", "amperes": "A", "a": "A",
        "watt": "W", "watts": "W", "w": "W",
        "decibel": "dBA", "decibels": "dBA", "dba": "dBA", "db": "dBA",
        "kelvin": "K", "k": "K",
        "lumen": "lm", "lumens": "lm",
        "gauge": "GA", "ga": "GA", "ga.": "GA",
        "teeth per inch": "TPI", "tpi": "TPI",
        "piece": "pc", "pieces": "pc", "pc.": "pc", "pcs": "pc",
        "pack": "pk", "packs": "pk", "pk.": "pk",
        "count": "ct", "ct.": "ct",
        "gallon": "gal", "gallons": "gal",
        "ounce": "oz", "ounces": "oz", "oz.": "oz",
        "pound": "lb", "pounds": "lb", "lbs": "lb"
    }
}

with open(os.path.join(DATA_DIR, 'uom_standards.json'), 'w') as f:
    json.dump(uom_standards, f, indent=2)

# 3. Master Brand & Manufacturer Canonical Database
master_brands = {
    "aliases": {
        "milw": "Milwaukee",
        "milwaukee": "Milwaukee",
        "milwaukee accessory": "Milwaukee",
        "dewalt": "DEWALT",
        "black & decker/dewlt": "DEWALT",
        "makita": "Makita",
        "makita usa inc": "Makita",
        "freud": "Diablo",
        "freud inc": "Diablo",
        "diablo": "Diablo",
        "3m": "3M",
        "3 m co": "3M",
        "jam industrial supply llc": "3M",
        "mirka": "Mirka",
        "mirka abrasives inc": "Mirka",
        "festool": "Festool",
        "festool usa": "Festool",
        "trex": "Trex",
        "timbertech": "TimberTech",
        "azek": "TimberTech",
        "parksite": "TimberTech",
        "boise cascade building materials": "Trex",
        "u s lumber": "Trex",
        "kichler": "Kichler",
        "kichler lighting": "Kichler",
        "satco": "Satco",
        "satco prod inc": "Satco",
        "nuvo": "Satco",
        "philips": "Philips",
        "phillips lighting": "Philips",
        "wiz": "WiZ",
        "provia": "ProVia",
        "united window & door": "United Window & Door",
        "velux": "Velux",
        "velux america inc": "Velux",
        "speed queen": "Speed Queen",
        "sq": "Speed Queen",
        "ge": "GE Appliances",
        "ge appliances": "GE Appliances",
        "cafe": "Café",
        "café": "Café",
        "lg": "LG",
        "frigidaire": "FRIGIDAIRE",
        "whirlpool": "Whirlpool",
        "kitchen aid": "KitchenAid",
        "kitchenaid": "KitchenAid",
        "beko": "Beko",
        "element": "Element",
        "first alert": "First Alert",
        "brk": "BRK",
        "first alert - b r k brands": "First Alert",
        "wera": "Wera",
        "wera tools na inc": "Wera",
        "kreg": "Kreg",
        "kreg tool company": "Kreg",
        "irwin": "Irwin",
        "irwin industrial tools": "Irwin",
        "senco": "Senco",
        "senco products inc": "Senco",
        "dremel": "Dremel",
        "robt bosch tool corp": "Bosch",
        "bosch": "Bosch",
        "oliver": "Oliver",
        "oliver machinery company": "Oliver Machinery",
        "grizzly": "Grizzly",
        "woodstock intl": "Grizzly",
        "saw stop llc": "SawStop",
        "sawstop": "SawStop",
        "bow products": "Bow Products",
        "leviton": "Leviton",
        "leviton mfg co": "Leviton",
        "square d": "Square D",
        "square d con prod dv": "Square D",
        "southwire": "Southwire",
        "southwire/g turner": "Southwire",
        "hager": "Hager",
        "hager hinge co": "Hager",
        "hunter": "Hunter",
        "hunter fan co": "Hunter Fan",
        "jameshardie": "James Hardie",
        "lp smartside": "LP SmartSide",
        "certainteed": "CertainTeed",
        "certainteed gypsum": "CertainTeed",
        "prebena": "Prebena",
        "malco": "Malco",
        "malco prod": "Malco",
        "vessel": "Vessel",
        "vessel tools usa inc": "Vessel",
        "woodpeckers": "Woodpeckers",
        "woodpeckers inc": "Woodpeckers",
        "marshalltown": "Marshalltown",
        "marshalltown trowel": "Marshalltown",
        "edge eyewear": "Edge Safety",
        "edge eyewear inc": "Edge Safety",
        "edge safety": "Edge Safety",
        "cooper wiring devices": "Cooper Lighting",
        "cooper lighting": "Cooper Lighting",
        "satco prod inc (5573)": "Satco",
        "lutron": "Lutron",
        "fenton bros electric inc": "Lutron",
        "prime": "Prime",
        "prime wire & cable": "Prime Wire & Cable",
        "feit electric": "Feit Electric",
        "gt-lite": "GT-Lite",
        "schumacher": "Schumacher",
        "stealthmounts": "StealthMounts",
        "metalmark industrial inc": "StealthMounts",
        "carlon": "Carlon",
        "thomas & betts": "Carlon",
        "streamlight": "Streamlight",
        "acg brands": "NEBO",
        "police security": "Police Security",
        "rees cast stone": "Rees Cast Stone",
        "rees cast stone company": "Rees Cast Stone",
        "millertech energy solutions": "MillerTech",
        "tech gear 5.7 inc": "UTW Pro",
        "sabre": "Sabre",
        "national nail corp": "National Nail",
        "cmt usa inc": "CMT",
        "jpw industries": "JET",
        "king canada inc": "King Canada"
    },
    "canonical": {
        "Milwaukee": {
            "mfg_name": "Milwaukee Electric Tool Corporation",
            "brand_name": "Milwaukee®",
            "mfg_code": "4031",
            "brand_code": "MILW"
        },
        "DEWALT": {
            "mfg_name": "Black & Decker / DEWALT",
            "brand_name": "DEWALT®",
            "mfg_code": "2585",
            "brand_code": "DEWLT"
        },
        "Makita": {
            "mfg_name": "Makita U.S.A., Inc.",
            "brand_name": "Makita®",
            "mfg_code": "5142",
            "brand_code": "MAKIT"
        },
        "Diablo": {
            "mfg_name": "Freud America, Inc.",
            "brand_name": "Diablo®",
            "mfg_code": "2435",
            "brand_code": "DIAB"
        },
        "3M": {
            "mfg_name": "3M Company",
            "brand_name": "3M™",
            "mfg_code": "5293",
            "brand_code": "3M"
        },
        "Mirka": {
            "mfg_name": "Mirka Abrasives, Inc.",
            "brand_name": "Mirka®",
            "mfg_code": "MIRUS",
            "brand_code": "MIRK"
        },
        "Festool": {
            "mfg_name": "Festool USA LLC",
            "brand_name": "Festool®",
            "mfg_code": "FESTO",
            "brand_code": "FEST"
        },
        "Trex": {
            "mfg_name": "Trex Company, Inc.",
            "brand_name": "Trex®",
            "mfg_code": "3073",
            "brand_code": "TREX"
        },
        "TimberTech": {
            "mfg_name": "The AZEK Company Inc.",
            "brand_name": "TimberTech®",
            "mfg_code": "6151",
            "brand_code": "TIMB"
        },
        "Kichler": {
            "mfg_name": "Kichler Lighting LLC",
            "brand_name": "Kichler®",
            "mfg_code": "KICLI",
            "brand_code": "KICH"
        },
        "Satco": {
            "mfg_name": "Satco Products, Inc.",
            "brand_name": "Satco®",
            "mfg_code": "5573",
            "brand_code": "SATC"
        },
        "Philips": {
            "mfg_name": "Signify North America Corporation",
            "brand_name": "Philips®",
            "mfg_code": "5831",
            "brand_code": "PHIL"
        },
        "WiZ": {
            "mfg_name": "Signify North America Corporation",
            "brand_name": "WiZ®",
            "mfg_code": "5831",
            "brand_code": "WIZ"
        },
        "ProVia": {
            "mfg_name": "ProVia LLC",
            "brand_name": "ProVia®",
            "mfg_code": "PRODO",
            "brand_code": "PROV"
        },
        "United Window & Door": {
            "mfg_name": "United Window & Door Manufacturing, Inc.",
            "brand_name": "United Window & Door®",
            "mfg_code": "UNIWI",
            "brand_code": "UNWD"
        },
        "Velux": {
            "mfg_name": "Velux America Inc.",
            "brand_name": "VELUX®",
            "mfg_code": "VELAM",
            "brand_code": "VELX"
        },
        "FRIGIDAIRE": {
            "mfg_name": "Electrolux Home Products / Rheem Manufacturing",
            "brand_name": "FRIGIDAIRE®",
            "mfg_code": "APPDE",
            "brand_code": "FRIG"
        },
        "Whirlpool": {
            "mfg_name": "Whirlpool Corporation",
            "brand_name": "Whirlpool®",
            "mfg_code": "APPDE",
            "brand_code": "WHRL"
        },
        "GE Appliances": {
            "mfg_name": "GE Appliances, a Haier company",
            "brand_name": "GE®",
            "mfg_code": "APPDE",
            "brand_code": "GEAP"
        },
        "Café": {
            "mfg_name": "GE Appliances, a Haier company",
            "brand_name": "Café™",
            "mfg_code": "APPDE",
            "brand_code": "CAFE"
        },
        "KitchenAid": {
            "mfg_name": "Whirlpool Corporation",
            "brand_name": "KitchenAid®",
            "mfg_code": "APPDE",
            "brand_code": "KTCH"
        },
        "LG": {
            "mfg_name": "LG Electronics U.S.A., Inc.",
            "brand_name": "LG®",
            "mfg_code": "APPDE",
            "brand_code": "LGEL"
        },
        "Speed Queen": {
            "mfg_name": "Alliance Laundry Systems LLC",
            "brand_name": "Speed Queen®",
            "mfg_code": "APPDE",
            "brand_code": "SPDQ"
        },
        "Beko": {
            "mfg_name": "Beko US, Inc.",
            "brand_name": "Beko®",
            "mfg_code": "APPDE",
            "brand_code": "BEKO"
        },
        "Element": {
            "mfg_name": "Element Appliances",
            "brand_name": "Element®",
            "mfg_code": "APPDE",
            "brand_code": "ELEM"
        },
        "First Alert": {
            "mfg_name": "Resideo Technologies, Inc. / BRK Brands",
            "brand_name": "First Alert®",
            "mfg_code": "2754",
            "brand_code": "FSTA"
        },
        "BRK": {
            "mfg_name": "Resideo Technologies, Inc. / BRK Brands",
            "brand_name": "BRK®",
            "mfg_code": "2754",
            "brand_code": "BRKB"
        },
        "Wera": {
            "mfg_name": "Wera Tools NA Inc.",
            "brand_name": "Wera®",
            "mfg_code": "WERTO",
            "brand_code": "WERA"
        },
        "Kreg": {
            "mfg_name": "Kreg Tool Company",
            "brand_name": "Kreg®",
            "mfg_code": "KRETO",
            "brand_code": "KREG"
        },
        "Irwin": {
            "mfg_name": "Stanley Black & Decker, Inc.",
            "brand_name": "IRWIN®",
            "mfg_code": "5863",
            "brand_code": "IRWN"
        },
        "Senco": {
            "mfg_name": "Kyocera Senco Industrial Tools, Inc.",
            "brand_name": "Senco®",
            "mfg_code": "4650",
            "brand_code": "SENC"
        },
        "Dremel": {
            "mfg_name": "Robert Bosch Tool Corporation",
            "brand_name": "Dremel®",
            "mfg_code": "6564",
            "brand_code": "DREM"
        },
        "Bosch": {
            "mfg_name": "Robert Bosch Tool Corporation",
            "brand_name": "Bosch®",
            "mfg_code": "6564",
            "brand_code": "BOSC"
        },
        "Oliver Machinery": {
            "mfg_name": "Oliver Machinery Company",
            "brand_name": "Oliver®",
            "mfg_code": "OLIMA",
            "brand_code": "OLIV"
        },
        "Grizzly": {
            "mfg_name": "Woodstock International, Inc.",
            "brand_name": "Grizzly®",
            "mfg_code": "3658",
            "brand_code": "GRIZ"
        },
        "SawStop": {
            "mfg_name": "SawStop LLC",
            "brand_name": "SawStop®",
            "mfg_code": "SAWST",
            "brand_code": "SAWS"
        },
        "Bow Products": {
            "mfg_name": "Bow Products LLC",
            "brand_name": "Bow Products®",
            "mfg_code": "BOWPR",
            "brand_code": "BOWP"
        },
        "Leviton": {
            "mfg_name": "Leviton Manufacturing Co., Inc.",
            "brand_name": "Leviton®",
            "mfg_code": "4927",
            "brand_code": "LEVT"
        },
        "Square D": {
            "mfg_name": "Schneider Electric USA, Inc.",
            "brand_name": "Square D™",
            "mfg_code": "6825",
            "brand_code": "SQRD"
        },
        "Southwire": {
            "mfg_name": "Southwire Company, LLC",
            "brand_name": "Southwire®",
            "mfg_code": "6603",
            "brand_code": "SOUT"
        },
        "Hager": {
            "mfg_name": "Hager Companies",
            "brand_name": "Hager®",
            "mfg_code": "4189",
            "brand_code": "HAGR"
        },
        "Hunter Fan": {
            "mfg_name": "Hunter Fan Company",
            "brand_name": "Hunter®",
            "mfg_code": "4381",
            "brand_code": "HUNT"
        },
        "James Hardie": {
            "mfg_name": "James Hardie Building Products Inc.",
            "brand_name": "James Hardie®",
            "mfg_code": "BOICA",
            "brand_code": "HARD"
        },
        "LP SmartSide": {
            "mfg_name": "Louisiana-Pacific Corporation",
            "brand_name": "LP® SmartSide®",
            "mfg_code": "3073",
            "brand_code": "LPSC"
        },
        "CertainTeed": {
            "mfg_name": "CertainTeed Gypsum, Inc.",
            "brand_name": "CertainTeed®",
            "mfg_code": "2765",
            "brand_code": "CERT"
        },
        "Prebena": {
            "mfg_name": "Prebena Fastening Technology",
            "brand_name": "Prebena®",
            "mfg_code": "PREBE",
            "brand_code": "PREB"
        },
        "Malco": {
            "mfg_name": "Malco Products, SBC",
            "brand_name": "Malco®",
            "mfg_code": "2370",
            "brand_code": "MALC"
        },
        "Vessel": {
            "mfg_name": "Vessel Tools USA Inc.",
            "brand_name": "Vessel®",
            "mfg_code": "VESTO",
            "brand_code": "VESS"
        },
        "Woodpeckers": {
            "mfg_name": "Woodpeckers LLC",
            "brand_name": "Woodpeckers®",
            "mfg_code": "WOODP",
            "brand_code": "WOOD"
        },
        "Marshalltown": {
            "mfg_name": "Marshalltown Company",
            "brand_name": "Marshalltown®",
            "mfg_code": "5155",
            "brand_code": "MRSH"
        },
        "Edge Safety": {
            "mfg_name": "Edge Eyewear Inc.",
            "brand_name": "Edge Eyewear®",
            "mfg_code": "EDGSA",
            "brand_code": "EDGE"
        },
        "Lutron": {
            "mfg_name": "Lutron Electronics Co., Inc.",
            "brand_name": "Lutron®",
            "mfg_code": "FENBR",
            "brand_code": "LUTR"
        },
        "Prime Wire & Cable": {
            "mfg_name": "Prime Wire & Cable, Inc.",
            "brand_name": "Prime®",
            "mfg_code": "3562",
            "brand_code": "PRIM"
        },
        "Feit Electric": {
            "mfg_name": "Feit Electric Company",
            "brand_name": "Feit Electric®",
            "mfg_code": "3468",
            "brand_code": "FEIT"
        },
        "GT-Lite": {
            "mfg_name": "GT-Lite Direct",
            "brand_name": "GT-Lite®",
            "mfg_code": "5702",
            "brand_code": "GTLT"
        },
        "Schumacher": {
            "mfg_name": "Schumacher Electric Corporation",
            "brand_name": "Schumacher®",
            "mfg_code": "SCHUM",
            "brand_code": "SCHU"
        },
        "StealthMounts": {
            "mfg_name": "Metalmark Industrial Inc.",
            "brand_name": "StealthMounts®",
            "mfg_code": "METIN",
            "brand_code": "STLM"
        },
        "Carlon": {
            "mfg_name": "Thomas & Betts Corporation",
            "brand_name": "Carlon®",
            "mfg_code": "7405",
            "brand_code": "CARL"
        },
        "Streamlight": {
            "mfg_name": "Streamlight, Inc.",
            "brand_name": "Streamlight®",
            "mfg_code": "7277",
            "brand_code": "STRM"
        },
        "NEBO": {
            "mfg_name": "Alliance Consumer Group (ACG Brands)",
            "brand_name": "NEBO®",
            "mfg_code": "1154",
            "brand_code": "NEBO"
        },
        "Police Security": {
            "mfg_name": "Police Security Flashlights",
            "brand_name": "Police Security®",
            "mfg_code": "9470",
            "brand_code": "POLI"
        },
        "Rees Cast Stone": {
            "mfg_name": "Rees Cast Stone Company",
            "brand_name": "Rees Cast Stone™",
            "mfg_code": "REECA",
            "brand_code": "REES"
        },
        "MillerTech": {
            "mfg_name": "MillerTech Energy Solutions LLC",
            "brand_name": "MillerTech®",
            "mfg_code": "MILTE",
            "brand_code": "MLRT"
        },
        "UTW Pro": {
            "mfg_name": "Tech Gear 5.7 Inc.",
            "brand_name": "UTW Pro®",
            "mfg_code": "TECGE",
            "brand_code": "UTWP"
        },
        "Sabre": {
            "mfg_name": "Security Equipment Corporation",
            "brand_name": "SABRE®",
            "mfg_code": "9195",
            "brand_code": "SABR"
        },
        "National Nail": {
            "mfg_name": "National Nail Corp.",
            "brand_name": "CAMO®",
            "mfg_code": "7439",
            "brand_code": "NATN"
        },
        "CMT": {
            "mfg_name": "CMT USA Inc.",
            "brand_name": "CMT Orange Tools®",
            "mfg_code": "CMTUS",
            "brand_code": "CMTO"
        },
        "JET": {
            "mfg_name": "JPW Industries, Inc.",
            "brand_name": "JET®",
            "mfg_code": "JPWIN",
            "brand_code": "JETP"
        },
        "King Canada": {
            "mfg_name": "King Canada Inc.",
            "brand_name": "King Canada®",
            "mfg_code": "KINCA",
            "brand_code": "KING"
        }
    }
}

with open(os.path.join(DATA_DIR, 'master_brands.json'), 'w', encoding='utf-8') as f:
    json.dump(master_brands, f, indent=2, ensure_ascii=False)

# 4. Taxonomy & Category LOVs
category_lovs = {
    "dishwashers": {
        "dept": "Appliances",
        "class": "Large Appliances",
        "fine": "Dishwashers",
        "classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
        "unspsc": "52141505",
        "product_type": "Dishwasher",
        "attributes": [
            "Series", "Model", "Number of Wash Cycles", "Voltage Rating", "Amperage Rating",
            "Mounting Type", "Plug Type", "Size", "Depth With Door Open", "Minimum Height",
            "Maximum Height", "Sound Level", "Material", "Color", "Additional Information"
        ]
    },
    "refrigerators": {
        "dept": "Appliances",
        "class": "Large Appliances",
        "fine": "Refrigerators",
        "classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Refrigerators",
        "unspsc": "24131501",
        "product_type": "Refrigerator",
        "attributes": ["Series", "Capacity", "Total Capacity", "Color", "Installation Type", "Voltage Rating"]
    },
    "freezers": {
        "dept": "Appliances",
        "class": "Large Appliances",
        "fine": "Freezers",
        "classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Freezers",
        "unspsc": "24131502",
        "product_type": "Freezer",
        "attributes": ["Series", "Capacity", "Configuration", "Color", "Defrost Type", "Voltage Rating"]
    },
    "ranges": {
        "dept": "Appliances",
        "class": "Cooking Appliances",
        "fine": "Ranges",
        "classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Ranges",
        "unspsc": "52141514",
        "product_type": "Range",
        "attributes": ["Series", "Fuel Type", "Size", "Number of Burners", "Color", "Voltage Rating"]
    },
    "microwaves": {
        "dept": "Appliances",
        "class": "Cooking Appliances",
        "fine": "Microwave Ovens",
        "classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Microwave Ovens",
        "unspsc": "52141511",
        "product_type": "Microwave Oven",
        "attributes": ["Series", "Capacity", "Wattage", "Type", "Color", "Mounting Type"]
    },
    "washers": {
        "dept": "Appliances",
        "class": "Laundry",
        "fine": "Washing Machines",
        "classpath": "Appliances & Consumer Electronics>Laundry Appliances>Washing Machines",
        "unspsc": "52141601",
        "product_type": "Washing Machine",
        "attributes": ["Series", "Capacity", "Load Type", "Color", "Voltage Rating"]
    },
    "dryers": {
        "dept": "Appliances",
        "class": "Laundry",
        "fine": "Dryers",
        "classpath": "Appliances & Consumer Electronics>Laundry Appliances>Clothes Dryers",
        "unspsc": "52141602",
        "product_type": "Clothes Dryer",
        "attributes": ["Series", "Fuel Type", "Capacity", "Color", "Voltage Rating"]
    },
    "coffee_makers": {
        "dept": "Appliances",
        "class": "Small Appliances",
        "fine": "Coffee & Espresso",
        "classpath": "Appliances & Consumer Electronics>Small Appliances>Coffee & Espresso Makers",
        "unspsc": "52141526",
        "product_type": "Coffee Maker",
        "attributes": ["Series", "Type", "Capacity", "Color", "Material", "Voltage Rating"]
    },
    "toasters": {
        "dept": "Appliances",
        "class": "Small Appliances",
        "fine": "Toasters",
        "classpath": "Appliances & Consumer Electronics>Small Appliances>Toasters & Ovens",
        "unspsc": "52141527",
        "product_type": "Toaster",
        "attributes": ["Series", "Slice Capacity", "Color", "Material", "Wattage"]
    },
    "abrasives_cut_off": {
        "dept": "Abrasives",
        "class": "Cutting & Grinding Wheels",
        "fine": "Cut-Off Wheels",
        "classpath": "Abrasives>Cutting & Grinding Wheels>Cut-Off Wheels",
        "unspsc": "31191600",
        "product_type": "Cut-Off Wheel",
        "attributes": ["Diameter", "Thickness", "Arbor/Shank Size", "Abrasive Material", "Applicable Materials", "Max RPM"]
    },
    "abrasives_sanding": {
        "dept": "Abrasives",
        "class": "Sanding Discs & Belts",
        "fine": "Sanding Belts & Discs",
        "classpath": "Abrasives>Sanding & Finishing>Sanding Belts & Discs",
        "unspsc": "31191500",
        "product_type": "Sanding Disc",
        "attributes": ["Size", "Grit", "Backing Material", "Attachment Type", "Quantity"]
    },
    "saw_blades": {
        "dept": "Tools & Hardware",
        "class": "Power Tool Accessories",
        "fine": "Saw Blades",
        "classpath": "Tools & Hardware>Power Tool Accessories>Saw Blades>Circular Saw Blades",
        "unspsc": "27112802",
        "product_type": "Saw Blade",
        "attributes": ["Blade Diameter", "Number of Teeth", "Arbor Size", "Kerf", "Applicable Materials", "Hook Angle"]
    },
    "fastener_bits": {
        "dept": "Tools & Hardware",
        "class": "Power Tool Accessories",
        "fine": "Screwdriver Bits",
        "classpath": "Tools & Hardware>Power Tool Accessories>Driver Bits & Fastener Holders",
        "unspsc": "27112814",
        "product_type": "Driver Bit",
        "attributes": ["Drive Type", "Drive Size", "Length", "Shank Size", "Quantity", "Impact Rated"]
    },
    "power_tools_saws": {
        "dept": "Tools & Hardware",
        "class": "Power Tools",
        "fine": "Saws",
        "classpath": "Tools & Hardware>Power Tools>Saws>Circular Saws",
        "unspsc": "27112700",
        "product_type": "Circular Saw",
        "attributes": ["Series", "Voltage Rating", "Blade Diameter", "Motor Type", "Power Source", "Bevel Capacity"]
    },
    "power_tools_drills": {
        "dept": "Tools & Hardware",
        "class": "Power Tools",
        "fine": "Drills & Drivers",
        "classpath": "Tools & Hardware>Power Tools>Drills & Drivers>Impact Drivers",
        "unspsc": "27112703",
        "product_type": "Impact Driver",
        "attributes": ["Series", "Voltage Rating", "Chuck Size", "Torque", "Drive Size", "Power Source"]
    },
    "power_tools_sanders": {
        "dept": "Tools & Hardware",
        "class": "Power Tools",
        "fine": "Sanders & Polishers",
        "classpath": "Tools & Hardware>Power Tools>Sanders & Polishers>Random Orbital Sanders",
        "unspsc": "27112708",
        "product_type": "Orbital Sander",
        "attributes": ["Series", "Pad Size", "Orbit Diameter", "Voltage Rating", "Speed Rating", "Dust Collection"]
    },
    "power_tools_nailers": {
        "dept": "Tools & Hardware",
        "class": "Power Tools",
        "fine": "Nailers & Staplers",
        "classpath": "Tools & Hardware>Power Tools>Nailers & Staplers>Framing Nailers",
        "unspsc": "27112709",
        "product_type": "Nailer",
        "attributes": ["Series", "Fastener Gauge", "Magazine Angle", "Collation Type", "Power Source"]
    },
    "batteries_chargers": {
        "dept": "Tools & Hardware",
        "class": "Power Tool Accessories",
        "fine": "Batteries & Chargers",
        "classpath": "Tools & Hardware>Power Tool Accessories>Batteries & Chargers>Power Tool Batteries",
        "unspsc": "26111700",
        "product_type": "Battery Pack",
        "attributes": ["Series", "Voltage Rating", "Battery Capacity", "Battery Chemistry", "Package Quantity"]
    },
    "decking": {
        "dept": "Building Materials",
        "class": "Decking & Railing",
        "fine": "Composite Decking",
        "classpath": "Building Materials>Decking & Railing>Deck Boards",
        "unspsc": "30103600",
        "product_type": "Deck Board",
        "attributes": ["Series", "Profile", "Color", "Length", "Nominal Size", "Material"]
    },
    "deck_railing": {
        "dept": "Building Materials",
        "class": "Decking & Railing",
        "fine": "Railing Systems",
        "classpath": "Building Materials>Decking & Railing>Railing Kits",
        "unspsc": "30103601",
        "product_type": "Railing Kit",
        "attributes": ["Series", "Color", "Length", "Height", "Baluster Type", "Material"]
    },
    "lighting_bulbs": {
        "dept": "Electrical",
        "class": "Lamps & Bulbs",
        "fine": "LED Bulbs",
        "classpath": "Electrical>Lamps & Bulbs>LED Bulbs",
        "unspsc": "39101628",
        "product_type": "LED Light Bulb",
        "attributes": ["Bulb Shape", "Base Type", "Wattage Equivalent", "Color Temperature", "Lumens", "Voltage Rating", "Package Quantity"]
    },
    "lighting_fixtures": {
        "dept": "Electrical",
        "class": "Lighting Fixtures",
        "fine": "Indoor & Outdoor Fixtures",
        "classpath": "Electrical>Lighting Fixtures>Wall & Ceiling Fixtures",
        "unspsc": "39111500",
        "product_type": "Light Fixture",
        "attributes": ["Series", "Mounting Type", "Finish", "Number of Lights", "Dimensions", "Voltage Rating"]
    },
    "electrical_devices": {
        "dept": "Electrical",
        "class": "Wiring Devices",
        "fine": "Receptacles & Outlets",
        "classpath": "Electrical>Wiring Devices>Outlets & Receptacles",
        "unspsc": "39121406",
        "product_type": "Receptacle Outlet",
        "attributes": ["Amperage Rating", "Voltage Rating", "NEMA Configuration", "Color", "Grade", "Features"]
    },
    "safety_gear": {
        "dept": "Safety & Security",
        "class": "Personal Protective Equipment",
        "fine": "Eye Protection & Heated Gear",
        "classpath": "Safety & Security>Personal Protective Equipment>Safety Glasses",
        "unspsc": "46181802",
        "product_type": "Safety Glasses",
        "attributes": ["Series", "Frame Color", "Lens Color", "Lens Coating", "Size"]
    }
}

with open(os.path.join(DATA_DIR, 'category_lovs.json'), 'w', encoding='utf-8') as f:
    json.dump(category_lovs, f, indent=2, ensure_ascii=False)

print("Master reference datasets generated successfully.")
