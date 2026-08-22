"""
UniEnrich Web Governance Studio - FastAPI Application
Provides interactive endpoints for real-time single-item enrichment, batch processing,
downloadable XLSX/CSV generation, and benchmark scorecards.
"""
import os
import io
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse

from engine.pipeline import enrich_single_record, enrich_dataset, DELIVERY_HEADERS
from evaluation.benchmark import run_benchmark_tests

app = FastAPI(title="UniEnrich Governance Studio", version="1.0.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')

# Cache for batch enriched dataframe
ENRICHED_CACHE = None

@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    index_file = os.path.join(TEMPLATES_DIR, 'index.html')
    with open(index_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/api/enrich-single")
async def api_enrich_single(request: Request):
    """Enriches a single user-supplied dirty row and returns the record + audit trace."""
    body = await request.json()
    record, audit = enrich_single_record(body)
    return JSONResponse(content={"record": record, "audit": audit})

@app.get("/api/benchmark-stats")
async def api_benchmark_stats():
    """Returns real-time benchmark evaluation and quality compliance statistics."""
    sample_file = os.path.join(DATA_DIR, 'sample_input.csv')
    df_sample = pd.read_csv(sample_file)
    _, report = run_benchmark_tests()
    return JSONResponse(content=report)

@app.get("/api/process-full-batch")
async def api_process_full_batch():
    """Processes the full 1,000-item sample catalog and caches the result."""
    global ENRICHED_CACHE
    sample_file = os.path.join(DATA_DIR, 'sample_input.csv')
    df_sample = pd.read_csv(sample_file)
    df_enriched, audits = enrich_dataset(df_sample)
    ENRICHED_CACHE = df_enriched
    
    preview_data = df_enriched.head(50).to_dict(orient="records")
    return JSONResponse(content={
        "total_processed": len(df_enriched),
        "columns_count": len(df_enriched.columns),
        "preview": preview_data
    })

@app.get("/api/download-export")
async def api_download_export(format: str = "csv"):
    """Downloads the 252-column enriched dataset in CSV or XLSX format."""
    global ENRICHED_CACHE
    if ENRICHED_CACHE is None:
        sample_file = os.path.join(DATA_DIR, 'sample_input.csv')
        df_sample = pd.read_csv(sample_file)
        ENRICHED_CACHE, _ = enrich_dataset(df_sample)

    if format.lower() == "xlsx":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            ENRICHED_CACHE.to_excel(writer, index=False, sheet_name="Enriched_Delivery_Format")
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=UniEnrich_Delivered_Catalog_252_Cols.xlsx"}
        )
    else:
        stream = io.StringIO()
        ENRICHED_CACHE.to_csv(stream, index=False)
        response_bytes = stream.getvalue().encode("utf-8-sig")
        return StreamingResponse(
            io.BytesIO(response_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=UniEnrich_Delivered_Catalog_252_Cols.csv"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
