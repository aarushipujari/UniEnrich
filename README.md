# UniEnrich — Industrial Commerce Catalog Enrichment Platform

UniEnrich is an enterprise-grade catalog enrichment system designed specifically for industrial, electrical, and commercial B2B distributors (such as Unilog, Grainger, and Ferguson). It transforms sparse, messy, or minimal supplier records (e.g. `D519127 Heater Kit` or `3/8 CPLG BRS 150#`) into **252-column, fully standardized, commerce-ready product data**.

---

## 1. System Architecture & Capabilities

```mermaid
flowchart TD
    Raw["Raw Sparse Industrial Row<br/>MPN / Unbranded Desc / Cryptic Text"] --> Hybrid["UniEnrich Multi-Stage Pipeline"]
    
    subgraph Sourcing["Sourcing & Disambiguation"]
        Hybrid --> Web["Auxiliary Web Sourcing Adapter - Optional<br/>Public Specs & Documentation Sourcing"]
        Hybrid --> Brand["General Dynamic N-Gram Entity Resolver<br/>Token Hygiene, RapidFuzz, Curated Master Brand Catalog"]
    end
    
    subgraph NLP["Classification & NLP"]
        Hybrid --> Tax["Taxonomy Classifier<br/>Longest-Match Specificity & Scikit-Learn TF-IDF"]
        Hybrid --> LLM["Generative AI Reasoner - Optional<br/>Google Gemini / OpenAI Structured Schemas"]
    end
    
    subgraph GuardrailsArea["Enterprise Guardrails"]
        Tax --> Guardrails["Deterministic Guardrail Engine<br/>- Master UOM Standards<br/>- 63 Exact 64th Fraction Conversions<br/>- Hard Invoice le 40 Chars & Mobile le 80 Chars<br/>- Zero Speculative Factual Guessing"]
        Brand --> Guardrails
        Web --> Guardrails
    end
    
    Guardrails --> Output["252-Column Commerce-Ready Export<br/>Full Cell Provenance & Quality Audit Trace"]
```

### Key Engineering Modules:
1. **Dynamic N-Gram Entity & Brand Resolver (`engine/brand_resolver.py`)**:
   - Extracts 1-gram, 2-gram, and 3-gram phrases dynamically across supplier descriptions and manufacturer names, matching them against the Master Brand & Manufacturer Catalog (`data/master_brands.json`).
   - **Zero Hardcoded Brand Family Lists**: Completely purged static brand lists; uses dynamic dictionary lookups and RapidFuzz token-set scoring.
   - Strips distributor trailing codes (e.g. `(APPDE)`, `(3658)`, `(VVAPP)`) and guarantees official legal trademark symbols (`®`, `™`) across 100% of resolved brands.

2. **Hierarchical Taxonomy Classifier (`engine/taxonomy_classifier.py` & `engine/ai_agent.py`)**:
   - Uses weighted longest-match compound noun ranking and pre-classification color/noise stripping to prevent category collisions.
   - Incorporates a local **Scikit-Learn TF-IDF N-Gram Vector Classifier** for offline zero-shot semantic matching across 50+ industrial taxonomy nodes.
   - Supports Cloud LLM inference (`google-generativeai`, `openai`) when API keys are configured in the environment.

3. **Grounded Spec Extraction & Physical Guardrails (`engine/inference_engine.py`)**:
   - Extracts and normalizes factual dimensional, electrical, and physical specifications directly grounded in input text or official documentation.
   - **Zero Factual Guessing**: Does not fabricate arbitrary numeric ratings (e.g. RPM or kerf) into catalog columns.

4. **Multi-Channel Copywriting Synthesizer (`engine/copy_synthesizer.py`)**:
   - **`INVOICE_DESC`**: Hard $\le 40$ character ceiling, uppercase, universal algorithmic consonant-extractor.
   - **`MOBILE_DESC`**: Strictly grounded in real product attributes, $\le 80$ characters, **zero synthetic filler phrases**.
   - **`SHORT_DESC` / Product Title**: Strict Unilog standard formula (`[Brand®] [Series] [MPN] [Item Type] [With Modifier], [Key Attributes]`).
   - **`LONG_DESC1`**: Grammatically complete technical narrative.

5. **Explainability & Human-in-the-Loop Governance (`engine/explainability.py` & `web/app.py`)**:
   - Multi-factor empirical confidence scoring ($0.0 - 1.0$) combining brand certainty, taxonomy specificity, and grounded attribute volume with cell-level provenance logging (`EXACT_ALIAS`, `GROUNDED_TEXT_EXTRACTION`, `WEB_SOURCING`, `TFIDF_VECTOR`).
   - Automatically routes unbranded, ambiguous, or low-confidence rows ($\le 0.80$) to a dedicated `NEEDS_HUMAN_REVIEW` queue.

6. **Auxiliary Web Sourcing Adapter (`engine/web_enricher.py`)**:
   - Best-effort external search adapter that retrieves auxiliary public documentation and extracts electrical, physical, and safety certification attributes (`UL`, `CSA`, `Energy Star`) when connectivity is available, with graceful zero-error degradation to offline ML when unavailable.

---

## 2. Benchmark Scorecard (Held-Out Evaluation)

```
=== UniEnrich Ground Truth & Quality Benchmark Scorecard ===

[A. GROUND TRUTH ACCURACY (Held-Out Evaluation Dataset - 200 Records)]
  * Records Evaluated:                       200 (0 overlapping MPNs with sample_input.csv)
  * Exact Brand Name Match:                  89.5%
  * Exact Legal Manufacturer Match:          93.5%
  * Classpath Hierarchy Match:                83.5%
  * UNSPSC Commodity Match:                  90.0%
  * Digital Asset Spec Naming:               82.5%

[B. SCALE DATASET QUALITY & COMPLIANCE (1,000 Catalog Rows)]
  * Total Records Processed:                 1,000
  * Schema Columns Count:                    252 / 252 (100% Header Invariance)
  * Invoice Length Compliance (≤40):         100.0%
  * Invoice Uppercase Compliance:            100.0%
  * Mobile Ceiling Compliance (≤80):         100.0%
  * Brand Resolution Rate:                   97.1%
  * Auto-Verified Records:                   694
  * Human Review Queue Flagged:              306
```

---

## 3. Quickstart & Usage

### Setup
```bash
pip install -r requirements.txt
```

### Launch Interactive Governance Studio
```bash
python web/app.py
```
Open **`http://127.0.0.1:8000`** to view catalog records, confidence filters, audit traces, and the human review queue.

### Run Batch Processing (1,000 Rows)
```bash
python run_enrichment.py
```
Outputs:
- `data/UniEnrich_Delivered_Catalog_252_Cols.csv`
- `data/UniEnrich_Delivered_Catalog_252_Cols.xlsx`

### Run Disjoint Benchmark Suite
```bash
python run_benchmark.py
```
