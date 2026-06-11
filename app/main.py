from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from app.schemas import HealthResponse, QueryRequest, QueryResponse
from app.services.analyst_service import (
    audit_tail,
    datasets,
    demo_top_5_drg,
    health,
    query,
    schema,
    tables,
)


app = FastAPI(
    title="Controlled ADK Data Analyst Agent API",
    description="Safe FastAPI wrapper for controlled BigQuery analysis tools.",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse)
def get_health() -> dict[str, str]:
    return health()


@app.get("/datasets")
def get_datasets() -> dict:
    return datasets()


@app.get("/tables")
def get_tables() -> dict:
    return tables()


@app.get("/schema/{table_key}")
def get_schema(table_key: str) -> dict:
    result = schema(table_key)
    if result.get("status") != "success":
        raise HTTPException(status_code=400, detail=result)
    return result


@app.post("/query", response_model=QueryResponse)
def run_query(payload: QueryRequest) -> dict:
    result = query(payload.sql)
    if result.get("status") == "blocked":
        return {
            "status": "blocked",
            "reason": result.get("reason"),
            "rows": [],
        }
    return {
        "status": result.get("status", "unknown"),
        "job_project": result.get("job_project"),
        "bytes_processed_estimate": result.get("bytes_processed_estimate"),
        "row_count": result.get("row_count"),
        "rows": result.get("rows", []),
        "reason": result.get("reason"),
    }


@app.get("/demo/top-5-drg")
def get_top_5_drg() -> dict:
    return demo_top_5_drg()


@app.get("/audit")
def get_audit(limit: int = Query(default=50, ge=1, le=500)) -> dict:
    return audit_tail(limit=limit)
