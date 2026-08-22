"""
UniEnrich Universal Industrial Taxonomy & Product Type Classifier
Combines high-speed deterministic regex with AI zero-shot semantic matching across 50+ categories.
Never fabricates fallbacks; marks truly ambiguous records as NEEDS_HUMAN_REVIEW.
"""
import os
import json
import re
from .ai_classifier import semantic_zero_shot_classify

# Dynamic Product Type Token Extractors
PRODUCT_TYPE_EXTRACTORS = [
    # Lighting & Bulbs (including BR40, PAR38, MR16, A19)
    (r"\bbr40\b|\bbr30\b|\bbr20\b", "LED BR Reflector Bulb"),
    (r"\bpar38\b|\bpar30\b|\bpar20\b|\bpar16\b", "LED PAR Flood Bulb"),
    (r"\bmr16\b|\bmr11\b|\bgu10\b", "LED MR16 Spotlight Bulb"),
    (r"\ba19\b|\ba21\b|\bst19\b|\bedison\b|\bcandle\b|\bcand\b|\bg25\b", "LED General Purpose Bulb"),
    (r"\bt8\b|\bt5\b|\bt12\b|\blinear\s*tube\b", "LED Linear Tube"),
    (r"led\s*bulb|incan|halogen|lamp|\bbulb\b", "LED Light Bulb"),
    (r"wall\s*lt|wall\s*light|wall\s*sconce|sconce|vanity", "Wall Light Fixture"),
    (r"bath\s*light", "Bath Light Fixture"),
    (r"ceiling\s*lt|ceiling\s*light|flushmount", "Ceiling Light Fixture"),
    (r"pendant\s*lt|pendant\s*light", "Pendant Light Fixture"),
    (r"chandelier", "Chandelier Light Fixture"),
    (r"down\s*light|downlight", "Recessed Downlight"),
    (r"highbay|shop\s*light|strip\s*light|wrap\s*lt|flat\s*panel", "Commercial / Shop Light Fixture"),
    (r"flash\s*light|headlight|work\s*light|clip\s*light", "Work Flashlight"),

    # Pipe Fittings & Plumbing
    (r"\bcplg\b|coupling", "Pipe Coupling"),
    (r"elbow|90\s*deg\s*ell", "Pipe Elbow"),
    (r"bushing|reducer\s*bushing", "Reducer Bushing"),
    (r"pipe\s*nipple|\bnipple\b", "Pipe Nipple"),
    (r"union|flange|pipe\s*tee", "Pipe Fitting"),

    # Wire & Cable
    (r"so\s*cord|soow|sjoow|portable\s*cord", "Portable SOOW Cord"),
    (r"romex|nm-b|thhn|uf-b|triplex", "Electrical Wire / Cable"),

    # Sanders & Planers
    (r"belt\s*(?:and|&)\s*spindle\s*sander", "Belt & Spindle Sander"),
    (r"oscillating(?:edge)?\s*sander", "Oscillating Spindle Sander"),
    (r"random\s*orbit\s*sander", "Random Orbital Sander"),
    (r"orbit(?:al)?\s*sander", "Orbital Sander"),
    (r"benchtop\s*planer", "Benchtop Planer"),
    (r"portable\s*planer", "Portable Planer"),
    (r"carpentry\s*planing\s*machine", "Planing Machine"),
    (r"plunge\s*router", "Plunge Router"),
    (r"router\s*bit", "Router Bit"),
    (r"band\s*file", "Band File"),
    (r"polisher", "Polisher"),
    
    # Saws & Blades
    (r"cement\s*track\s*saw\s*blade", "Cement Track Saw Blade"),
    (r"plywood\s*track\s*saw\s*blade", "Track Saw Blade"),
    (r"laminate\s*track\s*saw\s*blade", "Track Saw Blade"),
    (r"track\s*saw", "Track Saw"),
    (r"circular\s*saw|circ\s*saw", "Circular Saw"),
    (r"miter\s*saw", "Miter Saw"),
    (r"table\s*saw", "Table Saw"),
    (r"bandsaw|band\s*saw", "Band Saw"),
    (r"jigsaw|jig\s*saw", "Jig Saw"),
    (r"recip(?:rocating)?\s*saw", "Reciprocating Saw"),
    (r"sawzall\s*blade", "Reciprocating Saw Blade"),
    (r"diamond\s*tile\s*blade", "Diamond Tile Blade"),
    (r"dado\s*pro\s*set|dado\s*set", "Dado Saw Blade Set"),
    (r"saw\s*blade|\bblade\b", "Saw Blade"),
    
    # Drills, Drivers & Grinders
    (r"hammer\s*drill", "Hammer Drill"),
    (r"impact\s*driver", "Impact Driver"),
    (r"impact\s*wrench", "Impact Wrench"),
    (r"drill\s*driver", "Drill Driver"),
    (r"right\s*angle\s*die\s*grinder", "Right Angle Die Grinder"),
    (r"die\s*grinder", "Die Grinder"),
    (r"angle\s*grinder", "Angle Grinder"),
    (r"drill\s*press", "Drill Press"),
    (r"ratchet|rachet", "Cordless Ratchet"),
    (r"screwdriver|screw\s*setter", "Screwdriver"),

    # Lasers & Measuring Tools
    (r"cross\s*line\s*laser|line\s*laser", "Cross Line Laser"),
    (r"laser\s*level|spot\s*laser|laser", "Laser Level"),
    (r"rafter\s*square|t-square", "Rafter Square"),
    (r"mason\s*line", "Mason Line"),
    (r"chalk\s*&\s*reel", "Chalk Reel Set"),
    (r"caliper|bigcal", "Caliper Measuring Tool"),
    (r"tire\s*pressure|inflator\s*gauge", "Digital Tire Inflator Gauge"),
    (r"voltage\s*detector", "Voltage Detector"),

    # Fasteners & Power Tool Accessories
    (r"framing\s*nailer", "Framing Nailer"),
    (r"brad\s*nailer", "Brad Nailer"),
    (r"finish\s*nailer", "Finish Nailer"),
    (r"roofing\s*nailer", "Roofing Nailer"),
    (r"crown\s*stapler|stapler", "Stapler"),
    (r"staple", "Staples"),
    (r"finish\s*nail|framing\s*nail|\bnail\b", "Collated Nails"),
    (r"socket\s*adapter", "Socket Adapter"),
    (r"driver\s*bit|torx\s*drive|phillips\s*drive|square\s*drive", "Driver Bit"),
    (r"bit\s*holder", "Bit Holder"),
    (r"battery\s*mount", "Battery Mount"),
    (r"starter\s*kit|battery\s*pack|\bbattery\b", "Battery Pack"),
    (r"charger|power\s*source", "Battery Charger"),

    # Abrasives
    (r"sanding\s*belt", "Sanding Belt"),
    (r"sanding\s*sponge", "Sanding Sponge"),
    (r"stikit\s*film|sanding\s*disc|abrasive\s*disc", "Sanding Disc"),
    (r"abranet|hiolit|iridium|abrasive\s*sheet", "Sanding Sheet"),
    (r"cut[- ]?off\s*disc|cut[- ]?off\s*wheel", "Cut-Off Disc"),
    (r"cut\s*and\s*grind|grinding\s*wheel", "Grinding Wheel"),

    # Decking & Railing
    (r"decking|deck\s*board", "Composite Deck Board"),
    (r"fascia", "Fascia Board"),
    (r"post\s*wrap", "Post Wrap"),
    (r"post\s*sleeve", "Post Sleeve"),
    (r"post\s*trim|post\s*cap", "Post Trim & Cap"),
    (r"rail\s*kit|railing\s*panel", "Railing Kit"),
    (r"baluster", "Balusters"),
    (r"deck\s*joist\s*tape|joist\s*tape", "Deck Joist Flashing Tape"),

    # Electrical Wiring & Power Distribution
    (r"outlet|receptacle|wall\s*tap", "Receptacle Outlet"),
    (r"dimmer", "Dimmer Switch"),
    (r"timer", "Programmable Timer"),
    (r"switch", "Wall Switch"),
    (r"wallplate|box\s*cover", "Wallplate / Box Cover"),
    (r"oct\s*box|square\s*box", "Electrical Junction Box"),
    (r"load\s*cntr|load\s*center", "Electrical Load Center / Panel"),
    (r"circuit\s*breaker|breaker", "Circuit Breaker"),

    # Appliances & Replacement Parts
    (r"dishwasher", "Dishwasher"),
    (r"heater\s*kit", "Dryer Heater Kit"),
    (r"dryer", "Clothes Dryer"),
    (r"laundry\s*center|washer", "Washing Machine"),
    (r"beverage\s*center|fridge|refrigerator", "Refrigerator"),
    (r"freezer", "Freezer"),
    (r"cooktop", "Cooktop"),
    (r"range", "Range"),
    (r"microwave", "Microwave Oven"),
    (r"coffee\s*maker|espresso", "Coffee & Espresso Maker"),
    (r"toaster|toast\s*oven", "Toaster"),

    # Building Envelope & Materials
    (r"drywall", "Drywall Gypsum Board"),
    (r"siding|smart\s*lap|hardieplank|hardiepanel", "Siding Plank / Panel"),
    (r"soffit|smart\s*vented", "Soffit Panel"),
    (r"skylight|skylt", "Roof Skylight"),
    (r"patio\s*dr|patio\s*door|access\s*door", "Patio / Access Door"),
    (r"window|slider|hopper", "Window Assembly"),
    (r"rainscreen", "Rainscreen Flashing"),
    (r"mortar", "Masonry Mortar Mix"),
    (r"threshold", "Door Threshold"),

    # Safety & PPE
    (r"safety\s*glasses", "Safety Glasses"),
    (r"heated\s*glove", "Heated Work Gloves"),
    (r"heated\s*hoodie", "Heated Hoodie"),
    (r"kneeling\s*pad", "Kneeling Pad"),
    (r"hearing\s*protector", "Hearing Protection Earmuffs"),
    (r"fire\s*extinguisher", "Fire Extinguisher"),
    (r"smoke\s*&\s*co\s*alarm", "Smoke & CO Alarm")
]

