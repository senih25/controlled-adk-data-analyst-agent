# Architecture

## Overview

Controlled ADK Data Analyst Agent is a Google ADK-based data analysis agent designed for safe, auditable, and product-ready dataset exploration.

The system combines:

- Google ADK
- Gemini 2.5 Flash
- Vertex AI backend
- Custom BigQuery tools
- SQL guardrails
- Audit logging
- Automated tests

## High-Level Flow

User prompt
-> ADK agent
-> Tool selection
-> Guardrail validation
-> BigQuery dry-run cost estimate
-> Safe query execution
-> Audit log
-> Analyst-style response

## Core Components

### 1. ADK Agent

File:

data_analyst_agent/agent.py

Responsibilities:

- Defines the root agent
- Registers available tools
- Provides system instructions
- Enforces analyst-style output format

### 2. Configuration Layer

File:

data_analyst_agent/config.py

Responsibilities:

- Project configuration
- Allowed dataset registry
- Allowed table registry
- Query limits
- Maximum bytes processed
- Audit log path

### 3. BigQuery Tool Layer

File:

data_analyst_agent/tools/bigquery_tools.py

Responsibilities:

- List allowed datasets
- List allowed tables
- Inspect table schemas
- Run predefined analytical queries
- Run safe SELECT-only queries
- Perform dry-run cost estimation
- Write audit events

### 4. Guardrail Layer

File:

data_analyst_agent/tools/guardrails.py

Responsibilities:

- Block non-SELECT queries
- Block destructive SQL keywords
- Enforce query LIMIT
- Cap excessive LIMIT values
- Validate allowlisted tables
- Require fully qualified BigQuery table names

### 5. Audit Layer

File:

data_analyst_agent/tools/audit.py

Responsibilities:

- Append structured JSON audit events
- Track successful tool calls
- Track blocked queries
- Track query cost estimates
- Support later compliance and observability work

## Security Model

The agent does not receive unrestricted database access.

Instead, it uses controlled tools with:

- Allowlisted tables
- SELECT-only enforcement
- Forbidden keyword blocking
- Automatic LIMIT enforcement
- BigQuery dry-run cost checks
- Fixed job project
- Audit logging

## Current Allowlisted Tables

- bigquery-public-data.cms_medicare.inpatient_charges_2015
- bigquery-public-data.cms_medicare.hospital_general_info
- bigquery-public-data.cms_medicare.outpatient_charges_2015

## Current Tool List

- list_allowed_datasets
- list_allowed_tables
- list_cms_medicare_tables
- get_table_schema
- get_inpatient_charges_2015_schema
- top_5_drg_by_discharges
- run_safe_select_query

## Data Flow Example

Prompt:

"Run a safe SELECT query on inpatient_charges_2015 and return the top 5 DRG definitions by total discharges."

Flow:

1. Agent receives prompt.
2. Agent selects run_safe_select_query.
3. Guardrail checks that query is SELECT-only.
4. Guardrail validates that the table is allowlisted.
5. LIMIT is enforced.
6. BigQuery dry-run estimates bytes processed.
7. Query executes under the fixed job project.
8. Result rows are returned.
9. Audit event is written.
10. Agent explains results.

## Testing

The project includes tests for:

- SELECT-only validation
- Destructive SQL blocking
- LIMIT enforcement
- Allowlisted table resolution
- BigQuery schema inspection
- Safe query execution
- Blocked unsafe queries

Current test status:

16 passed

## Design Decision

The project intentionally uses custom BigQuery tools instead of relying only on the built-in ADK BigQueryToolset.

Reason:

Custom tools provide better control over:

- Security
- Billing project
- Query scope
- Cost limits
- Auditability
- Product readiness
