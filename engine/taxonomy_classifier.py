"""
UniEnrich Universal Industrial Taxonomy & Product Type Classifier
Employs Longest-Match Compound-Noun Specificity Scoring and Clean NLP Noun-Phrase Fallbacks.
"""
import os
import json
import re
from .ai_classifier import semantic_zero_shot_classify
from .ai_agent import predict_ml_taxonomy

# Dynamic Product Type Extractors (Pattern, Product Type, Priority Score)
PRODUCT_TYPE_EXTRACTORS = [
    # Mason Line & Layout Tools (High Priority to prevent "Line" colliding with Laser Level!)
    (r"mason\s*line|chalk\s*line|chalk\s*reel|mason\s*twine", "Mason Line & Chalk Reel", 100),
    (r"cross\s*line\s*laser|line\s*laser|laser\s*level|spot\s*laser", "Cross Line Laser", 95),
    (r"rafter\s*square|t-square|framing\s*square", "Rafter Square", 95),
    (r"tape\s*measure|measuring\s*tape", "Tape Measure", 95),
    (r"caliper|bigcal", "Caliper Measuring Tool", 95),

    # Decking & Railing (Dimension & Profile Patterns: 1x12, 1x6, 5/4x6)
    (r"\b1x(?:8|10|12)\b.*(?:fascia|lineage|azek|trex|deck)", "Fascia Board", 98),
    (r"\b(?:1x6|5/4x6|1x4)\b.*(?:lineage|azek|trex|transcend|enhance|decking|deck)", "Composite Deck Board", 98),
    (r"decking|deck\s*board|vintage\s*azek|transcend|lineage", "Composite Deck Board", 90),
    (r"fascia\s*board|fascia", "Fascia Board", 90),
    (r"post\s*wrap", "Post Wrap", 95),
    (r"post\s*sleeve", "Post Sleeve", 95),
    (r"post\s*trim|post\s*cap", "Post Trim & Cap", 95),
    (r"rail\s*kit|railing\s*panel", "Railing Kit", 95),
    (r"baluster", "Balusters", 90),
    (r"deck\s*joist\s*tape|joist\s*tape", "Deck Joist Flashing Tape", 95),

    # Wet/Dry Vacs & Shop Machinery
    (r"wet\s*dry\s*shop\s*vac|wet\s*dry\s*vac|shop\s*vac|dust\s*extractor", "Wet/Dry Shop Vacuum", 100),
    (r"air\s*compressor|compressor", "Air Compressor", 95),
    (r"pressure\s*washer", "Pressure Washer", 95),
    (r"generator|inverter\s*generator", "Portable Generator", 95),
    (r"welder|mig\s*welder|tig\s*welder", "Arc Welder", 95),

    # Safety & Alarms
    (r"smoke\s*&\s*co\s*alarm|smoke\s*and\s*carbon\s*monoxide|smoke\s*alarm|fire\s*alarm\s*detector", "Smoke & CO Alarm", 100),
    (r"fire\s*extinguisher", "Fire Extinguisher", 100),
    (r"hearing\s*protection|earmuffs|hearing\s*protector", "Hearing Protection Earmuffs", 95),
    (r"heated\s*glove", "Heated Work Gloves", 95),
    (r"heated\s*hoodie", "Heated Hoodie", 95),
    (r"kneeling\s*pad", "Kneeling Pad", 95),
    (r"safety\s*glasses", "Safety Glasses", 90),

    # Building Envelope & Drywall
    (r"gypsum\s*board|drywall|easi-lite|sheetrock", "Drywall Gypsum Board", 95),
    (r"rainscreen|rain\s*screen\s*flashing", "Rainscreen Flashing", 95),
    (r"masonry\s*mortar|mortar\s*mix", "Masonry Mortar Mix", 95),
    (r"smart\s*lap|hardieplank|hardiepanel|engineered\s*siding", "Siding Plank / Panel", 85),
    (r"soffit\s*panel|smart\s*vented", "Soffit Panel", 85),
    (r"skylight|skylt", "Roof Skylight", 85),
    (r"patio\s*dr|patio\s*door|access\s*door", "Patio / Access Door", 85),
    (r"threshold", "Door Threshold", 80),

    # Sanders & Woodworking Machinery
    (r"belt\s*(?:and|&)\s*spindle\s*sander", "Belt & Spindle Sander", 95),
    (r"oscillating(?:edge)?\s*sander", "Oscillating Spindle Sander", 95),
    (r"random\s*orbit\s*sander", "Random Orbital Sander", 95),
    (r"orbit(?:al)?\s*sander", "Orbital Sander", 90),
    (r"benchtop\s*planer", "Benchtop Planer", 95),
    (r"portable\s*planer", "Portable Planer", 95),
    (r"carpentry\s*planing\s*machine|planing\s*machine", "Planing Machine", 95),
    (r"plunge\s*router", "Plunge Router", 95),
    (r"router\s*bit", "Router Bit", 90),
    (r"band\s*file", "Band File", 90),
    (r"polisher", "Polisher", 85),
    
    # Saws & Blades
    (r"cement\s*track\s*saw\s*blade", "Cement Track Saw Blade", 95),
    (r"plywood\s*track\s*saw\s*blade|laminate\s*track\s*saw\s*blade|track\s*saw\s*blade", "Track Saw Blade", 95),
    (r"diamond\s*tile\s*blade", "Diamond Tile Blade", 95),
    (r"sawzall\s*blade|reciprocating\s*saw\s*blade", "Reciprocating Saw Blade", 95),
    (r"dado\s*pro\s*set|dado\s*set", "Dado Saw Blade Set", 95),
    (r"saw\s*blade|\bblade\b", "Saw Blade", 80),
    (r"track\s*saw", "Track Saw", 90),
    (r"circular\s*saw|circ\s*saw", "Circular Saw", 90),
    (r"miter\s*saw", "Miter Saw", 90),
    (r"table\s*saw", "Table Saw", 90),
    (r"bandsaw|band\s*saw", "Band Saw", 90),
    (r"jigsaw|jig\s*saw", "Jig Saw", 90),
    (r"recip(?:rocating)?\s*saw", "Reciprocating Saw", 90),

    # Drills & Accessories
    (r"hammer\s*drill", "Hammer Drill", 90),
    (r"impact\s*driver", "Impact Driver", 90),
    (r"impact\s*wrench", "Impact Wrench", 90),
    (r"drill\s*driver", "Drill Driver", 90),
    (r"right\s*angle\s*die\s*grinder", "Right Angle Die Grinder", 95),
    (r"die\s*grinder", "Die Grinder", 90),
    (r"angle\s*grinder", "Angle Grinder", 90),
    (r"drill\s*press", "Drill Press", 90),
    (r"cordless\s*ratchet|ratchet|rachet", "Cordless Ratchet", 85),
    (r"screwdriver|screw\s*setter", "Screwdriver", 85),

    # Fasteners & Power Tool Accessories
    (r"framing\s*nailer", "Framing Nailer", 95),
    (r"brad\s*nailer", "Brad Nailer", 95),
    (r"finish\s*nailer", "Finish Nailer", 95),
    (r"roofing\s*nailer", "Roofing Nailer", 95),
    (r"crown\s*stapler|stapler", "Stapler", 90),
    (r"socket\s*adapter", "Socket Adapter", 90),
    (r"driver\s*bit|torx\s*drive|phillips\s*drive|square\s*drive", "Driver Bit", 90),
    (r"bit\s*holder", "Bit Holder", 90),
    (r"battery\s*mount", "Battery Mount", 90),
    (r"battery\s*charger", "Battery Charger", 90),
    (r"starter\s*kit|battery\s*pack", "Battery Pack", 80),
    (r"collated\s*nail|finish\s*nail|framing\s*nail", "Collated Nails", 85),
    (r"\bstaple\b|\bstaples\b", "Staples", 75),

    # Abrasives
    (r"sanding\s*belt", "Sanding Belt", 95),
    (r"sanding\s*sponge", "Sanding Sponge", 95),
    (r"stikit\s*film|sanding\s*disc|abrasive\s*disc", "Sanding Disc", 90),
    (r"abranet|hiolit|iridium|abrasive\s*sheet|sanding\s*sheet", "Sanding Sheet", 90),
    (r"cut[- ]?off\s*disc|cut[- ]?off\s*wheel", "Cut-Off Disc", 90),
    (r"cut\s*and\s*grind|grinding\s*wheel", "Grinding Wheel", 90),

    # Bulbs & Electrical
    (r"\bbr40\b|\bbr30\b|\bbr20\b", "LED BR Reflector Bulb", 95),
    (r"\bpar38\b|\bpar30\b|\bpar20\b|\bpar16\b", "LED PAR Flood Bulb", 95),
    (r"\bmr16\b|\bmr11\b|\bgu10\b", "LED MR16 Spotlight Bulb", 95),
    (r"\ba19\b|\ba21\b|\bst19\b|\bedison\b|\bcandle\b|\bcand\b|\bg25\b", "LED General Purpose Bulb", 90),
    (r"\bt8\b|\bt5\b|\bt12\b|\blinear\s*tube\b", "LED Linear Tube", 90),
    (r"led\s*bulb|incan|halogen|lamp|\bbulb\b", "LED Light Bulb", 75),
    (r"wall\s*lt|wall\s*light|wall\s*sconce|sconce", "Wall Light Fixture", 85),
    (r"bath\s*light", "Bath Light Fixture", 85),
    (r"ceiling\s*lt|ceiling\s*light|flushmount", "Ceiling Light Fixture", 85),
    (r"pendant\s*lt|pendant\s*light", "Pendant Light Fixture", 85),
    (r"chandelier", "Chandelier Light Fixture", 85),
    (r"down\s*light|downlight", "Recessed Downlight", 85),
    (r"highbay|shop\s*light|strip\s*light|wrap\s*lt|flat\s*panel", "Commercial / Shop Light Fixture", 85),
    (r"flash\s*light|headlight|work\s*light|clip\s*light", "Work Flashlight", 80),
    (r"circuit\s*breaker|tandem\s*breaker", "Circuit Breaker", 95),
    (r"portable\s*so\s*cord|soow|sjoow|so\s*cord", "Portable SOOW Cord", 95),
    (r"romex|nm-b|thhn|uf-b|triplex\s*wire", "Electrical Wire / Cable", 90),
    (r"outlet|receptacle|wall\s*tap", "Receptacle Outlet", 85),
    (r"dimmer", "Dimmer Switch", 85),
    (r"programmable\s*timer|timer", "Programmable Timer", 85),
    (r"wallplate|box\s*cover", "Wallplate / Box Cover", 85),
    (r"oct\s*box|square\s*box|junction\s*box", "Electrical Junction Box", 85),
    (r"load\s*cntr|load\s*center", "Electrical Load Center / Panel", 85),
    (r"pipe\s*coupling|\bcplg\b", "Pipe Coupling", 90),
    (r"pipe\s*elbow|90\s*deg\s*ell", "Pipe Elbow", 90),

    # Appliances
    (r"dryer\s*heater\s*kit|heater\s*kit", "Dryer Heater Kit", 95),
    (r"dishwasher", "Dishwasher", 90),
    (r"clothes\s*dryer|\bdryer\b", "Clothes Dryer", 80),
    (r"laundry\s*center|washing\s*machine|\bwasher\b", "Washing Machine", 80),
    (r"beverage\s*center|refrigerator|\bfridge\b", "Refrigerator", 80),
    (r"freezer", "Freezer", 80),
    (r"cooktop", "Cooktop", 80),
    (r"range", "Range", 80),
    (r"microwave\s*oven|microwave", "Microwave Oven", 80),
    (r"coffee\s*maker|espresso", "Coffee & Espresso Maker", 80),
    (r"toaster|toast\s*oven", "Toaster", 80)
]

