# UniEnrich — Industrial Product Intelligence & Governance Platform

UniEnrich is an enterprise AI-powered catalog enrichment pipeline and governance studio built for industrial distributors. It transforms noisy, cryptic, and unstandardized raw supplier catalog records into **252-column, fully standardized, commerce-ready product intelligence**.

Built strictly in accordance with:
* **Unilog Internal Content Guidelines**
* **Master UOM Standards & Abbreviations**
* **Decimal-to-Fraction Conversion Tables (63 exact 64th lookups)**
* **UniCat Manufacturer & Brand Controlled Vocabularies**

---

## Key Features

1. **Deterministic Rule Engine + AI Entity Resolution**:
   - Strips placeholders (`-- Unbranded --`, `-- No Unilog Brand --`).
   - Normalizes manufacturers and brands to canonical legal names with mandatory trademark symbols (`®`, `™`, `Inc.`, `LLC`).
   - Zero hallucination guarantee: attribute labels and values strictly follow category LOVs.

2. **5-Tier Multi-Channel Description Generation**:
   - **Tier 1: Invoice Description**: $\le 40$ chars, strictly UPPERCASE, dense trade abbreviations.
   - **Tier 2: Mobile Description**: $60 - 80$ chars, concise structure: `[Manufacturer] [Brand], [Product Type], [Series], [MPN]`.
   - **Tier 3: Product Title / Short Description**: Formula-based: `[Brand®] [Series] [MPN] [Item Type] [With Modifier], [Key Attributes]`.
   - **Tier 4: Long Description**: Comprehensive sentence capturing electrical, dimensional, mounting, and material specs.
   - **Tier 5: Retail Description & Feature Bullets**: High-impact marketing highlights.

3. **Decimal-to-Fraction & UOM Normalization**:
   - Enforces exact conversions (e.g. `50.25 in` $\to$ `50-1/4 in`, `0.5` $\to$ `1/2`).
   - Enforces strict spacing (`24 in`, not `24in`) and approved abbreviations (`V`, `A`, `W`, `dBA`, `kW-hr`, `GA`, `TPI`).

4. **Digital Asset & Document Mapping**:
   - Generates standardized image filenames (`BRAND_MPN.jpg`, `BRAND_MPN_1.jpg`) and specification sheet PDFs (`BRAND_MPN_Specification_Sheet.pdf`).

5. **Explainability & Provenance Trace**:
   - Every cell outputs its confidence score and origin trail (`[EXACT_BRAND_ALIAS]`, `[DECIMAL_FRACTION_LOOKUP]`, `[LOV_NORMALIZED]`).

---

## Quick Start & Usage

### 1. Launch the Interactive Web Governance Studio
```bash
python web/app.py
```
Open **http://127.0.0.1:8000** in your browser to:
- Test real-time single-item enrichment with the interactive sandbox.
- Inspect all 252 fields, LOV attribute triplets, and explainability traces.
- Run batch enrichment on the full 1,000 items and download `.xlsx` / `.csv` files.

### 2. Run Batch Enrichment via CLI
```bash
python run_enrichment.py
```
This processes `data/sample_input.csv` (1,000 records) and outputs:
- `data/UniEnrich_Delivered_Catalog_252_Cols.xlsx`
- `data/UniEnrich_Delivered_Catalog_252_Cols.csv`

### 3. Run Benchmark & Evaluation Suite
```bash
python run_benchmark.py
```
Evaluates accuracy, character-limit compliance, and brand match rates against ground truth data.

---

## Project Structure

```
c:\Users\aarus\Desktop\unihack\
├── data/
│   ├── sample_input.csv                # 1,000 raw input rows
│   ├── expected_output_headers.csv     # 252 static delivery headers
│   ├── master_brands.json              # Canonical UniCat brand/mfg DB
│   ├── decimal_fraction.json           # 63 exact fraction lookups
│   ├── uom_standards.json              # Approved unit standards & house rules
│   └── category_lovs.json              # Category taxonomy & LOV schemas
├── engine/
│   ├── sanitizer.py                    # Preprocessing & placeholder stripping
│   ├── brand_resolver.py               # Fuzzy + exact brand/mfg resolver with ®/™
│   ├── taxonomy_classifier.py          # Classpath & UNSPSC predictor
│   ├── attribute_extractor.py          # Spec extraction & LOV validator
│   ├── uom_normalizer.py               # Decimal-fraction & UOM standardizer
│   ├── copy_synthesizer.py             # 5-tier multi-format copybuilder
│   ├── asset_mapper.py                 # Image & PDF spec sheet naming
│   ├── explainability.py               # Confidence & provenance audit engine
│   └── pipeline.py                     # Master pipeline orchestrator
├── evaluation/
│   └── benchmark.py                    # Ground truth scoring harness
├── web/
│   ├── app.py                          # FastAPI governance studio server
│   └── templates/
│       └── index.html                  # Sleek interactive dashboard
├── run_enrichment.py                   # Batch CLI runner
├── run_benchmark.py                    # Evaluation CLI runner
├── requirements.txt                    # Python dependencies
└── README.md
```
