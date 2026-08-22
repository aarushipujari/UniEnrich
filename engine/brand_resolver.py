"""
UniEnrich Canonical Brand & Manufacturer Resolver
Fuzzy & exact entity matching against UniCat reference data with legal trademark symbols (®, ™).
"""
import os
import json
import re
from rapidfuzz import process, fuzz
from .sanitizer import clean_placeholder, strip_trailing_distributor_codes

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

with open(os.path.join(DATA_DIR, 'master_brands.json'), 'r', encoding='utf-8') as f:
    MASTER_BRANDS = json.load(f)

ALIASES = {k.lower(): v for k, v in MASTER_BRANDS.get('aliases', {}).items()}
CANONICAL = MASTER_BRANDS.get('canonical', {})

# Fast pattern check for prominent brands embedded in MPN / Part_Desc
DESC_BRAND_HINTS = [
    ("Speed Queen", ["d519127", "speed queen", "sq ", "df7004", "dr7004", "dv2000", "dc5004", "ff7011", "dr5004", "tv2000", "tc5003", "tr7006", "tr5006", "v & v appliance"]),
    ("FRIGIDAIRE", ["frigidaire", "pdsh", "gcfg", "prfs", "pmos"]),
    ("Whirlpool", ["whirlpool", "wdts", "wmms", "wsgs"]),
    ("GE Appliances", ["ge ", "ge_", "pdt", "pdd", "ptd", "ptw", "gde", "fcm", "gne", "pad", "pge", "pep", "ps960", "pb900", "pcwk", "gcst", "jxgriLL"]),
    ("Café", ["café", "cafe", "ces700", "chp90", "cvm51", "c9tma", "c7cda", "c7ceb", "c7ces", "cve28"]),
    ("KitchenAid", ["kitchen aid", "kitchenaid", "kdfm", "kdts", "kdps", "kmmf", "kses"]),
    ("LG", ["lg ", "lg-", "ldph", "wke100", "lt18", "mser2090", "lsel6333"]),
    ("Beko", ["beko", "wosp30100"]),
    ("Element", ["element", "erfd19", "euf17", "euf21"]),
    ("Milwaukee", ["milw", "milwaukee", "48-", "49-", "25", "27", "28", "29", "30", "32", "34", "0887", "m12", "m18", "packout"]),
    ("DEWALT", ["dewalt", "dewlt", "dcd", "dcf", "dcg", "dcm", "dcn", "dcl", "dcs", "dw", "dcgg", "dwmt", "dzn", "dwht"]),
    ("Makita", ["makita", "xnb", "xrf", "xlt", "xvp", "xru", "xts", "bl1850", "191v", "gsl02", "a-96095"]),
    ("Diablo", ["diablo", "freud", "dcb", "dbd", "dph", "dsq", "dt1", "dt2", "dt3", "dt4", "ddwssb", "d0860", "d0760", "d0708", "d1012", "d1216", "djt155", "d0604", "d0620", "d0648", "d0652", "dfbl", "dsa"]),
    ("3M", ["3m", "3mabr", "stikit", "cubitron", "scotch"]),
    ("Mirka", ["mirka", "hiolit", "abranet", "iridium", "deos", "5b-", "9a-", "24-"]),
    ("Festool", ["festool", "etsc", "systainer", "577", "578"]),
    ("Trex", ["trex", "543", "15137", "select classic", "lineage", "transcend", "enhance"]),
    ("TimberTech", ["timbertech", "azek", "adb", "agb", "adcb", "adr", "adcr", "1508395", "1508396"]),
    ("Kichler", ["kichler", "45297", "45573", "37418", "45496", "45973", "55155", "55157", "55184", "55210", "44072", "52033", "84322", "52404", "34686", "43671", "52616", "52678", "52772", "82399", "42955", "42275", "42296", "43913", "52476", "42199", "42200", "43851", "43905", "52529", "52662", "52734", "82400", "43849", "59061", "59062", "59124", "59025"]),
    ("Satco", ["satco", "nuvo", "starfish", "65-", "62-", "64-", "s11", "s21", "s35", "s34", "s37", "s47"]),
    ("Philips", ["philips", "phillips", "141465", "391227", "392225", "467316", "567313", "586875", "576355", "576363", "565374", "565390", "576371", "576496", "564856", "565796", "576389", "564492", "586909", "566364", "571497", "576306", "588533", "576520", "574004", "574012", "573971", "573989", "576769", "567446", "573997", "571463", "576512", "581181", "566430", "568337", "565788", "565770", "573436", "576538", "573451", "586883", "586859", "576488", "575217", "586479", "571471", "570762", "533352", "573519", "573378", "565622", "586891", "585448", "573444", "566687", "564385", "566661", "564898", "538319", "576009", "564450", "572669", "564906", "573410", "576504", "576017", "574392", "576751", "583161", "566695", "577007", "566653", "566679", "573311", "573394", "573329", "564930", "565000", "564922", "573295", "564914", "573485", "573337", "544874", "570846", "565473", "573402", "573352", "573428", "573386", "564948", "573303", "573188", "573469", "565671", "573204", "581199", "565887", "586867", "568451", "568444", "573196", "564500", "571513", "588566", "565655", "565812", "586917"]),
    ("WiZ", ["wiz", "603571", "603449"]),
    ("ProVia", ["provia", "ecoliteplus", "1501831", "1501832"]),
    ("United Window & Door", ["united window & door", "united", "1517602", "1517603", "1517604", "1517605", "1515974"]),
    ("Velux", ["velux", "fs c01", "fs c04", "fs c06"]),
    ("First Alert", ["first alert", "1046793"]),
    ("BRK", ["brk", "1046870"]),
    ("Wera", ["wera", "05134545001", "133164", "950/9", "9516"]),
    ("Kreg", ["kreg", "kpt", "bcb2a20a", "batt4a", "batt2a", "crgr401a"]),
    ("Irwin", ["irwin", "iwht"]),
    ("Senco", ["senco", "k527", "vb0212"]),
    ("Dremel", ["dremel", "4000-", "3100-"]),
    ("Bosch", ["bosch", "gcl165", "ts1017"]),
    ("Oliver Machinery", ["oliver", "10047vs", "4225.201", "kc-426c", "10045.201", "10014.201", "4430.201", "10055.201"]),
    ("Grizzly", ["grizzly", "g0771z", "t27417"]),
    ("SawStop", ["sawstop", "tgp2-fa", "atgi-fa", "atgp-fa", "tgi2-fa", "tgi2-t36a"]),
    ("Bow Products", ["bow products", "xt524", "xt536", "xt546", "xtp235", "xtp242"]),
    ("Leviton", ["leviton", "r02-", "pbuc", "r00-", "r92-", "r12-", "r62-", "165-04729", "161-04720", "r56-", "r20-05378", "r51-", "s03-", "174-0csb3", "r50-", "r52-"]),
    ("Square D", ["square d", "hom2040", "hom3060", "qo612"]),
    ("Southwire", ["southwire", "bha1", "g1941", "g1950", "g1951", "52c3", "52c14", "54151", "54171", "52151", "72171", "wc1v12w", "13093005", "r50003", "10-4 so", "2/2/4 ud", "55418901"]),
    ("Hager", ["hager", "413s"]),
    ("Hunter Fan", ["hunter", "51334", "59210", "52485", "52486", "52487", "52488", "52655", "59261", "51731"]),
    ("James Hardie", ["hardie", "jameshardie", "8912220", "8904015"]),
    ("LP SmartSide", ["smartside", "smart lap", "smart pan", "smart vented", "25796", "40503", "25825", "25822"]),
    ("CertainTeed", ["certainteed", "easi-lite", "firelite", "640383", "653258"]),
    ("Prebena", ["prebena", "d10cnk", "e28cnkha"]),
    ("Malco", ["malco", "avm6ev", "avm7"]),
    ("Vessel", ["vessel", "qb22", "220usb", "ibmg", "ibph"]),
    ("Woodpeckers", ["woodpeckers", "bc-12300", "bc-24600", "aas-p", "sscms"]),
    ("Marshalltown", ["marshalltown", "wal-board", "40025", "vn56920"]),
    ("Edge Safety", ["edge safety", "tsdkap", "xpap418", "xdap419", "xb11pcvs", "kb121vs", "kb126vs", "tc121vs", "tc126vs", "mk113mpap", "ls117mpap"]),
    ("Lutron", ["lutron", "aycl-"]),
    ("Prime Wire & Cable", ["prime", "tnocd", "tndhd", "tnidp", "tniw24"]),
    ("Feit Electric", ["feit", "shop/4x2", "work6000"]),
    ("GT-Lite", ["gt-lite", "gt-cb-100c"]),
    ("Schumacher", ["schumacher", "sl1672"]),
    ("StealthMounts", ["stealthmounts", "bm-dw20"]),
    ("Carlon", ["carlon", "a410rcar"]),
    ("Streamlight", ["streamlight", "73020 nano"]),
    ("NEBO", ["nebo", "slyde king", "neb-flt"]),
    ("Police Security", ["police security", "97708"]),
    ("Rees Cast Stone", ["rees cast stone", "25-a", "38-e", "59-j", "44-a"]),
    ("MillerTech", ["millertech", "402-r"]),
    ("UTW Pro", ["utw pro", "mwug42", "mwug36"]),
    ("Sabre", ["sabre", "hs-da"]),
    ("National Nail", ["national nail", "603150", "918200"]),
    ("CMT", ["cmt", "230.312", "790.82", "794.321"]),
    ("JET", ["jet", "jt1-549", "jt1-1371", "jt9-714400k"]),
    ("King Canada", ["king canada", "58006", "kc-426c"])
]

