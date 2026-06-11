# e-Nabiz Anonymized Analytics Export Contract

## Purpose

This contract defines the safe bridge between enabiz-local-health-assistant and controlled-adk-data-analyst-agent.

The controlled analyst agent must only consume PHI-free aggregate analytics exports.

## Allowed Data

The export may include:

- category counts
- date ranges
- document completeness status
- normalized diagnosis code frequencies
- timeline completeness metrics
- data quality scores
- non-identifying aggregate flags

## Forbidden Data

The export must not include:

- patient names
- doctor names
- TCKN or national identity numbers
- phone numbers
- email addresses
- physical addresses
- raw PDF text
- raw clinical notes
- free-text report bodies
- direct identifiers

## Required Top-Level Fields

- schema_version
- export_type
- privacy
- cohort
- category_counts
- data_quality

## Required Privacy Flags

- phi_free: true
- raw_text_included: false
- pseudonymized: true

## Agent Boundary

The controlled ADK data analyst agent may summarize:

- data quality
- missing evidence
- completeness
- aggregate frequency patterns
- analysis readiness

The agent must not produce:

- diagnosis
- treatment advice
- disability percentage
- legal conclusion
- malpractice assessment
- medical decision

## Strategic Role

This contract allows healthcare-related analytics to be connected to AI agents without exposing raw PHI or sensitive clinical text.