# Taxonomy Category Mappings
TAXONOMY_MAP = {
    # Layout & Measuring Tools
    "Mason Line & Chalk Reel": ("Tools & Hardware", "Hand & Measuring Tools", "Marking & Layout Tools", "Tools & Hardware>Measuring & Layout Tools>Chalk & Mason Lines", "27111800"),
    "Cross Line Laser": ("Tools & Hardware", "Hand & Measuring Tools", "Lasers & Levels", "Tools & Hardware>Measuring & Layout Tools>Laser Levels", "27111802"),
    "Rafter Square": ("Tools & Hardware", "Hand & Measuring Tools", "Squares", "Tools & Hardware>Measuring & Layout Tools>Squares", "27111800"),
    "Tape Measure": ("Tools & Hardware", "Hand & Measuring Tools", "Tape Measures", "Tools & Hardware>Measuring & Layout Tools>Tape Measures", "27111801"),
    "Caliper Measuring Tool": ("Tools & Hardware", "Hand & Measuring Tools", "Precision Measurement", "Tools & Hardware>Measuring & Layout Tools>Calipers", "27111800"),

    # Building Materials & Decking
    "Composite Deck Board": ("Building Materials", "Decking & Railing", "Deck Boards", "Building Materials>Decking & Railing>Deck Boards", "30103600"),
    "Fascia Board": ("Building Materials", "Decking & Railing", "Fascia", "Building Materials>Decking & Railing>Fascia Boards", "30103600"),
    "Railing Kit": ("Building Materials", "Decking & Railing", "Railing Kits", "Building Materials>Decking & Railing>Railing Kits", "30103601"),
    "Post Wrap": ("Building Materials", "Decking & Railing", "Post Wraps", "Building Materials>Decking & Railing>Post Wraps", "30103601"),
    "Post Sleeve": ("Building Materials", "Decking & Railing", "Post Sleeves", "Building Materials>Decking & Railing>Post Sleeves", "30103601"),
    "Post Trim & Cap": ("Building Materials", "Decking & Railing", "Post Accessories", "Building Materials>Decking & Railing>Post Caps & Trim", "30103601"),
    "Balusters": ("Building Materials", "Decking & Railing", "Balusters", "Building Materials>Decking & Railing>Balusters", "30103601"),
    "Deck Joist Flashing Tape": ("Building Materials", "Waterproofing", "Joist Tape", "Building Materials>Waterproofing>Flashing Tapes", "30151600"),
    "Drywall Gypsum Board": ("Building Materials", "Drywall & Plaster", "Drywall Panels", "Building Materials>Drywall & Gypsum>Panels", "30161500"),
    "Siding Plank / Panel": ("Building Materials", "Siding & Trim", "Planks", "Building Materials>Siding>Engineered Siding", "30151800"),
    "Soffit Panel": ("Building Materials", "Siding & Trim", "Soffit", "Building Materials>Siding>Soffit Panels", "30151800"),
    "Roof Skylight": ("Building Materials", "Doors & Windows", "Skylights", "Building Materials>Windows & Doors>Skylights", "30171600"),
    "Patio / Access Door": ("Building Materials", "Doors & Windows", "Doors", "Building Materials>Windows & Doors>Doors", "30171500"),
    "Door Threshold": ("Building Materials", "Doors & Windows", "Hardware", "Building Materials>Door Hardware>Thresholds", "30171500"),
    "Masonry Mortar Mix": ("Building Materials", "Masonry & Concrete", "Mortar", "Building Materials>Masonry>Mortar Mixes", "30111500"),
    "Rainscreen Flashing": ("Building Materials", "Building Envelope", "Rainscreen", "Building Materials>Moisture Management>Rainscreen", "30151600"),

    # Vacuums & Equipment
    "Wet/Dry Shop Vacuum": ("Tools & Hardware", "Cleaning & Janitorial Tools", "Shop Vacuums", "Tools & Hardware>Cleaning Equipment>Wet Dry Vacuums", "47121602"),
    "Air Compressor": ("Tools & Hardware", "Pneumatic Tools", "Air Compressors", "Tools & Hardware>Pneumatic Tools>Air Compressors", "40151601"),
    "Pressure Washer": ("Tools & Hardware", "Cleaning Equipment", "Pressure Washers", "Tools & Hardware>Cleaning Equipment>Pressure Washers", "47121800"),
    "Portable Generator": ("Electrical", "Power Generation", "Generators", "Electrical>Generators>Portable Generators", "26111601"),
    "Arc Welder": ("Tools & Hardware", "Welding & Soldering", "Welders", "Tools & Hardware>Welding Equipment>Arc Welders", "23271400"),

    # Safety
    "Smoke & CO Alarm": ("Safety & Security", "Alarms & Detectors", "Smoke Alarms", "Safety & Security>Alarms & Warnings>Smoke Detectors", "46191500"),
    "Fire Extinguisher": ("Safety & Security", "Fire Protection", "Extinguishers", "Safety & Security>Fire Protection>Fire Extinguishers", "46191601"),
    "Hearing Protection Earmuffs": ("Safety & Security", "Personal Protective Equipment", "Hearing Protection", "Safety & Security>Personal Protective Equipment>Hearing Protectors", "46181900"),
    "Heated Work Gloves": ("Safety & Security", "Personal Protective Equipment", "Hand Protection", "Safety & Security>Personal Protective Equipment>Work Gloves", "46181504"),
    "Heated Hoodie": ("Safety & Security", "Workwear & Apparel", "Heated Gear", "Safety & Security>Workwear>Heated Apparel", "46181500"),
    "Kneeling Pad": ("Safety & Security", "Ergonomics", "Kneeling Pads", "Safety & Security>Ergonomics>Kneeling Pads", "46181500"),
    "Safety Glasses": ("Safety & Security", "Personal Protective Equipment", "Eye Protection", "Safety & Security>Personal Protective Equipment>Safety Glasses", "46181802"),

    # Sanders & Saws
    "Belt & Spindle Sander": ("Tools & Hardware", "Power Tools", "Sanders & Polishers", "Tools & Hardware>Power Tools>Sanders & Polishers>Spindle Sanders", "27112708"),
    "Oscillating Spindle Sander": ("Tools & Hardware", "Power Tools", "Sanders & Polishers", "Tools & Hardware>Power Tools>Sanders & Polishers>Spindle Sanders", "27112708"),
    "Random Orbital Sander": ("Tools & Hardware", "Power Tools", "Sanders & Polishers", "Tools & Hardware>Power Tools>Sanders & Polishers>Random Orbital Sanders", "27112708"),
    "Orbital Sander": ("Tools & Hardware", "Power Tools", "Sanders & Polishers", "Tools & Hardware>Power Tools>Sanders & Polishers>Sheet Sanders", "27112708"),
    "Planing Machine": ("Tools & Hardware", "Power Tools", "Planers & Jointers", "Tools & Hardware>Power Tools>Woodworking Machinery>Planers", "27112700"),
    "Benchtop Planer": ("Tools & Hardware", "Power Tools", "Planers & Jointers", "Tools & Hardware>Power Tools>Woodworking Machinery>Planers", "27112700"),
    "Portable Planer": ("Tools & Hardware", "Power Tools", "Planers & Jointers", "Tools & Hardware>Power Tools>Woodworking Machinery>Planers", "27112700"),
    "Plunge Router": ("Tools & Hardware", "Power Tools", "Routers", "Tools & Hardware>Power Tools>Routers & Trimmers", "27112700"),
    "Router Bit": ("Tools & Hardware", "Power Tool Accessories", "Router Bits", "Tools & Hardware>Power Tool Accessories>Router Bits", "27112800"),
    "Band File": ("Tools & Hardware", "Power Tools", "Sanders & Polishers", "Tools & Hardware>Power Tools>Sanders & Polishers>Band Files", "27112708"),
    "Polisher": ("Tools & Hardware", "Power Tools", "Sanders & Polishers", "Tools & Hardware>Power Tools>Sanders & Polishers>Polishers", "27112708"),
    "Cement Track Saw Blade": ("Tools & Hardware", "Power Tool Accessories", "Saw Blades", "Tools & Hardware>Power Tool Accessories>Saw Blades>Specialty Blades", "27112802"),
    "Track Saw Blade": ("Tools & Hardware", "Power Tool Accessories", "Saw Blades", "Tools & Hardware>Power Tool Accessories>Saw Blades>Track Saw Blades", "27112802"),
    "Diamond Tile Blade": ("Tools & Hardware", "Power Tool Accessories", "Diamond Blades", "Tools & Hardware>Power Tool Accessories>Diamond Blades", "27112802"),
    "Reciprocating Saw Blade": ("Tools & Hardware", "Power Tool Accessories", "Saw Blades", "Tools & Hardware>Power Tool Accessories>Saw Blades>Reciprocating Blades", "27112802"),
    "Dado Saw Blade Set": ("Tools & Hardware", "Power Tool Accessories", "Saw Blades", "Tools & Hardware>Power Tool Accessories>Saw Blades>Dado Sets", "27112802"),
    "Saw Blade": ("Tools & Hardware", "Power Tool Accessories", "Saw Blades", "Tools & Hardware>Power Tool Accessories>Saw Blades>Circular Saw Blades", "27112802"),
    "Track Saw": ("Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Track Saws", "27112700"),
    "Circular Saw": ("Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Circular Saws", "27112700"),
    "Miter Saw": ("Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Miter Saws", "27112700"),
    "Table Saw": ("Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Table Saws", "27112700"),
    "Band Saw": ("Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Band Saws", "27112700"),
    "Jig Saw": ("Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Jig Saws", "27112700"),
    "Reciprocating Saw": ("Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Reciprocating Saws", "27112700"),

    # Drills & Fasteners
    "Hammer Drill": ("Tools & Hardware", "Power Tools", "Drills & Drivers", "Tools & Hardware>Power Tools>Drills & Drivers>Hammer Drills", "27112703"),
    "Impact Driver": ("Tools & Hardware", "Power Tools", "Drills & Drivers", "Tools & Hardware>Power Tools>Drills & Drivers>Impact Drivers", "27112703"),
    "Impact Wrench": ("Tools & Hardware", "Power Tools", "Drills & Drivers", "Tools & Hardware>Power Tools>Impact Wrenches", "27112703"),
    "Drill Driver": ("Tools & Hardware", "Power Tools", "Drills & Drivers", "Tools & Hardware>Power Tools>Drills & Drivers>Drill Drivers", "27112703"),
    "Angle Grinder": ("Tools & Hardware", "Power Tools", "Grinders", "Tools & Hardware>Power Tools>Grinders>Angle Grinders", "27112704"),
    "Die Grinder": ("Tools & Hardware", "Power Tools", "Grinders", "Tools & Hardware>Power Tools>Grinders>Die Grinders", "27112704"),
    "Right Angle Die Grinder": ("Tools & Hardware", "Power Tools", "Grinders", "Tools & Hardware>Power Tools>Grinders>Die Grinders", "27112704"),
    "Drill Press": ("Tools & Hardware", "Power Tools", "Stationary Machinery", "Tools & Hardware>Power Tools>Drill Presses", "27112700"),
    "Cordless Ratchet": ("Tools & Hardware", "Power Tools", "Fastening Tools", "Tools & Hardware>Power Tools>Ratchets", "27112700"),
    "Screwdriver": ("Tools & Hardware", "Power Tool Accessories", "Driver Bits", "Tools & Hardware>Power Tool Accessories>Driver Bits", "27112814"),
    "Framing Nailer": ("Tools & Hardware", "Power Tools", "Nailers & Staplers", "Tools & Hardware>Power Tools>Nailers & Staplers>Framing Nailers", "27112709"),
    "Brad Nailer": ("Tools & Hardware", "Power Tools", "Nailers & Staplers", "Tools & Hardware>Power Tools>Nailers & Staplers>Brad Nailers", "27112709"),
    "Finish Nailer": ("Tools & Hardware", "Power Tools", "Nailers & Staplers", "Tools & Hardware>Power Tools>Nailers & Staplers>Finish Nailers", "27112709"),
    "Roofing Nailer": ("Tools & Hardware", "Power Tools", "Nailers & Staplers", "Tools & Hardware>Power Tools>Nailers & Staplers>Roofing Nailers", "27112709"),
    "Stapler": ("Tools & Hardware", "Power Tools", "Nailers & Staplers", "Tools & Hardware>Power Tools>Nailers & Staplers>Staplers", "27112709"),
    "Socket Adapter": ("Tools & Hardware", "Power Tool Accessories", "Adapters", "Tools & Hardware>Power Tool Accessories>Socket Adapters", "27112800"),
    "Driver Bit": ("Tools & Hardware", "Power Tool Accessories", "Driver Bits", "Tools & Hardware>Power Tool Accessories>Driver Bits", "27112814"),
    "Bit Holder": ("Tools & Hardware", "Power Tool Accessories", "Holders", "Tools & Hardware>Power Tool Accessories>Bit Holders", "27112800"),
    "Battery Mount": ("Tools & Hardware", "Power Tool Accessories", "Storage", "Tools & Hardware>Tool Storage>Battery Mounts", "24102000"),
    "Battery Charger": ("Tools & Hardware", "Power Tool Accessories", "Chargers", "Tools & Hardware>Power Tool Accessories>Chargers", "26111700"),
    "Battery Pack": ("Tools & Hardware", "Power Tool Accessories", "Batteries", "Tools & Hardware>Power Tool Accessories>Batteries", "26111700"),
    "Collated Nails": ("Fasteners & Hardware", "Collated Fasteners", "Nails", "Fasteners>Nails>Collated Nails", "31162000"),
    "Staples": ("Fasteners & Hardware", "Collated Fasteners", "Staples", "Fasteners>Staples>Heavy Duty Staples", "31162000"),

    # Abrasives
    "Sanding Belt": ("Abrasives", "Sanding & Finishing", "Sanding Belts", "Abrasives>Sanding & Finishing>Sanding Belts", "31191500"),
    "Sanding Disc": ("Abrasives", "Sanding & Finishing", "Sanding Discs", "Abrasives>Sanding & Finishing>Sanding Discs", "31191500"),
    "Sanding Sheet": ("Abrasives", "Sanding & Finishing", "Sanding Sheets", "Abrasives>Sanding & Finishing>Sanding Sheets", "31191500"),
    "Sanding Sponge": ("Abrasives", "Sanding & Finishing", "Sanding Sponges", "Abrasives>Sanding & Finishing>Sanding Sponges", "31191500"),
    "Cut-Off Disc": ("Abrasives", "Cutting & Grinding Wheels", "Cut-Off Wheels", "Abrasives>Cutting & Grinding Wheels>Cut-Off Wheels", "31191600"),
    "Grinding Wheel": ("Abrasives", "Cutting & Grinding Wheels", "Grinding Wheels", "Abrasives>Cutting & Grinding Wheels>Grinding Wheels", "31191600"),

    # Bulbs & Electrical
    "LED BR Reflector Bulb": ("Electrical", "Lamps & Bulbs", "LED Bulbs", "Electrical>Lamps & Bulbs>LED Bulbs>Directional & Reflector Bulbs", "39101628"),
    "LED PAR Flood Bulb": ("Electrical", "Lamps & Bulbs", "LED Bulbs", "Electrical>Lamps & Bulbs>LED Bulbs>PAR Flood Bulbs", "39101628"),
    "LED MR16 Spotlight Bulb": ("Electrical", "Lamps & Bulbs", "LED Bulbs", "Electrical>Lamps & Bulbs>LED Bulbs>MR16 Spotlights", "39101628"),
    "LED General Purpose Bulb": ("Electrical", "Lamps & Bulbs", "LED Bulbs", "Electrical>Lamps & Bulbs>LED Bulbs>Standard Bulbs", "39101628"),
    "LED Linear Tube": ("Electrical", "Lamps & Bulbs", "Linear Tubes", "Electrical>Lamps & Bulbs>Linear Tubes", "39101605"),
    "LED Light Bulb": ("Electrical", "Lamps & Bulbs", "LED Bulbs", "Electrical>Lamps & Bulbs>LED Bulbs", "39101628"),
    "Wall Light Fixture": ("Electrical", "Lighting Fixtures", "Wall Sconces", "Electrical>Lighting Fixtures>Wall Lights", "39111500"),
    "Bath Light Fixture": ("Electrical", "Lighting Fixtures", "Bath Vanity", "Electrical>Lighting Fixtures>Bath Vanity Lights", "39111500"),
    "Ceiling Light Fixture": ("Electrical", "Lighting Fixtures", "Flush Mounts", "Electrical>Lighting Fixtures>Ceiling Lights", "39111500"),
    "Pendant Light Fixture": ("Electrical", "Lighting Fixtures", "Pendants", "Electrical>Lighting Fixtures>Pendant Lights", "39111500"),
    "Chandelier Light Fixture": ("Electrical", "Lighting Fixtures", "Chandeliers", "Electrical>Lighting Fixtures>Chandeliers", "39111500"),
    "Recessed Downlight": ("Electrical", "Lighting Fixtures", "Downlights", "Electrical>Lighting Fixtures>Recessed Downlights", "39111500"),
    "Commercial / Shop Light Fixture": ("Electrical", "Lighting Fixtures", "Commercial", "Electrical>Lighting Fixtures>Commercial Lighting", "39111500"),
    "Work Flashlight": ("Electrical", "Portable Lighting", "Flashlights", "Electrical>Portable Lighting>Work Lights", "39111610"),
    "Circuit Breaker": ("Electrical", "Power Distribution", "Circuit Breakers", "Electrical>Power Distribution>Circuit Breakers", "39121601"),
    "Portable SOOW Cord": ("Electrical", "Wire & Cable", "Portable Cord", "Electrical>Wire & Cable>Portable Cords", "26121629"),
    "Electrical Wire / Cable": ("Electrical", "Wire & Cable", "Building Wire", "Electrical>Wire & Cable>Electrical Cable", "26121600"),
    "Receptacle Outlet": ("Electrical", "Wiring Devices", "Outlets & Receptacles", "Electrical>Wiring Devices>Receptacles", "39121406"),
    "Dimmer Switch": ("Electrical", "Wiring Devices", "Dimmers", "Electrical>Wiring Devices>Dimmers", "39122200"),
    "Programmable Timer": ("Electrical", "Wiring Devices", "Timers", "Electrical>Wiring Devices>Timers", "39122200"),
    "Wallplate / Box Cover": ("Electrical", "Wiring Devices", "Wallplates", "Electrical>Wiring Devices>Wallplates", "39121300"),
    "Electrical Junction Box": ("Electrical", "Enclosures & Boxes", "Junction Boxes", "Electrical>Enclosures & Boxes>Outlet Boxes", "39121300"),
    "Electrical Load Center / Panel": ("Electrical", "Power Distribution", "Load Centers", "Electrical>Power Distribution>Load Centers", "39121101"),

    # Plumbing
    "Pipe Coupling": ("Plumbing & Pumps", "Pipe, Tube & Hose Fittings", "Fittings", "Plumbing & Pumps>Pipe, Tube & Hose Fittings>Couplings", "40142315"),
    "Pipe Elbow": ("Plumbing & Pumps", "Pipe, Tube & Hose Fittings", "Fittings", "Plumbing & Pumps>Pipe, Tube & Hose Fittings>Elbows", "40142315"),

    # Appliances
    "Dryer Heater Kit": ("Appliances", "Laundry Accessories", "Dryer Heating Elements", "Appliances & Consumer Electronics>Laundry Appliances>Dryer Replacement Parts", "52141602"),
    "Dishwasher": ("Appliances", "Large Appliances", "Dishwashers", "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "52141505"),
    "Clothes Dryer": ("Appliances", "Laundry", "Clothes Dryers", "Appliances & Consumer Electronics>Laundry Appliances>Clothes Dryers", "52141602"),
    "Washing Machine": ("Appliances", "Laundry", "Washing Machines", "Appliances & Consumer Electronics>Laundry Appliances>Washing Machines", "52141601"),
    "Refrigerator": ("Appliances", "Large Appliances", "Refrigerators", "Appliances & Consumer Electronics>Kitchen Appliances>Refrigerators", "24131501"),
    "Freezer": ("Appliances", "Large Appliances", "Freezers", "Appliances & Consumer Electronics>Kitchen Appliances>Freezers", "24131502"),
    "Range": ("Appliances", "Cooking Appliances", "Ranges", "Appliances & Consumer Electronics>Kitchen Appliances>Ranges", "52141514"),
    "Cooktop": ("Appliances", "Cooking Appliances", "Cooktops", "Appliances & Consumer Electronics>Kitchen Appliances>Cooktops", "52141514"),
    "Microwave Oven": ("Appliances", "Cooking Appliances", "Microwave Ovens", "Appliances & Consumer Electronics>Kitchen Appliances>Microwave Ovens", "52141511"),
    "Coffee & Espresso Maker": ("Appliances", "Small Appliances", "Coffee Makers", "Appliances & Consumer Electronics>Small Appliances>Coffee Makers", "52141526"),
    "Toaster": ("Appliances", "Small Appliances", "Toasters", "Appliances & Consumer Electronics>Small Appliances>Toasters", "52141527")
}

NOISE_WORDS = {
    "model", "type", "item", "series", "version", "part", "brand", "pack", "display", 
    "only", "box", "case", "assorted", "unit", "spec", "industrial", "standard", "heavy", "duty"
}

def clean_fallback_noun_phrase(part_desc: str, mfg_part_num: str) -> str:
    desc = part_desc or ""
    if mfg_part_num:
        desc = re.sub(rf"\b{re.escape(mfg_part_num)}\b", "", desc, flags=re.IGNORECASE)
        
    clean = re.sub(r'\b\d+(?:[-/.]\d+)?\s*(?:in|ft|v|w|a|rpm|dba|gal|gallon|hp|amp|volt|watt|pc|pk)\b', '', desc, flags=re.IGNORECASE)
    clean = re.sub(r'[\"\'#\-/\(\)]', ' ', clean)
    clean = re.sub(r'\b[a-z0-9]*\d+[a-z0-9]*\b', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    raw_tokens = clean.split()
    tokens = [t for t in raw_tokens if t.lower() not in NOISE_WORDS and len(t) > 1]
    
    if len(tokens) >= 2:
        return f"{tokens[-2]} {tokens[-1]}".title()
    elif len(tokens) == 1:
        return f"{tokens[0]} Equipment".title()
        
    return "Industrial Product"

def classify_product(part_desc: str, mfg_part_num: str = "", raw_dept: str = "", raw_class: str = "", raw_fine: str = "") -> dict:
    text = f"{part_desc} {mfg_part_num}".strip()
    
    # 1. Multi-Candidate Match with Specificity Ranking
    best_type = None
    best_priority = -1
    best_match_len = 0

    for pattern, p_type, priority in PRODUCT_TYPE_EXTRACTORS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            matched_len = len(m.group(0))
            total_rank = priority * 100 + matched_len
            if total_rank > (best_priority * 100 + best_match_len):
                best_priority = priority
                best_match_len = matched_len
                best_type = p_type

    if best_type and best_type in TAXONOMY_MAP:
        dept, cls, fine, classpath, unspsc = TAXONOMY_MAP[best_type]
        return {
            "cat_key": best_type.lower().replace(' ', '_'),
            "Dept": raw_dept or dept,
            "Class": raw_class or cls,
            "Fine": raw_fine or fine,
            "Classpath": classpath,
            "UNSPSC": unspsc,
            "Product Name": best_type,
            "is_fallback": False,
            "provenance": "REGEX_LONG_MATCH_PRIORITY"
        }

    # 2. Local Scikit-Learn TF-IDF N-Gram Vector Classifier
    ml_res = predict_ml_taxonomy(part_desc, mfg_part_num)
    if ml_res:
        return ml_res

    # 3. Clean fallback
    clean_pname = clean_fallback_noun_phrase(part_desc, mfg_part_num)

    return {
        "cat_key": "uncategorized",
        "Dept": raw_dept or "Uncategorized Supplies",
        "Class": raw_class or "General Industrial",
        "Fine": raw_fine or "Pending Review",
        "Classpath": "Uncategorized Supplies>General Industrial>Pending Review",
        "UNSPSC": "",
        "Product Name": clean_pname,
        "is_fallback": True,
        "provenance": "FALLBACK_UNCATEGORIZED"
    }
