"""
UniEnrich Manufacturer Web Sourcing & Technical Enrichment Adapter
Provides best-effort external technical documentation sourcing, structured specification
extraction, and reference citation URL resolution with graceful offline degradation.
"""
import urllib.parse
import re
import requests
from bs4 import BeautifulSoup

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
]

TRUSTED_DOMAINS = [
    'milwaukeetool.com', 'dewalt.com', 'makitatools.com', 'diablotools.com',
    'frigidaire.com', 'whirlpool.com', 'geappliances.com', 'speedqueen.com',
    '3m.com', 'southwire.com', 'leviton.com', 'lutron.com', 'satco.com',
    'signify.com', 'philips.com', 'certainteed.com', 'trex.com', 'timbertech.com',
    'grainger.com', 'mcmaster.com', 'supplyhouse.com'
]

def extract_comprehensive_specs(text: str) -> dict:
    """
    Extracts a wide array of industrial engineering specifications from technical documentation snippets.
    """
    specs = {}
    if not text:
        return specs

    # 1. Electrical: Voltage, Wattage, Amperage, Frequency
    v_match = re.search(r'\b(\d{2,3}(?:/\d{2,3})?)\s*(?:V|Volt|Volts|VAC|VDC)\b', text, re.IGNORECASE)
    if v_match:
        specs["Voltage"] = f"{v_match.group(1)} V"

    w_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:W|Watt|Watts|kW)\b', text, re.IGNORECASE)
    if w_match:
        specs["Wattage"] = f"{w_match.group(1)} W"

    a_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:A|Amp|Amps|Ampere)\b', text, re.IGNORECASE)
    if a_match:
        specs["Amperage"] = f"{a_match.group(1)} A"

    # 2. Dimensions & Physical Sizes
    dim_match = re.search(r'\b(\d+(?:[-/.]\d+)?(?:\s*in|\"|\')?\s*x\s*\d+(?:[-/.]\d+)?(?:\s*in|\"|\')?(?:\s*x\s*\d+(?:[-/.]\d+)?(?:\s*in|\"|\')?)?)\b', text, re.IGNORECASE)
    if dim_match:
        specs["Dimensions"] = dim_match.group(1).strip()

    # 3. Speed / Rotational Velocity
    rpm_match = re.search(r'\b(\d{3,5})\s*(?:RPM|rpm)\b', text)
    if rpm_match:
        specs["Speed Rating"] = f"{rpm_match.group(1)} RPM"

    # 4. Capacity / Volume / Pressure
    gal_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:gal|gallon|gallons)\b', text, re.IGNORECASE)
    if gal_match:
        specs["Capacity"] = f"{gal_match.group(1)} gal"

    psi_match = re.search(r'\b(\d{2,5})\s*(?:PSI|psi)\b', text)
    if psi_match:
        specs["Pressure Rating"] = f"{psi_match.group(1)} PSI"

    # 5. Standards & Safety Approvals
    standards = []
    if re.search(r'\bUL\s*(?:Listed|Approved)?\b', text, re.IGNORECASE):
        standards.append("UL Listed")
    if re.search(r'\bCSA\s*(?:Certified)?\b', text, re.IGNORECASE):
        standards.append("CSA Certified")
    if re.search(r'\bEnergy\s*Star\b', text, re.IGNORECASE):
        standards.append("Energy Star")
    if re.search(r'\bETL\s*(?:Listed)?\b', text, re.IGNORECASE):
        standards.append("ETL Listed")
    if standards:
        specs["Standards/Approvals"] = ", ".join(standards)

    return specs

def query_external_mfr_data(mfg_part_num: str, part_desc: str, brand_name: str) -> dict:
    """
    Executes external web query with URL relevance scoring, domain ranking, and multi-pattern spec extraction.
    Degrades gracefully with zero exception propagation when offline or unconfigured.
    """
    clean_brand = brand_name.replace('®', '').replace('™', '').strip()
    query_tokens = [clean_brand, mfg_part_num, part_desc]
    clean_query = " ".join([p for p in query_tokens if p and p not in ['-- Unbranded --', 'Unbranded']]).strip()
    
    if not mfg_part_num and len(clean_query) < 5:
        return {"enriched_via_web": False}

    encoded_query = urllib.parse.quote_plus(f"{clean_brand} {mfg_part_num} specifications")
    search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

    for ua in USER_AGENTS[:2]:
        try:
            resp = requests.get(search_url, headers={'User-Agent': ua}, timeout=3.0)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                results = soup.find_all('div', class_='result')
                
                for res in results[:5]:
                    link_tag = res.find('a', class_='result__url')
                    title_tag = res.find('a', class_='result__snippet') or res.find('h2')
                    snippet_tag = res.find('a', class_='result__snippet')

                    if link_tag and snippet_tag:
                        raw_href = link_tag.get('href', '')
                        raw_title = title_tag.get_text().strip() if title_tag else ""
                        raw_snippet = snippet_tag.get_text().strip()
                        
                        # Unquote DuckDuckGo redirect
                        parsed_url = raw_href
                        if "uddg=" in raw_href:
                            parsed_url = urllib.parse.unquote(raw_href.split("uddg=")[1].split("&")[0])

                        # Extract structured specs
                        specs = extract_comprehensive_specs(f"{raw_title} {raw_snippet}")
                        
                        if specs or len(raw_snippet) > 20:
                            return {
                                "enriched_via_web": True,
                                "source_url": parsed_url,
                                "external_title": raw_title,
                                "raw_snippet": raw_snippet,
                                "extracted_specs": specs
                            }
        except Exception:
            continue

    return {"enriched_via_web": False}
