"""
UniEnrich Taxonomy & Classpath Classification Engine
Predicts Dept, Class, Fine, Classpath hierarchy, and UNSPSC codes.
"""
import os
import json
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

with open(os.path.join(DATA_DIR, 'category_lovs.json'), 'r', encoding='utf-8') as f:
    CATEGORY_LOVS = json.load(f)

# Rules mapping keywords to category keys
TAXONOMY_RULES = [
    ("dishwashers", [r"dishwasher", r"dish\s*washer"]),
    ("washers", [r"washer\s*wh", r"washer\s*bk", r"laundry\s*center", r"elect\s*washer", r"speed\s*queen\s*washer"]),
    ("dryers", [r"heater\s*kit", r"dryer", r"elect\s*dryer", r"gas\s*dryer"]),
    ("refrigerators", [r"fridge", r"refrigerator", r"beverage\s*center"]),
    ("freezers", [r"freezer", r"freezer\s*chest", r"freezer\s*-\s*upright"]),
    ("ranges", [r"cooktop", r"range\s*ss", r"range\s*bk", r"electric\s*range", r"gas\s*range", r"elec\s*range"]),
    ("microwaves", [r"microwave", r"otr\s*microwave", r"microwave\s*drawer"]),
    ("coffee_makers", [r"coffee\s*maker", r"espresso\s*machine", r"drip\s*coffee"]),
    ("toasters", [r"toaster", r"toast\s*oven"]),
    ("abrasives_cut_off", [r"cut-off", r"cut\s*off\s*disc", r"cut\s*and\s*grind", r"grinding\s*wheel", r"masonry\s*cut\s*off", r"masonry\s*grinding"]),
    ("abrasives_sanding", [r"sanding\s*belt", r"sanding\s*sponge", r"stikit\s*film", r"abranet", r"hiolit", r"iridium", r"abrasive\s*set"]),
    ("saw_blades", [r"saw\s*blade", r"blade\s*7-1/4", r"dado\s*pro", r"planer\s*blade", r"planer\s*knives", r"sawzall\s*blade", r"diamond\s*tile\s*blade", r"jig\s*saw\s*blade", r"track\s*saw\s*blade"]),
    ("fastener_bits", [r"drive\s*bit", r"phillips\s*drive", r"square\s*drive\s*bit", r"torx\s*drive", r"trox\s*drive", r"screw\s*setter", r"torsion\s*bit", r"bit\s*holder", r"impact\s*driver\s*set", r"socket\s*adapter"]),
    ("power_tools_saws", [r"circular\s*saw", r"circ\s*saw", r"jig\s*saw", r"jigsaw", r"miter\s*saw", r"recip\s*saw", r"bandsaw", r"table\s*saw", r"track\s*saw\s*kit"]),
    ("power_tools_drills", [r"drill\s*driver", r"impact\s*driver", r"hammer\s*drill", r"die\s*grinder", r"angle\s*grinder", r"drill\s*press", r"impact\s*wrench", r"ratchet", r"rachet"]),
    ("power_tools_sanders", [r"orbit\s*sander", r"orbital\s*sander", r"cordless\s*sander", r"polisher", r"planing\s*machine", r"portable\s*planer", r"benchtop\s*planer", r"plunge\s*router", r"band\s*file"]),
    ("power_tools_nailers", [r"brad\s*nailer", r"finish\s*nailer", r"framing\s*nailer", r"roofing\s*nailer", r"narrow\s*crown\s*stapler", r"staple"]),
    ("batteries_chargers", [r"battery", r"starter\s*kit", r"charger", r"power\s*source", r"fast\s*charger", r"rapid\s*charger"]),
    ("decking", [r"decking", r"sq\s*edge", r"grooved", r"pvc\s*decking", r"fascia", r"pvc\s*fascia"]),
    ("deck_railing", [r"rail\s*kit", r"post\s*trim", r"post\s*sleeve", r"post\s*cap", r"blank\s*post", r"support\s*post", r"post\s*wrap", r"railing\s*panel", r"ada\s*rail", r"ada\s*wall\s*mount"]),
    ("lighting_bulbs", [r"led\s*bulb", r"flor\s*", r"halogen\s*", r"incan\s*", r"cct", r"par38", r"par30", r"br30", r"br40", r"a19", r"st19", r"edison", r"cand\s*", r"cob\s*bulb", r"ubulb"]),
    ("lighting_fixtures", [r"wall\s*lt", r"wall\s*light", r"bath\s*light", r"ceiling\s*lt", r"ceiling\s*light", r"pendant\s*lt", r"pendant\s*light", r"down\s*light", r"downlight", r"strip\s*light", r"shop\s*light", r"highbay\s*light", r"chandelier", r"sconce", r"wrap\s*lt", r"flat\s*panel"]),
    ("electrical_devices", [r"outlet", r"receptacle", r"dimmer", r"timer", r"cord\s*conn", r"switch", r"wallplate", r"box\s*cover", r"oct\s*box", r"square\s*box", r"load\s*cntr", r"load\s*center", r"cable", r"wire\s*16", r"triplex", r"so\s*cord", r"voltage\s*detector"]),
    ("safety_gear", [r"safety\s*glasses", r"heated\s*glove", r"heated\s*hoodie", r"kneeling\s*pad", r"hearing\s*protector", r"fire\s*extinguisher", r"smoke\s*&\s*co\s*alarm"])
]

def classify_product(part_desc: str, mfg_part_num: str = "", raw_dept: str = "", raw_class: str = "", raw_fine: str = "") -> dict:
    """
    Classifies raw item into standard Dept, Class, Fine, Classpath, UNSPSC, and Product Name.
    """
    text = f"{part_desc} {mfg_part_num}".lower()
    
    # Specific override for heater kits
    if "heater kit" in text or "d519127" in text:
        return {
            "cat_key": "dryers",
            "Dept": "Appliances",
            "Class": "Laundry Accessories",
            "Fine": "Dryer Heating Elements",
            "Classpath": "Appliances & Consumer Electronics>Laundry Appliances>Dryer Replacement Parts",
            "UNSPSC": "52141602",
            "Product Name": "Dryer Heater Kit",
            "attributes_schema": ["Voltage", "Wattage", "Application", "Includes"]
        }

    # 1. Match against explicit keywords
    matched_cat = None
    for cat_key, patterns in TAXONOMY_RULES:
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                matched_cat = cat_key
                break
        if matched_cat:
            break

    # Default fallback category if no match
    if not matched_cat:
        if "saw" in text or "drill" in text or "tool" in text:
            matched_cat = "power_tools_drills"
        elif "light" in text or "lamp" in text or "led" in text:
            matched_cat = "lighting_fixtures"
        else:
            matched_cat = "dishwashers"

    cat_info = CATEGORY_LOVS.get(matched_cat, CATEGORY_LOVS["dishwashers"])

    return {
        "cat_key": matched_cat,
        "Dept": raw_dept or cat_info.get("dept", "Appliances"),
        "Class": raw_class or cat_info.get("class", "Large Appliances"),
        "Fine": raw_fine or cat_info.get("fine", "Dishwashers"),
        "Classpath": cat_info.get("classpath", ""),
        "UNSPSC": cat_info.get("unspsc", ""),
        "Product Name": cat_info.get("product_type", "Product"),
        "attributes_schema": cat_info.get("attributes", [])
    }
