"""
UniEnrich Generative AI & Semantic NLP Reasoning Engine
Implements a Hybrid Neuro-Symbolic Architecture combining:
1. Generative LLM Structured Extraction & Spec Reasoning (Google Gemini / OpenAI)
2. Local Scikit-Learn TF-IDF N-Gram Vector Classifier (Zero-shot ML fallback)
3. Deterministic Guardrails & Explainability Provenance
"""
import os
import json
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel, Field

# -------------------------------------------------------------
# 1. Structured Pydantic Schema for LLM Output
# -------------------------------------------------------------
class LLMProductEnrichment(BaseModel):
    product_type: str = Field(description="The canonical standard noun phrase for the product, e.g., 'Circular Saw Blade', 'Belt & Spindle Sander'")
    brand_name: str = Field(description="The primary brand name with legal trademark symbol if known, e.g., 'Diablo®', 'Milwaukee®'")
    manufacturer_name: str = Field(description="The full corporate legal entity name of the manufacturer")
    dept: str = Field(description="Primary commercial department, e.g., 'Tools & Hardware', 'Electrical', 'Appliances'")
    class_name: str = Field(description="Category class")
    fine_name: str = Field(description="Category fine classification")
    classpath: str = Field(description="Full hierarchy leaf path delimited by >")
    unspsc: str = Field(description="8-digit UNSPSC commodity code")
    technical_specs: dict[str, str] = Field(description="Key dimensional, electrical, physical, and engineering properties deduced from the input or physical laws")
    feature_highlights: list[str] = Field(description="3 to 5 commercial feature bullet points")
    confidence_score: float = Field(description="Calibrated confidence score between 0.0 and 1.0")
    reasoning_summary: str = Field(description="Brief domain explanation justifying the classification and inferred specs")

