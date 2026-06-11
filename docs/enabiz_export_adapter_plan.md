# e-Nabiz Real Export Adapter Plan

## Purpose

This document defines how `enabiz-local-health-assistant` should generate a PHI-free aggregate analytics export that can be safely consumed by `controlled-adk-data-analyst-agent`.

The export adapter is responsible for converting local structured health outputs into a safe JSON contract.

## Source Repository

Target producer:

    enabiz-local-health-assistant

Target consumer:

    controlled-adk-data-analyst-agent

Consumer endpoint:

    POST /connectors/enabiz/summarize

## Product Flow

    enabiz-capture-tool
        -> enabiz-local-health-assistant
        -> anonymized aggregate export JSON
        -> controlled-adk-data-analyst-agent
        -> dashboard / companion / analytics tools

## Adapter Location in Producer Repo

Recommended path:

    src/exporters/anonymized_analytics_export.py

Recommended output path:

    exports/anonymized/anonymized_enabiz_analytics.json

## Required Export Schema

The exporter must generate a JSON object with the following top-level fields:

    schema_version
    source
    export_type
    generated_at
    privacy
    cohort
    category_counts
    diagnosis_frequency
    document_completeness
    timeline_completeness
    data_quality

## Required Privacy Object

    {
      "phi_free": true,
      "raw_text_included": false,
      "pseudonymized": true,
      "notes": "Aggregate analytics only. No raw clinical text or direct identifiers."
    }

## Allowed Data

The exporter may include:

- aggregate document counts
- category-level counts
- date min / date max
- normalized diagnosis code frequencies
- timeline completeness ratio
- data quality score
- missing document flags
- weak evidence flags
- parser coverage metrics

## Forbidden Data

The exporter must never include:

- patient name
- doctor name
- TCKN
- phone number
- email
- address
- raw PDF text
- raw OCR output
- free clinical notes
- report body text
- prescription free text
- hospital visit full narrative
- direct identifiers

## Example Output

    {
      "schema_version": "anonymized-enabiz-analytics-v0.1",
      "source": "enabiz-local-health-assistant",
      "export_type": "aggregate_analytics",
      "generated_at": "2026-06-11T00:00:00Z",
      "privacy": {
        "phi_free": true,
        "raw_text_included": false,
        "pseudonymized": true,
        "notes": "Aggregate analytics only. No raw clinical text or direct identifiers."
      },
      "cohort": {
        "case_count": 1,
        "date_min": "2021-01-01",
        "date_max": "2026-06-01"
      },
      "category_counts": {
        "diagnoses": 32,
        "lab_results": 18,
        "imaging_reports": 25,
        "prescriptions": 11,
        "procedures": 9,
        "epicrisis": 2,
        "pathology": 1,
        "official_reports": 4
      },
      "diagnosis_frequency": [
        {"code": "M17", "count": 4},
        {"code": "I10", "count": 3}
      ],
      "document_completeness": [
        {"document_type": "official_reports", "status": "available", "count": 4},
        {"document_type": "recent_lab_results", "status": "missing", "count": 0}
      ],
      "timeline_completeness": {
        "events_total": 102,
        "events_with_date": 98,
        "coverage_ratio": 0.96
      },
      "data_quality": {
        "score": 0.86,
        "flags": [
          "recent_lab_results_missing",
          "epicrisis_count_low"
        ]
      }
    }

## Exporter Responsibilities

The producer-side exporter must:

1. Load only structured local outputs.
2. Aggregate fields before export.
3. Remove direct identifiers.
4. Refuse to export raw text.
5. Validate the final JSON against this contract.
6. Save the export to a local file.
7. Print a clear success message with the output path.
8. Fail closed if unsafe fields are detected.

## Consumer Responsibilities

The controlled ADK data analyst agent must:

1. Validate required top-level fields.
2. Validate privacy flags.
3. Block PHI-like keys.
4. Block TCKN-like values.
5. Block email-like values.
6. Block phone-like values.
7. Return only safe summaries.
8. Avoid diagnosis, treatment, disability, or legal conclusions.

## Minimum Producer Test Cases

The producer repo should add tests for:

- valid anonymized export generation
- no raw text included
- no direct identifiers included
- required top-level fields present
- missing document flags generated
- category counts generated
- diagnosis frequency aggregated
- output file written

## Minimum Consumer Test Cases

Already implemented in this repo:

- valid export loads
- summary generated
- TCKN-like value blocked
- email-like value blocked
- phone-like value blocked
- raw_text key blocked
- patient_name key blocked
- invalid privacy contract blocked
- API endpoint returns safe summary

## MVP Implementation Plan

Day 1:

- Add exporter module in `enabiz-local-health-assistant`
- Generate aggregate JSON from existing SQLite / structured CSV outputs
- Add safety validation

Day 2:

- Add tests
- Add CLI command
- Add dashboard export button if available

Day 3:

- Call controlled agent API
- Validate end-to-end flow
- Document integration

## Strategic Value

This adapter turns local private health parsing into AI-safe analytics without exposing raw PHI.

It creates a reusable bridge for:

- health data quality dashboards
- companion agents
- policy analytics
- disability-document readiness checks
- timeline completeness analysis
- portfolio-grade clinical AI safety demos

## Hard Boundary

The adapter is not a medical decision system.

It must not produce:

- diagnosis
- treatment recommendation
- disability percentage
- legal eligibility conclusion
- malpractice assessment

It only produces aggregate analytics readiness signals.
