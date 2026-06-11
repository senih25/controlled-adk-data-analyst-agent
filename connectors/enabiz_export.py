from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


FORBIDDEN_KEYS = {
    "patient_name",
    "doctor_name",
    "full_name",
    "first_name",
    "last_name",
    "name",
    "surname",
    "tc",
    "tckn",
    "identity_number",
    "national_id",
    "phone",
    "email",
    "address",
    "raw_text",
    "pdf_text",
    "report_text",
    "rapor_metni",
    "clinical_note",
    "free_text",
}

TCKN_PATTERN = re.compile(r"\b[1-9][0-9]{10}\b")
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
PHONE_PATTERN = re.compile(r"(\+90|0)?\s?5[0-9]{2}\s?[0-9]{3}\s?[0-9]{2}\s?[0-9]{2}")


class EnabizExportValidationError(ValueError):
    """Raised when an e-Nabiz analytics export violates the PHI-free contract."""


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace("-", "_").replace(" ", "_")


def validate_no_phi(value: Any, path: str = "$") -> None:
    """Recursively validate that the export does not contain obvious PHI fields or values."""
    if isinstance(value, dict):
        for key, child in value.items():
            normalized_key = _normalize_key(str(key))
            current_path = f"{path}.{key}"

            if normalized_key in FORBIDDEN_KEYS:
                raise EnabizExportValidationError(
                    f"Forbidden PHI-like key found at {current_path}: {key}"
                )

            validate_no_phi(child, current_path)

    elif isinstance(value, list):
        for index, child in enumerate(value):
            validate_no_phi(child, f"{path}[{index}]")

    elif isinstance(value, str):
        if TCKN_PATTERN.search(value):
            raise EnabizExportValidationError(f"TCKN-like value found at {path}")

        if EMAIL_PATTERN.search(value):
            raise EnabizExportValidationError(f"Email-like value found at {path}")

        if PHONE_PATTERN.search(value):
            raise EnabizExportValidationError(f"Phone-like value found at {path}")


def validate_contract(data: dict[str, Any]) -> None:
    required_top_level_keys = {
        "schema_version",
        "export_type",
        "privacy",
        "cohort",
        "category_counts",
        "data_quality",
    }

    missing = sorted(required_top_level_keys - set(data.keys()))
    if missing:
        raise EnabizExportValidationError(
            f"Missing required top-level keys: {', '.join(missing)}"
        )

    if data.get("export_type") != "aggregate_analytics":
        raise EnabizExportValidationError("export_type must be aggregate_analytics")

    privacy = data.get("privacy", {})
    if privacy.get("phi_free") is not True:
        raise EnabizExportValidationError("privacy.phi_free must be true")

    if privacy.get("raw_text_included") is not False:
        raise EnabizExportValidationError("privacy.raw_text_included must be false")

    validate_no_phi(data)


def load_enabiz_anonymized_export(path: str | Path) -> dict[str, Any]:
    export_path = Path(path)
    data = json.loads(export_path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise EnabizExportValidationError("Export root must be a JSON object")

    validate_contract(data)
    return data


def summarize_enabiz_export(data: dict[str, Any]) -> dict[str, Any]:
    validate_contract(data)

    category_counts = data.get("category_counts", {})
    diagnosis_frequency = data.get("diagnosis_frequency", [])
    document_completeness = data.get("document_completeness", [])
    data_quality = data.get("data_quality", {})
    cohort = data.get("cohort", {})

    missing_documents = [
        item
        for item in document_completeness
        if isinstance(item, dict) and item.get("status") in {"missing", "weak"}
    ]

    top_categories = sorted(
        category_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:5]

    return {
        "status": "success",
        "schema_version": data.get("schema_version"),
        "case_count": cohort.get("case_count"),
        "date_min": cohort.get("date_min"),
        "date_max": cohort.get("date_max"),
        "top_categories": [
            {"category": category, "count": count}
            for category, count in top_categories
        ],
        "top_diagnosis_codes": diagnosis_frequency[:10],
        "missing_or_weak_documents": missing_documents,
        "data_quality_score": data_quality.get("score"),
        "data_quality_flags": data_quality.get("flags", []),
        "safe_for_agent_analysis": True,
    }


def load_and_summarize_enabiz_export(path: str | Path) -> dict[str, Any]:
    data = load_enabiz_anonymized_export(path)
    return summarize_enabiz_export(data)