# Taxonomy Category Mappings
TAXONOMY_MAP = {
    # Bulbs & Lighting
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
    
    # Pipe Fittings
    "Pipe Coupling": ("Plumbing & Pumps", "Pipe, Tube & Hose Fittings", "Fittings", "Plumbing & Pumps>Pipe, Tube & Hose Fittings>Couplings", "40142315"),
    "Pipe Elbow": ("Plumbing & Pumps", "Pipe, Tube & Hose Fittings", "Fittings", "Plumbing & Pumps>Pipe, Tube & Hose Fittings>Elbows", "40142315"),
    "Reducer Bushing": ("Plumbing & Pumps", "Pipe, Tube & Hose Fittings", "Fittings", "Plumbing & Pumps>Pipe, Tube & Hose Fittings>Bushings", "40142315"),
    "Pipe Nipple": ("Plumbing & Pumps", "Pipe, Tube & Hose Fittings", "Fittings", "Plumbing & Pumps>Pipe, Tube & Hose Fittings>Nipples", "40142315"),
    "Pipe Fitting": ("Plumbing & Pumps", "Pipe, Tube & Hose Fittings", "Fittings", "Plumbing & Pumps>Pipe, Tube & Hose Fittings>Metallic Fittings", "40142315"),

    # Wire & Cable
    "Portable SOOW Cord": ("Electrical", "Wire & Cable", "Portable Cord", "Electrical>Wire & Cable>Portable Cords", "26121629"),
    "Electrical Wire / Cable": ("Electrical", "Wire & Cable", "Building Wire", "Electrical>Wire & Cable>Electrical Cable", "26121600"),
    "Circuit Breaker": ("Electrical", "Power Distribution", "Circuit Breakers", "Electrical>Power Distribution>Circuit Breakers", "39121601"),

    # Power Tools
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
    "Circular Saw": ("Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Circular Saws", "27112700"),
    "Miter Saw": ("Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Miter Saws", "27112700"),
    "Table Saw": ("Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Table Saws", "27112700"),
    "Band Saw": ("Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Band Saws", "27112700"),
    "Jig Saw": ("Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Jig Saws", "27112700"),
    "Reciprocating Saw": ("Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Reciprocating Saws", "27112700"),
    "Track Saw": ("Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Track Saws", "27112700"),
    "Hammer Drill": ("Tools & Hardware", "Power Tools", "Drills & Drivers", "Tools & Hardware>Power Tools>Drills & Drivers>Hammer Drills", "27112703"),
    "Impact Driver": ("Tools & Hardware", "Power Tools", "Drills & Drivers", "Tools & Hardware>Power Tools>Drills & Drivers>Impact Drivers", "27112703"),
    "Impact Wrench": ("Tools & Hardware", "Power Tools", "Drills & Drivers", "Tools & Hardware>Power Tools>Impact Wrenches", "27112703"),
    "Drill Driver": ("Tools & Hardware", "Power Tools", "Drills & Drivers", "Tools & Hardware>Power Tools>Drills & Drivers>Drill Drivers", "27112703"),
    "Angle Grinder": ("Tools & Hardware", "Power Tools", "Grinders", "Tools & Hardware>Power Tools>Grinders>Angle Grinders", "27112704"),
    "Die Grinder": ("Tools & Hardware", "Power Tools", "Grinders", "Tools & Hardware>Power Tools>Grinders>Die Grinders", "27112704"),
    "Right Angle Die Grinder": ("Tools & Hardware", "Power Tools", "Grinders", "Tools & Hardware>Power Tools>Grinders>Die Grinders", "27112704"),
    "Drill Press": ("Tools & Hardware", "Power Tools", "Stationary Machinery", "Tools & Hardware>Power Tools>Drill Presses", "27112700"),
    "Cordless Ratchet": ("Tools & Hardware", "Power Tools", "Fastening Tools", "Tools & Hardware>Power Tools>Ratchets", "27112700"),
    "Framing Nailer": ("Tools & Hardware", "Power Tools", "Nailers & Staplers", "Tools & Hardware>Power Tools>Nailers & Staplers>Framing Nailers", "27112709"),
    "Brad Nailer": ("Tools & Hardware", "Power Tools", "Nailers & Staplers", "Tools & Hardware>Power Tools>Nailers & Staplers>Brad Nailers", "27112709"),
    "Finish Nailer": ("Tools & Hardware", "Power Tools", "Nailers & Staplers", "Tools & Hardware>Power Tools>Nailers & Staplers>Finish Nailers", "27112709"),
    "Roofing Nailer": ("Tools & Hardware", "Power Tools", "Nailers & Staplers", "Tools & Hardware>Power Tools>Nailers & Staplers>Roofing Nailers", "27112709"),
    "Stapler": ("Tools & Hardware", "Power Tools", "Nailers & Staplers", "Tools & Hardware>Power Tools>Nailers & Staplers>Staplers", "27112709"),

    # Measuring Tools
    "Cross Line Laser": ("Tools & Hardware", "Hand & Measuring Tools", "Lasers & Levels", "Tools & Hardware>Measuring & Layout Tools>Laser Levels", "27111802"),
    "Laser Level": ("Tools & Hardware", "Hand & Measuring Tools", "Lasers & Levels", "Tools & Hardware>Measuring & Layout Tools>Laser Levels", "27111802"),
    "Rafter Square": ("Tools & Hardware", "Hand & Measuring Tools", "Squares", "Tools & Hardware>Measuring & Layout Tools>Squares", "27111800"),
    "Mason Line": ("Tools & Hardware", "Hand & Measuring Tools", "Marking & Layout", "Tools & Hardware>Measuring & Layout Tools>Chalk & Mason Lines", "27111800"),
    "Chalk Reel Set": ("Tools & Hardware", "Hand & Measuring Tools", "Marking & Layout", "Tools & Hardware>Measuring & Layout Tools>Chalk Reels", "27111800"),
    "Caliper Measuring Tool": ("Tools & Hardware", "Hand & Measuring Tools", "Precision Measurement", "Tools & Hardware>Measuring & Layout Tools>Calipers", "27111800"),
    "Digital Tire Inflator Gauge": ("Automotive & Fleet", "Tire & Wheel Tools", "Pressure Gauges", "Automotive>Tire Maintenance>Pressure Gauges", "25172500"),
    "Voltage Detector": ("Electrical", "Test & Measurement", "Voltage Testers", "Electrical>Test Instruments>Voltage Detectors", "41113600"),

    # Accessories & Abrasives
    "Saw Blade": ("Tools & Hardware", "Power Tool Accessories", "Saw Blades", "Tools & Hardware>Power Tool Accessories>Saw Blades>Circular Saw Blades", "27112802"),
    "Track Saw Blade": ("Tools & Hardware", "Power Tool Accessories", "Saw Blades", "Tools & Hardware>Power Tool Accessories>Saw Blades>Track Saw Blades", "27112802"),
    "Cement Track Saw Blade": ("Tools & Hardware", "Power Tool Accessories", "Saw Blades", "Tools & Hardware>Power Tool Accessories>Saw Blades>Specialty Blades", "27112802"),
    "Reciprocating Saw Blade": ("Tools & Hardware", "Power Tool Accessories", "Saw Blades", "Tools & Hardware>Power Tool Accessories>Saw Blades>Reciprocating Blades", "27112802"),
    "Diamond Tile Blade": ("Tools & Hardware", "Power Tool Accessories", "Diamond Blades", "Tools & Hardware>Power Tool Accessories>Diamond Blades", "27112802"),
    "Dado Saw Blade Set": ("Tools & Hardware", "Power Tool Accessories", "Saw Blades", "Tools & Hardware>Power Tool Accessories>Saw Blades>Dado Sets", "27112802"),
    "Driver Bit": ("Tools & Hardware", "Power Tool Accessories", "Screwdriver Bits", "Tools & Hardware>Power Tool Accessories>Driver Bits", "27112814"),
    "Socket Adapter": ("Tools & Hardware", "Power Tool Accessories", "Adapters", "Tools & Hardware>Power Tool Accessories>Socket Adapters", "27112800"),
    "Bit Holder": ("Tools & Hardware", "Power Tool Accessories", "Holders", "Tools & Hardware>Power Tool Accessories>Bit Holders", "27112800"),
    "Battery Mount": ("Tools & Hardware", "Power Tool Accessories", "Storage", "Tools & Hardware>Tool Storage>Battery Mounts", "24102000"),
    "Battery Pack": ("Tools & Hardware", "Power Tool Accessories", "Batteries", "Tools & Hardware>Power Tool Accessories>Batteries", "26111700"),
    "Battery Charger": ("Tools & Hardware", "Power Tool Accessories", "Chargers", "Tools & Hardware>Power Tool Accessories>Chargers", "26111700"),
    "Sanding Belt": ("Abrasives", "Sanding & Finishing", "Sanding Belts", "Abrasives>Sanding & Finishing>Sanding Belts", "31191500"),
    "Sanding Disc": ("Abrasives", "Sanding & Finishing", "Sanding Discs", "Abrasives>Sanding & Finishing>Sanding Discs", "31191500"),
    "Sanding Sheet": ("Abrasives", "Sanding & Finishing", "Sanding Sheets", "Abrasives>Sanding & Finishing>Sanding Sheets", "31191500"),
    "Sanding Sponge": ("Abrasives", "Sanding & Finishing", "Sanding Sponges", "Abrasives>Sanding & Finishing>Sanding Sponges", "31191500"),
    "Cut-Off Disc": ("Abrasives", "Cutting & Grinding Wheels", "Cut-Off Wheels", "Abrasives>Cutting & Grinding Wheels>Cut-Off Wheels", "31191600"),
    "Grinding Wheel": ("Abrasives", "Cutting & Grinding Wheels", "Grinding Wheels", "Abrasives>Cutting & Grinding Wheels>Grinding Wheels", "31191600"),
    "Collated Nails": ("Fasteners & Hardware", "Collated Fasteners", "Nails", "Fasteners>Nails>Collated Nails", "31162000"),
    "Staples": ("Fasteners & Hardware", "Collated Fasteners", "Staples", "Fasteners>Staples>Heavy Duty Staples", "31162000"),

    # Building Materials
    "Composite Deck Board": ("Building Materials", "Decking & Railing", "Deck Boards", "Building Materials>Decking & Railing>Deck Boards", "30103600"),
    "Fascia Board": ("Building Materials", "Decking & Railing", "Fascia", "Building Materials>Decking & Railing>Fascia Boards", "30103600"),
    "Railing Kit": ("Building Materials", "Decking & Railing", "Railing Kits", "Building Materials>Decking & Railing>Railing Kits", "30103601"),
    "Post Sleeve": ("Building Materials", "Decking & Railing", "Post Sleeves", "Building Materials>Decking & Railing>Post Sleeves", "30103601"),
    "Post Wrap": ("Building Materials", "Decking & Railing", "Post Wraps", "Building Materials>Decking & Railing>Post Wraps", "30103601"),
    "Post Trim & Cap": ("Building Materials", "Decking & Railing", "Post Accessories", "Building Materials>Decking & Railing>Post Caps & Trim", "30103601"),
    "Balusters": ("Building Materials", "Decking & Railing", "Balusters", "Building Materials>Decking & Railing>Balusters", "30103601"),
    "Deck Joist Flashing Tape": ("Building Materials", "Waterproofing", "Joist Tape", "Building Materials>Waterproofing>Flashing Tapes", "30151600"),
    "Drywall Gypsum Board": ("Building Materials", "Drywall & Plaster", "Drywall Panels", "Building Materials>Drywall & Gypsum>Panels", "30161500"),
    "Siding Plank / Panel": ("Building Materials", "Siding & Trim", "Planks", "Building Materials>Siding>Engineered Siding", "30151800"),
    "Soffit Panel": ("Building Materials", "Siding & Trim", "Soffit", "Building Materials>Siding>Soffit Panels", "30151800"),
    "Roof Skylight": ("Building Materials", "Doors & Windows", "Skylights", "Building Materials>Windows & Doors>Skylights", "30171600"),
    "Patio / Access Door": ("Building Materials", "Doors & Windows", "Doors", "Building Materials>Windows & Doors>Doors", "30171500"),
    "Window Assembly": ("Building Materials", "Doors & Windows", "Windows", "Building Materials>Windows & Doors>Windows", "30171600"),
    "Door Threshold": ("Building Materials", "Doors & Windows", "Hardware", "Building Materials>Door Hardware>Thresholds", "30171500"),
    "Masonry Mortar Mix": ("Building Materials", "Masonry & Concrete", "Mortar", "Building Materials>Masonry>Mortar Mixes", "30111500"),
    "Rainscreen Flashing": ("Building Materials", "Building Envelope", "Rainscreen", "Building Materials>Moisture Management>Rainscreen", "30151600"),

    # Appliances
    "Dishwasher": ("Appliances", "Large Appliances", "Dishwashers", "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "52141505"),
    "Dryer Heater Kit": ("Appliances", "Laundry Accessories", "Dryer Heating Elements", "Appliances & Consumer Electronics>Laundry Appliances>Dryer Replacement Parts", "52141602"),
    "Clothes Dryer": ("Appliances", "Laundry", "Clothes Dryers", "Appliances & Consumer Electronics>Laundry Appliances>Clothes Dryers", "52141602"),
    "Washing Machine": ("Appliances", "Laundry", "Washing Machines", "Appliances & Consumer Electronics>Laundry Appliances>Washing Machines", "52141601"),
    "Refrigerator": ("Appliances", "Large Appliances", "Refrigerators", "Appliances & Consumer Electronics>Kitchen Appliances>Refrigerators", "24131501"),
    "Freezer": ("Appliances", "Large Appliances", "Freezers", "Appliances & Consumer Electronics>Kitchen Appliances>Freezers", "24131502"),
    "Range": ("Appliances", "Cooking Appliances", "Ranges", "Appliances & Consumer Electronics>Kitchen Appliances>Ranges", "52141514"),
    "Cooktop": ("Appliances", "Cooking Appliances", "Cooktops", "Appliances & Consumer Electronics>Kitchen Appliances>Cooktops", "52141514"),
    "Microwave Oven": ("Appliances", "Cooking Appliances", "Microwave Ovens", "Appliances & Consumer Electronics>Kitchen Appliances>Microwave Ovens", "52141511"),
    "Coffee & Espresso Maker": ("Appliances", "Small Appliances", "Coffee Makers", "Appliances & Consumer Electronics>Small Appliances>Coffee Makers", "52141526"),
    "Toaster": ("Appliances", "Small Appliances", "Toasters", "Appliances & Consumer Electronics>Small Appliances>Toasters", "52141527"),

    # Safety
    "Safety Glasses": ("Safety & Security", "Personal Protective Equipment", "Eye Protection", "Safety & Security>Personal Protective Equipment>Safety Glasses", "46181802"),
    "Heated Work Gloves": ("Safety & Security", "Personal Protective Equipment", "Hand Protection", "Safety & Security>Personal Protective Equipment>Work Gloves", "46181504"),
    "Heated Hoodie": ("Safety & Security", "Workwear & Apparel", "Heated Gear", "Safety & Security>Workwear>Heated Apparel", "46181500"),
    "Kneeling Pad": ("Safety & Security", "Ergonomics", "Kneeling Pads", "Safety & Security>Ergonomics>Kneeling Pads", "46181500"),
    "Hearing Protection Earmuffs": ("Safety & Security", "Personal Protective Equipment", "Hearing Protection", "Safety & Security>Personal Protective Equipment>Hearing Protectors", "46181900"),
    "Fire Extinguisher": ("Safety & Security", "Fire Protection", "Extinguishers", "Safety & Security>Fire Protection>Fire Extinguishers", "46191601"),
    "Smoke & CO Alarm": ("Safety & Security", "Alarms & Detectors", "Smoke Alarms", "Safety & Security>Alarms & Warnings>Smoke Detectors", "46191500")
}

def classify_product(part_desc: str, mfg_part_num: str = "", raw_dept: str = "", raw_class: str = "", raw_fine: str = "") -> dict:
    """
    Dynamically identifies product type and classifies into proper category taxonomy.
    Executes:
    1. Direct regular expression token extraction
    2. Zero-shot AI semantic classification for long-tail industrial items
    3. Strict fallback with is_fallback=True (marked for human review)
    """
    text = f"{part_desc} {mfg_part_num}".strip()
    
    # 1. Primary Regex Pattern Matching
    matched_type = None
    for pattern, p_type in PRODUCT_TYPE_EXTRACTORS:
        if re.search(pattern, text, re.IGNORECASE):
            matched_type = p_type
            break

    if matched_type and matched_type in TAXONOMY_MAP:
        dept, cls, fine, classpath, unspsc = TAXONOMY_MAP[matched_type]
        return {
            "cat_key": matched_type.lower().replace(' ', '_'),
            "Dept": raw_dept or dept,
            "Class": raw_class or cls,
            "Fine": raw_fine or fine,
            "Classpath": classpath,
            "UNSPSC": unspsc,
            "Product Name": matched_type,
            "is_fallback": False,
            "provenance": "REGEX_PRODUCT_TYPE_MATCH"
        }

    # 2. AI Semantic Zero-Shot Classification
    ai_res = semantic_zero_shot_classify(part_desc, mfg_part_num)
    if ai_res:
        return ai_res

    # 3. Honest fallback for truly uncategorized items (NO dishwasher fabrication!)
    clean_pname = "Industrial Product"
    if text:
        tokens = text.split()
        if len(tokens) >= 2:
            clean_pname = f"{tokens[-2]} {tokens[-1]}".title()

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
