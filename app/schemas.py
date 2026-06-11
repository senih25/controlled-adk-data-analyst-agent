from pydantic import BaseModel, Field
from typing import Any


class QueryRequest(BaseModel):
    sql: str = Field(..., min_length=1)


class QueryResponse(BaseModel):
    status: str
    job_project: str | None = None
    bytes_processed_estimate: int | None = None
    row_count: int | None = None
    rows: list[dict[str, Any]] = []
    reason: str | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

class EnabizExportPathRequest(BaseModel):
    path: str = Field(..., min_length=1)

