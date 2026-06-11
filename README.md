# Controlled Data Analyst Agent

A controlled data analyst agent built with Google Agent Development Kit (ADK).

This project started from the Google ADK Data Analyst Agent codelab and evolved into a safer, product-ready prototype with custom BigQuery tools, guardrails, and audit logging.

## Purpose

The goal of this project is to build an AI-first data analyst agent that can:

- Explore datasets safely
- Inspect table schemas
- Run controlled BigQuery analysis
- Explain analytical results clearly
- Generate product and MVP insights from data

## Core Capabilities

- Gemini 2.5 Flash with Vertex AI backend
- Google ADK Web UI
- BigQuery public dataset analysis
- Custom BigQuery tools
- SELECT-only query guardrails
- Automatic LIMIT enforcement
- Query audit logging
- Product-oriented data interpretation

## Project Structure

ai-agents-adk/
  data_analyst_agent/
    __init__.py
    agent.py
    config.py
    tools/
      __init__.py
      bigquery_tools.py
      guardrails.py
      audit.py
  README.md
  requirements.txt

## Current Agent

The current agent is a controlled BigQuery data analyst agent.

It uses custom tools instead of relying only on the default ADK BigQueryToolset because custom tools provide stronger control over:

- Billing and job project
- Allowed datasets
- Allowed query types
- Query limits
- Audit logging
- Product safety

## Why Custom BigQuery Tools?

The built-in ADK BigQueryToolset worked for table discovery and schema inspection, but SQL execution caused authorization and job project issues in the Cloud Shell environment.

The custom tool approach solves this by explicitly setting the BigQuery job project to:

trustable-ai-100mph

This makes the system more predictable and production-friendly.

## Available Tools

### list_cms_medicare_tables

Lists tables from:

bigquery-public-data.cms_medicare

### get_inpatient_charges_2015_schema

Returns the schema of:

bigquery-public-data.cms_medicare.inpatient_charges_2015

### top_5_drg_by_discharges

Runs a controlled analytical query that returns the top 5 DRG definitions by total discharges from:

bigquery-public-data.cms_medicare.inpatient_charges_2015

### run_safe_select_query

Runs SELECT-only BigQuery queries with automatic LIMIT enforcement.

Dangerous SQL operations are blocked.

Blocked operations include:

- INSERT
- UPDATE
- DELETE
- DROP
- ALTER
- CREATE
- TRUNCATE
- MERGE
- GRANT
- REVOKE

## Setup

Activate the virtual environment:

cd ~/ai-agents-adk
source .venv/bin/activate

Install dependencies if needed:

uv pip install -r requirements.txt --no-cache

## Run the Agent

Start ADK Web UI:

adk web --host 0.0.0.0 --port 8000 --allow_origins "regex:https://.*\\.cloudshell\\.dev"

Then open Cloud Shell Web Preview:

Web Preview -> Preview on port 8000

## Test Prompt

Use this prompt in ADK Web UI:

Use the top_5_drg_by_discharges tool to list the top 5 DRG definitions.

Return the result as:
1. a table
2. a 3-point data analyst interpretation
3. an explanation of how this can become a healthcare data product MVP

## Expected Result

The agent should return results similar to:

871 - SEPTICEMIA OR SEVERE SEPSIS W/O MV 96+ HOURS W MCC                  521358
470 - MAJOR JOINT REPLACEMENT OR REATTACHMENT OF LOWER EXTREMITY W/O MCC 463930
291 - HEART FAILURE & SHOCK W MCC                                        221654
292 - HEART FAILURE & SHOCK W CC                                         192975
392 - ESOPHAGITIS, GASTROENT & MISC DIGEST DISORDERS W/O MCC             182443

## Local Checks

Compile Python files:

python -m py_compile data_analyst_agent/agent.py
python -m py_compile data_analyst_agent/config.py
python -m py_compile data_analyst_agent/tools/bigquery_tools.py
python -m py_compile data_analyst_agent/tools/guardrails.py
python -m py_compile data_analyst_agent/tools/audit.py

Test guardrails:

python - <<'PY'
from data_analyst_agent.tools.guardrails import is_select_only, enforce_limit

print("SELECT allowed:", is_select_only("SELECT * FROM table"))
print("DROP blocked:", is_select_only("DROP TABLE x"))
print("LIMIT added:", enforce_limit("SELECT * FROM table", 10))
PY

Expected output:

SELECT allowed: True
DROP blocked: False
LIMIT added: SELECT * FROM table LIMIT 10

Test BigQuery tool:

python - <<'PY'
from data_analyst_agent.tools.bigquery_tools import top_5_drg_by_discharges

result = top_5_drg_by_discharges()
print("job_project:", result["job_project"])
for row in result["results"]:
    print(row["drg_definition"], row["total_discharges"])