# -------------------------------------------------------------
# 2. Local Scikit-Learn TF-IDF N-Gram Vector Taxonomy Model
# -------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# Comprehensive Industrial Corpus for Local ML Classifier (50+ Industrial Taxonomy Classes)
CORPUS_TAXONOMY = [
    # Power Tools & Machinery
    ("Belt & Spindle Sander", "oscillating spindle edge belt sander benchtop woodworking machinery", "Tools & Hardware", "Power Tools", "Sanders & Polishers", "Tools & Hardware>Power Tools>Sanders & Polishers>Spindle Sanders", "27112708"),
    ("Random Orbital Sander", "random orbit orbital sander cordless electric finishing sander", "Tools & Hardware", "Power Tools", "Sanders & Polishers", "Tools & Hardware>Power Tools>Sanders & Polishers>Random Orbital Sanders", "27112708"),
    ("Benchtop Planer", "benchtop planer thickness planer wood carpentry planing machine", "Tools & Hardware", "Power Tools", "Planers & Jointers", "Tools & Hardware>Power Tools>Woodworking Machinery>Planers", "27112700"),
    ("Plunge Router", "plunge router fixed base wood router electronic speed control", "Tools & Hardware", "Power Tools", "Routers", "Tools & Hardware>Power Tools>Routers & Trimmers", "27112700"),
    ("Circular Saw", "circular saw circ saw cordless brushless framing saw track saw", "Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Circular Saws", "27112700"),
    ("Miter Saw", "miter saw compound sliding miter saw dual bevel chop saw", "Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Miter Saws", "27112700"),
    ("Table Saw", "table saw jobsite table saw cabinet saw fence system sawstop", "Tools & Hardware", "Power Tools", "Saws", "Tools & Hardware>Power Tools>Saws>Table Saws", "27112700"),
    ("Hammer Drill", "hammer drill driver brushless cordless percussion drill", "Tools & Hardware", "Power Tools", "Drills & Drivers", "Tools & Hardware>Power Tools>Drills & Drivers>Hammer Drills", "27112703"),
    ("Impact Driver", "impact driver hex hydraulic hex driver brushless high torque", "Tools & Hardware", "Power Tools", "Drills & Drivers", "Tools & Hardware>Power Tools>Drills & Drivers>Impact Drivers", "27112703"),
    ("Angle Grinder", "angle grinder paddle switch slide switch cutoff grinder die grinder", "Tools & Hardware", "Power Tools", "Grinders", "Tools & Hardware>Power Tools>Grinders>Angle Grinders", "27112704"),
    ("Die Grinder", "die grinder straight right angle collet rotary grinding tool", "Tools & Hardware", "Power Tools", "Grinders", "Tools & Hardware>Power Tools>Grinders>Die Grinders", "27112704"),
    ("Framing Nailer", "framing nailer pneumatic cordless 21 30 degree paper strip nails", "Tools & Hardware", "Power Tools", "Nailers & Staplers", "Tools & Hardware>Power Tools>Nailers & Staplers>Framing Nailers", "27112709"),
    ("Brad Nailer", "brad nailer 18 gauge finish straight brad nails", "Tools & Hardware", "Power Tools", "Nailers & Staplers", "Tools & Hardware>Power Tools>Nailers & Staplers>Brad Nailers", "27112709"),

    # Saws Blades & Abrasives
    ("Circular Saw Blade", "saw blade 10in 7-1/4 12in carbide tipped tooth teeth atb framing finish dado", "Tools & Hardware", "Power Tool Accessories", "Saw Blades", "Tools & Hardware>Power Tool Accessories>Saw Blades>Circular Saw Blades", "27112802"),
    ("Track Saw Blade", "track saw blade plunging fine finish laminate cement blade", "Tools & Hardware", "Power Tool Accessories", "Saw Blades", "Tools & Hardware>Power Tool Accessories>Saw Blades>Track Saw Blades", "27112802"),
    ("Reciprocating Saw Blade", "recip saw blade sawzall metal wood demolition pruning blade", "Tools & Hardware", "Power Tool Accessories", "Saw Blades", "Tools & Hardware>Power Tool Accessories>Saw Blades>Reciprocating Blades", "27112802"),
    ("Diamond Tile Blade", "diamond tile blade wet dry continuous rim porcelain ceramic blade", "Tools & Hardware", "Power Tool Accessories", "Diamond Blades", "Tools & Hardware>Power Tool Accessories>Diamond Blades", "27112802"),
    ("Sanding Belt", "sanding belt 1/2x18 3x21 4x24 cloth aluminum oxide ceramic grit", "Abrasives", "Sanding & Finishing", "Sanding Belts", "Abrasives>Sanding & Finishing>Sanding Belts", "31191500"),
    ("Sanding Disc", "sanding disc stikit hook and loop cubitron abranet film backing 5in 6in", "Abrasives", "Sanding & Finishing", "Sanding Discs", "Abrasives>Sanding & Finishing>Sanding Discs", "31191500"),
    ("Sanding Sheet", "sanding sheet grip net mesh abrasive hiolit iridum sheet", "Abrasives", "Sanding & Finishing", "Sanding Sheets", "Abrasives>Sanding & Finishing>Sanding Sheets", "31191500"),
    ("Cut-Off Disc", "cut off disc wheel metal masonry stainless steel thin cutting wheel", "Abrasives", "Cutting & Grinding Wheels", "Cut-Off Wheels", "Abrasives>Cutting & Grinding Wheels>Cut-Off Wheels", "31191600"),
    ("Grinding Wheel", "grinding wheel depressed center wheel type 27 metal grinding", "Abrasives", "Cutting & Grinding Wheels", "Grinding Wheels", "Abrasives>Cutting & Grinding Wheels>Grinding Wheels", "31191600"),

    # Measurement & Layout
    ("Cross Line Laser", "laser level green red beam cross line self leveling spot laser level", "Tools & Hardware", "Hand & Measuring Tools", "Lasers & Levels", "Tools & Hardware>Measuring & Layout Tools>Laser Levels", "27111802"),
    ("Rafter Square", "rafter square t-square framing speed square layout ruler", "Tools & Hardware", "Hand & Measuring Tools", "Squares", "Tools & Hardware>Measuring & Layout Tools>Squares", "27111800"),
    ("Digital Tire Inflator", "tire inflator gauge digital pressure gauge air chuck fleet maintenance", "Automotive & Fleet", "Tire & Wheel Tools", "Pressure Gauges", "Automotive>Tire Maintenance>Pressure Gauges", "25172500"),

    # Lighting & Electrical
    ("LED BR Reflector Bulb", "br40 br30 br20 reflector flood led dimmable light bulb lamp", "Electrical", "Lamps & Bulbs", "LED Bulbs", "Electrical>Lamps & Bulbs>LED Bulbs>Directional & Reflector Bulbs", "39101628"),
    ("LED PAR Flood Bulb", "par38 par30 par20 par16 outdoor wet rated led flood light bulb", "Electrical", "Lamps & Bulbs", "LED Bulbs", "Electrical>Lamps & Bulbs>LED Bulbs>PAR Flood Bulbs", "39101628"),
    ("LED MR16 Spotlight Bulb", "mr16 mr11 gu10 12v spotlight track light bulb led", "Electrical", "Lamps & Bulbs", "LED Bulbs", "Electrical>Lamps & Bulbs>LED Bulbs>MR16 Spotlights", "39101628"),
    ("LED General Purpose Bulb", "a19 a21 st19 edison candle candelabra filament e26 medium base led", "Electrical", "Lamps & Bulbs", "LED Bulbs", "Electrical>Lamps & Bulbs>LED Bulbs>Standard Bulbs", "39101628"),
    ("LED Linear Tube", "t8 t5 t12 linear tube fluorescent replacement bypass ballast led", "Electrical", "Lamps & Bulbs", "Linear Tubes", "Electrical>Lamps & Bulbs>Linear Tubes", "39101605"),
    ("Wall Light Fixture", "wall light sconce vanity bath vanity bracket mount indoor outdoor fixture", "Electrical", "Lighting Fixtures", "Wall Sconces", "Electrical>Lighting Fixtures>Wall Lights", "39111500"),
    ("Ceiling Light Fixture", "ceiling light flush mount semi flush pendant chandelier fixture", "Electrical", "Lighting Fixtures", "Flush Mounts", "Electrical>Lighting Fixtures>Ceiling Lights", "39111500"),
    ("Recessed Downlight", "downlight recessed can retrofit baffle trim led", "Electrical", "Lighting Fixtures", "Downlights", "Electrical>Lighting Fixtures>Recessed Downlights", "39111500"),
    ("Commercial / Shop Light", "highbay lowbay shop light strip wrap fixture led commercial", "Electrical", "Lighting Fixtures", "Commercial", "Electrical>Lighting Fixtures>Commercial Lighting", "39111500"),
    ("Work Flashlight", "flashlight headlamp work light magnetic clip rechargeable lantern", "Electrical", "Portable Lighting", "Flashlights", "Electrical>Portable Lighting>Work Lights", "39111610"),
    ("Circuit Breaker", "circuit breaker tandem standard 1-pole 2-pole 15a 20a 30a 50a homeline qo", "Electrical", "Power Distribution", "Circuit Breakers", "Electrical>Power Distribution>Circuit Breakers", "39121601"),
    ("Portable SOOW Cord", "so cord soow sjoow 600v 300v rubber jacket flexible portable power cord", "Electrical", "Wire & Cable", "Portable Cord", "Electrical>Wire & Cable>Portable Cords", "26121629"),
    ("Building Wire & Cable", "romex nm-b thhn uf-b building copper wire electrical cable", "Electrical", "Wire & Cable", "Building Wire", "Electrical>Wire & Cable>Building Wire", "26121600"),
    ("Receptacle Outlet", "outlet receptacle duplex tamper resistant gfci decorator wall tap", "Electrical", "Wiring Devices", "Outlets & Receptacles", "Electrical>Wiring Devices>Receptacles", "39121406"),
    ("Dimmer Switch", "dimmer switch single pole 3-way slide rotary smart switch", "Electrical", "Wiring Devices", "Dimmers", "Electrical>Wiring Devices>Dimmers", "39122200"),
    ("Electrical Junction Box", "junction box outlet box octagonal square 4-inch metal pvc box", "Electrical", "Enclosures & Boxes", "Junction Boxes", "Electrical>Enclosures & Boxes>Outlet Boxes", "39121300"),

    # Plumbing & Pipe Fittings
    ("Pipe Coupling", "cplg coupling metallic threaded brass copper pvc conduit fitting", "Plumbing & Pumps", "Pipe, Tube & Hose Fittings", "Fittings", "Plumbing & Pumps>Pipe, Tube & Hose Fittings>Couplings", "40142315"),
    ("Pipe Elbow", "elbow 90 deg 45 deg street elbow metallic threaded fitting", "Plumbing & Pumps", "Pipe, Tube & Hose Fittings", "Fittings", "Plumbing & Pumps>Pipe, Tube & Hose Fittings>Elbows", "40142315"),

    # Building Materials & Decking
    ("Composite Deck Board", "decking composite deck board vintage azek pvc square edge grooved decking", "Building Materials", "Decking & Railing", "Deck Boards", "Building Materials>Decking & Railing>Deck Boards", "30103600"),
    ("Railing Kit", "rail kit railing panel composite aluminum horizontal baluster", "Building Materials", "Decking & Railing", "Railing Kits", "Building Materials>Decking & Railing>Railing Kits", "30103601"),
    ("Post Wrap", "post wrap column sleeve trim pvc composite decking accessory", "Building Materials", "Decking & Railing", "Post Wraps", "Building Materials>Decking & Railing>Post Wraps", "30103601"),
    ("Deck Joist Flashing Tape", "joist tape deck flashing waterproofing butyl tape", "Building Materials", "Waterproofing", "Joist Tape", "Building Materials>Waterproofing>Flashing Tapes", "30151600"),
    ("Drywall Gypsum Board", "gypsum board drywall sheetrock lightweight easi-lite fire resistant panel", "Building Materials", "Drywall & Plaster", "Drywall Panels", "Building Materials>Drywall & Gypsum>Panels", "30161500"),
    ("Siding Plank / Panel", "siding smart lap hardieplank hardiepanel engineered composite siding", "Building Materials", "Siding & Trim", "Planks", "Building Materials>Siding>Engineered Siding", "30151800"),
    ("Roof Skylight", "skylight roof window curb mount deck mount velux flashing", "Building Materials", "Doors & Windows", "Skylights", "Building Materials>Windows & Doors>Skylights", "30171600"),

    # Safety & PPE
    ("Smoke & CO Alarm", "smoke co alarm carbon monoxide fire detector battery hardwired 10-year", "Safety & Security", "Alarms & Detectors", "Smoke Alarms", "Safety & Security>Alarms & Warnings>Smoke Detectors", "46191500"),
    ("Fire Extinguisher", "fire extinguisher abc dry chemical commercial residential suppression", "Safety & Security", "Fire Protection", "Extinguishers", "Safety & Security>Fire Protection>Fire Extinguishers", "46191601"),
    ("Safety Glasses", "safety glasses eye protection anti-fog scratch resistant ballistic ppe", "Safety & Security", "Personal Protective Equipment", "Eye Protection", "Safety & Security>Personal Protective Equipment>Safety Glasses", "46181802"),

    # Appliances & Replacement Parts
    ("Dryer Heater Kit", "dryer heater kit heating element electric commercial residential laundry part", "Appliances", "Laundry Accessories", "Dryer Heating Elements", "Appliances & Consumer Electronics>Laundry Appliances>Dryer Replacement Parts", "52141602"),
    ("Dishwasher", "dishwasher built-in tall tub stainless steel wash cycles cleanboost quiet", "Appliances", "Large Appliances", "Dishwashers", "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "52141505"),
    ("Clothes Dryer", "clothes dryer electric gas commercial residential front load laundry", "Appliances", "Laundry", "Clothes Dryers", "Appliances & Consumer Electronics>Laundry Appliances>Clothes Dryers", "52141602"),
    ("Washing Machine", "washing machine top load front load washer laundry center", "Appliances", "Laundry", "Washing Machines", "Appliances & Consumer Electronics>Laundry Appliances>Washing Machines", "52141601"),
    ("Refrigerator", "refrigerator french door top freezer bottom freezer side by side beverage center", "Appliances", "Large Appliances", "Refrigerators", "Appliances & Consumer Electronics>Kitchen Appliances>Refrigerators", "24131501")
]

# Initialize TF-IDF Vectorizer & Feature Matrix
corpus_texts = [f"{t[0]} {t[1]}" for t in CORPUS_TAXONOMY]
VECTORIZER = TfidfVectorizer(ngram_range=(1, 3), analyzer='word', lowercase=True, stop_words='english')
CORPUS_VECTORS = VECTORIZER.fit_transform(corpus_texts)

def predict_ml_taxonomy(text: str, mpn: str = "") -> dict | None:
    """
    Local Scikit-Learn TF-IDF Cosine Similarity Taxonomy Predictor.
    Provides real ML zero-shot semantic matching without cloud API keys.
    """
    query = f"{text} {mpn}".strip().lower()
    if not query:
        return None
        
    query_vec = VECTORIZER.transform([query])
    sims = cosine_similarity(query_vec, CORPUS_VECTORS)[0]
    best_idx = int(np.argmax(sims))
    best_score = float(sims[best_idx])
    
    if best_score >= 0.22:
        entry = CORPUS_TAXONOMY[best_idx]
        return {
            "Product Name": entry[0],
            "Dept": entry[2],
            "Class": entry[3],
            "Fine": entry[4],
            "Classpath": entry[5],
            "UNSPSC": entry[6],
            "cat_key": entry[0].lower().replace(' ', '_'),
            "is_fallback": False,
            "confidence": round(min(0.96, best_score * 1.6), 2),
            "provenance": f"LOCAL_TFIDF_VECTOR_COSINE (Sim: {round(best_score, 3)})"
        }
    return None

# -------------------------------------------------------------
# 3. Generative AI Reasoner (Gemini / OpenAI API Integration)
# -------------------------------------------------------------
def run_generative_enrichment(raw_desc: str, mpn: str, supplier_manuf: str, raw_brand: str) -> dict | None:
    """
    Calls Google Gemini or OpenAI with structured schema to reason over sparse industrial rows.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    prompt = f"""You are a master industrial catalog content specialist for Unilog.
Analyze the following sparse/messy distributor product row and extract standard commerce-ready intelligence:

Input Data:
- Part Description: "{raw_desc}"
- Manufacturer Part Number (MPN): "{mpn}"
- Supplier / Manufacturer: "{supplier_manuf}"
- Raw Brand: "{raw_brand}"

Rules:
1. Product Type: Canonical standard product noun (e.g. 'Belt & Spindle Sander', 'Cross Line Laser', 'Drywall Gypsum Board').
2. Legal Brand: Correct canonical brand with legal trademark symbol (®, ™) if applicable.
3. Classpath: Full hierarchical category path matching industrial distributor taxonomy.
4. Technical Specs: Dimensional, electrical, physical, and mounting specs (with valid UOMs e.g. 'in', 'V', 'A', 'W', 'RPM', 'dBA').
5. Zero Hallucination: Do not invent ungrounded serial numbers.
"""

    # 1. Try Google Gemini if key available
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash", generation_config={"response_mime_type": "application/json"})
            resp = model.generate_content(prompt)
            data = json.loads(resp.text)
            data["provenance"] = "GEMINI_GENAI_STRUCTURED_REASONING"
            return data
        except Exception:
            pass

    # 2. Try OpenAI if key available
    if openai_key:
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(resp.choices[0].message.content)
            data["provenance"] = "OPENAI_GENAI_STRUCTURED_REASONING"
            return data
        except Exception:
            pass

    # 3. Graceful ML Neural / Vector Fallback
    ml_res = predict_ml_taxonomy(raw_desc, mpn)
    if ml_res:
        return {
            "product_type": ml_res["Product Name"],
            "dept": ml_res["Dept"],
            "class_name": ml_res["Class"],
            "fine_name": ml_res["Fine"],
            "classpath": ml_res["Classpath"],
            "unspsc": ml_res["UNSPSC"],
            "technical_specs": {},
            "feature_highlights": [f"Commercial grade {ml_res['Product Name']}"],
            "confidence_score": ml_res["confidence"],
            "reasoning_summary": f"Classified via local Scikit-Learn TF-IDF vector embeddings with cosine similarity confidence {ml_res['confidence']}.",
            "provenance": ml_res["provenance"]
        }

    return None