def format_canonical_result(canon_dict: dict, provenance: str, conf: float) -> dict:
    return {
        "MANUFACTURER_NAME": canon_dict.get("mfg_name", ""),
        "BRAND_NAME": canon_dict.get("brand_name", ""),
        "mfg_code": canon_dict.get("mfg_code", ""),
        "brand_code": canon_dict.get("brand_code", ""),
        "provenance": provenance,
        "confidence": conf
    }

def resolve_brand(e1_brand: str, unilog_brand: str, dib_brand: str, part_manuf: str, part_desc: str, mfg_part_num: str) -> dict:
    raw_brands = [
        clean_placeholder(unilog_brand),
        clean_placeholder(e1_brand),
        clean_placeholder(dib_brand)
    ]
    raw_brand = next((b for b in raw_brands if b), "")
    clean_manuf = strip_trailing_distributor_codes(clean_placeholder(part_manuf))
    clean_desc = (part_desc or "").lower()
    clean_mpn = (mfg_part_num or "").lower()
    
    # 1. First check if raw_brand exists in ALIASES
    if raw_brand:
        key = raw_brand.lower()
        if key in ALIASES:
            canon_key = ALIASES[key]
            if canon_key in CANONICAL:
                return format_canonical_result(CANONICAL[canon_key], 'EXACT_BRAND_ALIAS', 1.0)

    # 2. Check part_manuf against ALIASES
    if clean_manuf:
        m_lower = clean_manuf.lower()
        if m_lower in ALIASES:
            canon_key = ALIASES[m_lower]
            if canon_key in CANONICAL:
                return format_canonical_result(CANONICAL[canon_key], 'MANUF_ALIAS_RESOLVED', 0.98)

    # 3. Check part_desc, MPN, and part_manuf against DESC_BRAND_HINTS
    combined_search_text = f"{clean_desc} {clean_mpn} {clean_manuf.lower()}"
    for canon_name, triggers in DESC_BRAND_HINTS:
        for trig in triggers:
            if trig in combined_search_text:
                if canon_name in CANONICAL:
                    return format_canonical_result(CANONICAL[canon_name], 'DESC_MPN_HINT_RESOLVED', 0.95)

    # 4. Fuzzy match against ALIASES keys
    search_terms = [clean_manuf, raw_brand, (part_desc or "")[:30]]
    search_term = next((t for t in search_terms if t), "")
    if search_term:
        best_match = process.extractOne(search_term.lower(), ALIASES.keys(), scorer=fuzz.token_set_ratio)
        if best_match and best_match[1] >= 80:
            canon_key = ALIASES[best_match[0]]
            if canon_key in CANONICAL:
                return format_canonical_result(CANONICAL[canon_key], 'FUZZY_ENTITY_RESOLVED', round(best_match[1]/100.0, 2))

    # 5. Fallback
    fallback_name = raw_brand or clean_manuf or "Unbranded"
    return {
        'MANUFACTURER_NAME': clean_manuf or fallback_name,
        'BRAND_NAME': fallback_name,
        'mfg_code': '',
        'brand_code': '',
        'provenance': 'FALLBACK_RAW',
        'confidence': 0.60
    }