PY

## Security Design

This project follows a controlled-tool approach:

- Do not give the model unrestricted SQL execution.
- Keep BigQuery job project fixed.
- Use tool-level guardrails.
- Log tool usage.
- Prefer explicit tools over broad database access.
- Restrict destructive SQL operations.
- Add dataset allowlists before production use.

## Productization Opportunities

This agent can be adapted into:

- Kaggle Dataset Analyst Agent
- SocialRightOS Policy Data Analyst
- Foundry Rule and Fixture Analyst
- Clinical CSV / BigQuery Analyst
- Real Estate Document Risk Analyst
- Public Dataset Research Assistant

## Next Phase

Phase 2: Generic Dataset Analyst

Planned improvements:

1. Support user-selected BigQuery datasets
2. Add dataset and table allowlists
3. Add dry-run cost estimation before query execution
4. Add configurable maximum bytes processed
5. Add structured audit logs
6. Add FastAPI wrapper
7. Add CSV / SQLite / PostgreSQL adapters
8. Add GitHub-ready project packaging
9. Add tests for tools and guardrails
10. Add deployment path for Cloud Run

## Strategic Decision

Use the codelab as a learning foundation, but productize the agent with controlled custom tools.

Final direction:

Learn -> stabilize -> modularize -> secure -> productize

## Test Suite

Run all tests:

pytest

Expected result:

16 passed

## Current Status

Phase 1 completed:
- Modular controlled data analyst agent
- Custom BigQuery tools
- Guardrails
- Audit logging
- ADK Web validation

Phase 2 completed:
- Generic allowlisted dataset/table analysis
- Safe SELECT execution
- Dry-run cost estimation
- Destructive SQL blocking

Phase 3 in progress:
- Test suite added
- Packaging files added
- GitHub-ready cleanup in progress

## License

This project is licensed under the Apache License, Version 2.0.

See the LICENSE file for details.

Copyright 2026 Senih BAYANKULU.

## Data Disclaimer

This repository does not redistribute BigQuery public datasets.

The example queries reference public datasets available through Google BigQuery.
Those datasets remain subject to their original provider terms.

## FastAPI Wrapper

This repository includes a FastAPI wrapper for the controlled analyst tools.

Run locally:

    uvicorn app.main:app --host 0.0.0.0 --port 8080

Open API docs:

    http://127.0.0.1:8080/docs

Core endpoints:

    GET  /
    GET  /health
    GET  /datasets
    GET  /tables
    GET  /schema/{table_key}
    POST /query
    GET  /audit

See [API Reference](docs/api.md) for request and response examples.

## e-Nabiz PHI-Free Aggregate Export Connector

This repository includes a PHI-free connector for aggregate e-Nabiz analytics exports.

The connector is designed to consume only PHI-free aggregate analytics data exported from `enabiz-local-health-assistant`.

It does not accept:

- patient names
- doctor names
- TCKN or national identity numbers
- phone numbers
- email addresses
- physical addresses
- raw PDF text
- raw clinical notes
- free-text report bodies

It can safely analyze:

- category counts
- document completeness
- diagnosis code frequencies
- timeline completeness
- data quality scores
- missing or weak evidence flags

### Connector API Example

Run the API:

    uvicorn app.main:app --host 0.0.0.0 --port 8080

Call the connector endpoint:

    curl -X POST http://127.0.0.1:8080/connectors/enabiz/summarize \
      -H "Content-Type: application/json" \
      -d '{"path":"fixtures/anonymized_enabiz_export_sample.json"}'

If the consumer token gate is enabled locally:

    CONTROLLED_ADK_HANDOFF_TOKEN=dev-local-handoff-token
    curl -X POST http://127.0.0.1:8080/connectors/enabiz/summarize \
      -H "Content-Type: application/json" \
      -H "X-Controlled-ADK-Handoff-Token: dev-local-handoff-token" \
      -d '{"path":"../enabiz-local-health-assistant/exports/anonymized/anonymized_enabiz_analytics.json"}'

Example response fields:

    {
      "status": "success",
      "safe_for_agent_analysis": true,
      "data_quality_score": 0.86,
      "missing_or_weak_documents": []
    }

See [e-Nabiz Export Contract](docs/enabiz_export_contract.md) for the privacy boundary and local path safety rules.

## Real e-Nabiz Export Adapter Plan

The next integration step is to generate a real PHI-free aggregate export from `enabiz-local-health-assistant`.

Producer:

    enabiz-local-health-assistant

Consumer:

    controlled-adk-data-analyst-agent

Planned producer module:

    src/exporters/anonymized_analytics_export.py

Planned export output:

    exports/anonymized/anonymized_enabiz_analytics.json

See [e-Nabiz Real Export Adapter Plan](docs/enabiz_export_adapter_plan.md).
