from __future__ import annotations

from pathlib import Path
from typing import Any

from connectors.enabiz_export import load_and_summarize_enabiz_export
from data_analyst_agent.tools.bigquery_tools import (
    list_allowed_tables,
    get_table_schema,
    run_safe_select_query,
    top_5_drg_by_discharges,
)


AUDIT_LOG_PATH = Path("logs/bigquery_audit.log")


def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "controlled-adk-data-analyst-agent-api",
        "version": "0.1.0",
    }


def datasets() -> dict[str, Any]:
    return {
        "status": "success",
        "datasets": [
            "bigquery-public-data.cms_medicare",
        ],
    }


def tables() -> dict[str, Any]:
    result = list_allowed_tables()
    if "status" not in result:
        result = {
            "status": "success",
            **result,
        }
    return result


def schema(table_key: str) -> dict[str, Any]:
    return get_table_schema(table_key)


def query(sql: str) -> dict[str, Any]:
    return run_safe_select_query(sql)


def demo_top_5_drg() -> dict[str, Any]:
    return top_5_drg_by_discharges()


def audit_tail(limit: int = 50) -> dict[str, Any]:
    if not AUDIT_LOG_PATH.exists():
        return {
            "status": "success",
            "path": str(AUDIT_LOG_PATH),
            "entries": [],
        }

    lines = AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines()
    return {
        "status": "success",
        "path": str(AUDIT_LOG_PATH),
        "entries": lines[-limit:],
    }

def summarize_enabiz_export_path(path: str) -> dict[str, Any]:
    return load_and_summarize_enabiz_export(path)

