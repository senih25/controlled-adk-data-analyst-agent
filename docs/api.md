# API Reference

## Overview

Controlled ADK Data Analyst Agent exposes a FastAPI wrapper around safe analytical tools.

The API provides:

- Health checks
- Dataset discovery
- Table discovery
- Schema inspection
- Safe SELECT-only query execution
- Audit log access

The API does not allow destructive SQL operations.

## Run Locally

    uvicorn app.main:app --host 0.0.0.0 --port 8080

Open:

    http://127.0.0.1:8080/docs

## Endpoints

### GET /

Returns available API routes.

Example:

    curl http://127.0.0.1:8080/

### GET /health

Returns service health status.

Example:

    curl http://127.0.0.1:8080/health

Expected response:

    {
      "status": "ok",
      "service": "controlled-adk-data-analyst-agent-api",
      "version": "0.1.0"
    }

### GET /datasets

Returns allowlisted datasets.

Example:

    curl http://127.0.0.1:8080/datasets

### GET /tables

Returns allowlisted tables.

Example:

    curl http://127.0.0.1:8080/tables

### GET /schema/{table_key}

Returns schema for an allowlisted table.

Example:

    curl http://127.0.0.1:8080/schema/cms_medicare.inpatient_charges_2015

### POST /query

Runs a safe SELECT-only query.

Example:

    curl -X POST http://127.0.0.1:8080/query \
      -H "Content-Type: application/json" \
      -d '{"sql":"SELECT drg_definition, SUM(total_discharges) AS total_discharges FROM `bigquery-public-data.cms_medicare.inpatient_charges_2015` GROUP BY drg_definition ORDER BY total_discharges DESC LIMIT 5"}'

Expected response fields:

    {
      "status": "success",
      "job_project": "trustable-ai-100mph",
      "bytes_processed_estimate": 11401378,
      "row_count": 5,
      "rows": [],
      "reason": null
    }

### Unsafe Query Example

    curl -X POST http://127.0.0.1:8080/query \
      -H "Content-Type: application/json" \
      -d '{"sql":"DROP TABLE `bigquery-public-data.cms_medicare.inpatient_charges_2015`"}'

Expected response:

    {
      "status": "blocked",
      "rows": [],
      "reason": "Only SELECT queries are allowed."
    }

### GET /audit

Returns recent audit log entries.

Example:

    curl http://127.0.0.1:8080/audit

Optional limit:

    curl "http://127.0.0.1:8080/audit?limit=10"

## Security Rules

The API enforces:

- SELECT-only SQL
- Destructive keyword blocking
- Allowlisted BigQuery tables
- Fully qualified BigQuery table names
- Automatic LIMIT enforcement
- Dry-run cost estimation
- Audit logging

## Product Value

This API turns the ADK codelab result into a reusable backend service that can be integrated with:

- React dashboards
- Kaggle analysis tools
- SocialRightOS policy engines
- Foundry rule analysis
- Clinical analytics workflows
- Internal BI tools

### POST /connectors/enabiz/summarize

Summarizes a PHI-free aggregate e-Nabiz analytics export.

This endpoint validates the export contract before producing a summary.

Example:

    curl -X POST http://127.0.0.1:8080/connectors/enabiz/summarize \
      -H "Content-Type: application/json" \
      -d '{"path":"fixtures/anonymized_enabiz_export_sample.json"}'

Expected response fields:

    {
      "status": "success",
      "schema_version": "anonymized-enabiz-analytics-v0.1",
      "case_count": 1,
      "top_categories": [],
      "top_diagnosis_codes": [],
      "missing_or_weak_documents": [],
      "data_quality_score": 0.86,
      "data_quality_flags": [],
      "safe_for_agent_analysis": true
    }

Safety behavior:

- blocks direct identifiers
- blocks TCKN-like values
- blocks email-like values
- blocks phone-like values
- blocks raw_text / pdf_text / clinical_note fields
- requires privacy.phi_free=true
- requires privacy.raw_text_included=false
