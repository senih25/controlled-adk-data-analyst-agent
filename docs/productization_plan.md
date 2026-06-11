# Productization Plan

## Product Vision

Controlled ADK Data Analyst Agent is a reusable AI-first data analysis template for safe dataset exploration, analytical querying, and product/MVP insight generation.

The long-term goal is to turn this prototype into a reusable agent framework that can support:

- Kaggle dataset analysis
- Policy and eligibility analytics
- Clinical data analysis
- Public dataset research
- Real estate document risk analysis
- Internal business intelligence workflows

## Current Status

Completed:

- Google ADK setup
- Gemini 2.5 Flash with Vertex AI backend
- Custom BigQuery tools
- SELECT-only SQL guardrails
- Allowlisted table access
- Dry-run cost estimation
- Audit logging
- English README
- Test suite with 16 passing tests
- GitHub repository publication

## Phase 1: Controlled Data Analyst Agent

Status: Complete

Delivered:

- Modular agent structure
- Custom BigQuery tools
- Guardrail layer
- Audit layer
- ADK Web validation

## Phase 2: Generic Dataset Analyst

Status: Complete

Delivered:

- Allowed dataset registry
- Allowed table registry
- Generic schema inspection
- Safe SELECT query execution
- Cost estimation
- Unsafe query blocking

## Phase 3: Tests and Packaging

Status: Complete

Delivered:

- pytest setup
- guardrail tests
- BigQuery tool tests
- .gitignore
- .env.example
- requirements.txt
- GitHub-ready structure

## Phase 4: Architecture Documentation

Status: In progress

Deliverables:

- architecture.md
- productization_plan.md
- future deployment notes

## Phase 5: Generic BigQuery Expansion

Goal:

Allow users to analyze additional BigQuery datasets safely.

Planned work:

1. Add configurable dataset allowlist
2. Add configurable table allowlist
3. Add table metadata cache
4. Add schema summarization
5. Add query template generation
6. Add max bytes processed enforcement
7. Add user-friendly error messages

## Phase 6: FastAPI Wrapper

Goal:

Expose the agent capabilities through a backend API.

Potential endpoints:

- GET /health
- GET /datasets
- GET /tables
- GET /schema/{table_key}
- POST /query
- GET /audit
- POST /analyze

## Phase 7: UI Layer

Goal:

Build a lightweight web interface for dataset analysis.

Possible stack:

- FastAPI backend
- React / Vite frontend
- BigQuery analysis panel
- Query preview
- Cost estimate display
- Result table
- Analyst summary
- Audit viewer

## Phase 8: Project Integrations

### Kaggle Dataset Analyst Agent

Use case:

- EDA automation
- schema understanding
- leakage risk detection
- baseline model planning

### SocialRightOS Policy Data Analyst

Use case:

- eligibility outcome analysis
- policy impact simulation
- rejection reason clustering
- threshold sensitivity analysis

### Foundry Rule and Fixture Analyst

Use case:

- fixture coverage analysis
- rule consistency checks
- adversarial data inspection
- evaluation report generation

### Clinical CSV / BigQuery Analyst

Use case:

- clinical data quality checks
- lab anomaly analysis
- patient cohort summaries
- risk signal extraction

### Real Estate Document Risk Analyst

Use case:

- document field extraction
- registry consistency checks
- missing document detection
- risk report generation

## Security Roadmap

Planned improvements:

1. Strict dataset/table allowlist
2. SELECT-only enforcement
3. Query LIMIT enforcement
4. Max bytes processed guardrail
5. Audit log persistence
6. Sensitive data redaction
7. Role-based access control
8. User-level query quotas
9. Prompt injection checks
10. Tool-level permission scopes

## Deployment Roadmap

Potential deployment targets:

- Google Cloud Run
- Vertex AI Agent Engine
- Internal FastAPI service
- GitHub Codespaces demo
- Local developer environment

## Success Metrics

Technical metrics:

- tests passing
- safe query blocking rate
- average query latency
- average bytes processed
- tool execution success rate
- audit coverage

Product metrics:

- time saved in dataset analysis
- number of datasets analyzed
- number of reusable insights generated
- number of MVP ideas produced
- analyst satisfaction score

## Strategic Decision

The project should continue as a reusable controlled-agent template.

Priority direction:

Learn -> stabilize -> modularize -> secure -> productize -> deploy
