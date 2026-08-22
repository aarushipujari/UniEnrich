"""
UniEnrich Manufacturer Web Sourcing & Technical Scraping Engine
Fetches live product specifications, wattage, voltage, applications, and source URLs
from public manufacturer catalogs and technical search indexes.
"""
import urllib.parse
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def query_external_mfr_data(mfg_part_num: str, part_desc: str, brand_name: str) -> dict:
    """
    Executes live web search against manufacturer indexes to retrieve technical specs and citation URLs.
    Never relies on hardcoded MPN checks.
    """
    query_parts = [brand_name.replace('®', '').replace('™', '').strip(), mfg_part_num, part_desc]
    clean_query = " ".join([p for p in query_parts if p and p != '-- Unbranded --'])
    
    if not mfg_part_num and len(clean_query) < 5:
        return {"enriched_via_web": False}

    encoded_query = urllib.parse.quote_plus(f"{clean_query} specifications")
    search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=3.5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = soup.find_all('div', class_='result')
            
            for res in results[:3]:
                link_tag = res.find('a', class_='result__url')
                title_tag = res.find('a', class_='result__snippet') or res.find('h2')
                snippet_tag = res.find('a', class_='result__snippet')

                if link_tag and snippet_tag:
                    raw_href = link_tag.get('href', '')
                    raw_title = title_tag.get_text().strip() if title_tag else ""
                    raw_snippet = snippet_tag.get_text().strip()
                    
                    # Parse duckduckgo redirect URL
                    parsed_url = raw_href
                    if "uddg=" in raw_href:
                        parsed_url = urllib.parse.unquote(raw_href.split("uddg=")[1].split("&")[0])

                    # Extract technical specifications dynamically from snippet
                    extracted_specs = {}
                    
                    # Extract Voltage
                    v_match = re.search(r'(\d{2,3})\s*(?:V|Volt|VAC|VDC)\b', raw_snippet, re.IGNORECASE)
                    if v_match:
                        extracted_specs["Voltage"] = f"{v_match.group(1)} V"

                    # Extract Wattage
                    w_match = re.search(r'(\d{3,5})\s*(?:W|Watt|Watts)\b', raw_snippet, re.IGNORECASE)
                    if w_match:
                        extracted_specs["Wattage"] = f"{w_match.group(1)} W"

                    # Extract Amperage
                    a_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:A|Amp|Amps)\b', raw_snippet, re.IGNORECASE)
                    if a_match:
                        extracted_specs["Amperage"] = f"{a_match.group(1)} A"

                    # Extract Dimensions
                    d_match = re.search(r'(\d+(?:[-/.]\d+)?(?:\s*in|\"|\')?\s*x\s*\d+(?:[-/.]\d+)?(?:\s*in|\"|\')?)', raw_snippet, re.IGNORECASE)
                    if d_match:
                        extracted_specs["Dimensions"] = d_match.group(1)

                    return {
                        "enriched_via_web": True,
                        "source_url": parsed_url,
                        "external_title": raw_title,
                        "raw_snippet": raw_snippet,
                        "extracted_specs": extracted_specs
                    }

    except Exception:
        pass

    return {"enriched_via_web": False}
