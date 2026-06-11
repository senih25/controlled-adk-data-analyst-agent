from __future__ import annotations

import os
from secrets import compare_digest

from fastapi import FastAPI, HTTPException, Query, Header

from app.schemas import EnabizExportPathRequest, HealthResponse, QueryRequest, QueryResponse
from app.services.analyst_service import (
    audit_tail,
    datasets,
    demo_top_5_drg,
    health,
    query,
    schema,
    tables,
    summarize_enabiz_export_path,
)
from connectors.enabiz_export import EnabizExportValidationError

HANDOFF_TOKEN_HEADER = "X-Controlled-ADK-Handoff-Token"
HANDOFF_TOKEN_ENV = "CONTROLLED_ADK_HANDOFF_TOKEN"


app = FastAPI(
    title="Controlled ADK Data Analyst Agent API",
    description="Safe FastAPI wrapper for controlled BigQuery analysis tools.",
    version="0.1.0",
)


@app.get("/")
def root() -> dict:
    return {
        "status": "ok",
        "service": "Controlled ADK Data Analyst Agent API",
        "docs": "/docs",
        "health": "/health",
        "datasets": "/datasets",
        "tables": "/tables",
        "audit": "/audit",
        "query": "/query",
    }


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
    rows = result.get("rows", [])
    row_count = result.get("row_count")
    if row_count is None:
        row_count = len(rows)

    return {
        "status": result.get("status", "unknown"),
        "job_project": result.get("job_project"),
        "bytes_processed_estimate": result.get("bytes_processed_estimate"),
        "row_count": row_count,
        "rows": rows,
        "reason": result.get("reason"),
    }


@app.get("/demo/top-5-drg")
def get_top_5_drg() -> dict:
    return demo_top_5_drg()


@app.get("/audit")
def get_audit(limit: int = Query(default=50, ge=1, le=500)) -> dict:
    return audit_tail(limit=limit)


@app.post("/connectors/enabiz/summarize")
def summarize_enabiz_export(
    payload: EnabizExportPathRequest,
    handoff_token: str | None = Header(default=None, alias=HANDOFF_TOKEN_HEADER),
) -> dict:
    _validate_handoff_token(handoff_token)
    try:
        return summarize_enabiz_export_path(payload.path)
    except EnabizExportValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail={"status": "blocked", "reason": str(exc)},
        ) from exc


def _validate_handoff_token(handoff_token: str | None) -> None:
    expected_token = os.getenv(HANDOFF_TOKEN_ENV)
    if not expected_token:
        return

    if handoff_token is None or not compare_digest(handoff_token, expected_token):
        raise HTTPException(
            status_code=403,
            detail={
                "status": "blocked",
                "reason": "Controlled ADK handoff token is missing or invalid.",
            },
        )
