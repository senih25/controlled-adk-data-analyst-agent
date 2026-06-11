from google.cloud import bigquery

from data_analyst_agent.config import (
    PROJECT_ID,
    DEFAULT_QUERY_LIMIT,
    MAX_BYTES_PROCESSED,
    ALLOWED_DATASETS,
    ALLOWED_TABLES,
)
from data_analyst_agent.tools.audit import write_audit_log
from data_analyst_agent.tools.guardrails import (
    is_select_only,
    enforce_limit,
    resolve_allowed_table,
    query_uses_only_allowed_tables,
)

BQ_CLIENT = bigquery.Client(project=PROJECT_ID)


def list_allowed_datasets() -> dict:
    """List datasets that this agent is allowed to access."""
    result = {
        "job_project": PROJECT_ID,
        "allowed_datasets": ALLOWED_DATASETS,
    }

    write_audit_log({
        "tool": "list_allowed_datasets",
        "status": "success",
    })

    return result


def list_allowed_tables() -> dict:
    """List tables that this agent is allowed to access."""
    result = {
        "job_project": PROJECT_ID,
        "allowed_tables": ALLOWED_TABLES,
    }

    write_audit_log({
        "tool": "list_allowed_tables",
        "status": "success",
    })

    return result


def list_cms_medicare_tables(limit: int = 10) -> dict:
    """List table names in bigquery-public-data.cms_medicare."""
    query = f"""
    SELECT table_name
    FROM `bigquery-public-data.cms_medicare.INFORMATION_SCHEMA.TABLES`
    ORDER BY table_name
    LIMIT {int(limit)}
    """

    rows = BQ_CLIENT.query(query).result()

    result = {
        "dataset": "bigquery-public-data.cms_medicare",
        "job_project": PROJECT_ID,
        "tables": [row.table_name for row in rows],
    }

    write_audit_log({
        "tool": "list_cms_medicare_tables",
        "dataset": "bigquery-public-data.cms_medicare",
        "limit": limit,
        "status": "success",
    })

    return result


def get_table_schema(table_key_or_id: str) -> dict:
    """Get schema for an allowed BigQuery table."""
    table_id = resolve_allowed_table(table_key_or_id)

    if table_id is None:
        write_audit_log({
            "tool": "get_table_schema",
            "status": "blocked",
            "reason": "table_not_allowed",
            "requested_table": table_key_or_id,
        })
        return {
            "status": "blocked",
            "reason": "Table is not in the allowlist.",
            "requested_table": table_key_or_id,
            "allowed_tables": ALLOWED_TABLES,
        }

    table = BQ_CLIENT.get_table(table_id)

    result = {
        "status": "success",
        "table": table.full_table_id,
        "job_project": PROJECT_ID,
        "num_rows": table.num_rows,
        "columns": [
            {
                "name": field.name,
                "type": field.field_type,
                "mode": field.mode,
            }
            for field in table.schema
        ],
    }

    write_audit_log({
        "tool": "get_table_schema",
        "table": table_id,
        "status": "success",
    })

    return result


def get_inpatient_charges_2015_schema() -> dict:
    """Get schema for bigquery-public-data.cms_medicare.inpatient_charges_2015."""
    return get_table_schema("cms_medicare.inpatient_charges_2015")


def top_5_drg_by_discharges() -> dict:
    """Return top 5 DRG definitions by total discharges from inpatient_charges_2015."""
    query = """
    SELECT
      drg_definition,
      SUM(total_discharges) AS total_discharges
    FROM `bigquery-public-data.cms_medicare.inpatient_charges_2015`
    GROUP BY drg_definition
    ORDER BY total_discharges DESC
    LIMIT 5
    """

    rows = BQ_CLIENT.query(query).result()

    result = {
        "source_table": "bigquery-public-data.cms_medicare.inpatient_charges_2015",
        "job_project": PROJECT_ID,
        "sql_summary": "Grouped inpatient_charges_2015 by drg_definition and summed total_discharges, ordered descending, limited to 5.",
        "results": [
            {
                "drg_definition": row.drg_definition,
                "total_discharges": row.total_discharges,
            }
            for row in rows
        ],
    }

    write_audit_log({
        "tool": "top_5_drg_by_discharges",
        "table": "bigquery-public-data.cms_medicare.inpatient_charges_2015",
        "status": "success",
    })

    return result


def run_safe_select_query(sql: str) -> dict:
    """Run a safe SELECT-only BigQuery query with automatic LIMIT and cost guardrail."""
    if not is_select_only(sql):
        write_audit_log({
            "tool": "run_safe_select_query",
            "status": "blocked",
            "reason": "non_select_or_forbidden_keyword",
        })
        return {
            "status": "blocked",
            "reason": "Only SELECT queries are allowed.",
        }

    if not query_uses_only_allowed_tables(sql):
        write_audit_log({
            "tool": "run_safe_select_query",
            "status": "blocked",
            "reason": "table_not_allowed_or_missing_backticks",
        })
        return {
            "status": "blocked",
            "reason": "Query must use only allowlisted tables and fully qualified table names inside backticks.",
            "allowed_tables": ALLOWED_TABLES,
        }

    safe_sql = enforce_limit(sql, DEFAULT_QUERY_LIMIT)

    dry_run_config = bigquery.QueryJobConfig(
        dry_run=True,
        use_query_cache=False,
    )

    dry_run_job = BQ_CLIENT.query(safe_sql, job_config=dry_run_config)
    bytes_processed = dry_run_job.total_bytes_processed

    if bytes_processed > MAX_BYTES_PROCESSED:
        write_audit_log({
            "tool": "run_safe_select_query",
            "status": "blocked",
            "reason": "max_bytes_processed_exceeded",
            "bytes_processed": bytes_processed,
        })
        return {
            "status": "blocked",
            "reason": "Query cost estimate exceeds the configured maximum bytes processed.",
            "bytes_processed_estimate": bytes_processed,
            "max_bytes_processed": MAX_BYTES_PROCESSED,
        }

    rows = BQ_CLIENT.query(safe_sql).result()

    result_rows = [dict(row.items()) for row in rows]

    write_audit_log({
        "tool": "run_safe_select_query",
        "status": "success",
        "bytes_processed": bytes_processed,
        "row_count": len(result_rows),
    })

    return {
        "status": "success",
        "job_project": PROJECT_ID,
        "bytes_processed_estimate": bytes_processed,
        "sql": safe_sql,
        "rows": result_rows,
    }
