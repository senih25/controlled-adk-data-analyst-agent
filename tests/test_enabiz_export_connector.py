import json
from pathlib import Path

import pytest

from connectors.enabiz_export import (
    EnabizExportValidationError,
    load_and_summarize_enabiz_export,
    load_enabiz_anonymized_export,
    validate_no_phi,
)


FIXTURE_PATH = Path("fixtures/anonymized_enabiz_export_sample.json")


def test_load_valid_anonymized_export():
    data = load_enabiz_anonymized_export(FIXTURE_PATH)

    assert data["export_type"] == "aggregate_analytics"
    assert data["privacy"]["phi_free"] is True
    assert data["privacy"]["raw_text_included"] is False


def test_summarize_valid_anonymized_export():
    summary = load_and_summarize_enabiz_export(FIXTURE_PATH)

    assert summary["status"] == "success"
    assert summary["safe_for_agent_analysis"] is True
    assert summary["case_count"] == 1
    assert summary["data_quality_score"] == 0.86
    assert len(summary["top_categories"]) > 0
    assert len(summary["missing_or_weak_documents"]) == 2


def test_blocks_tckn_like_value():
    with pytest.raises(EnabizExportValidationError):
        validate_no_phi({"safe_field": "12345678901"})


def test_blocks_email_like_value():
    with pytest.raises(EnabizExportValidationError):
        validate_no_phi({"safe_field": "person@example.com"})


def test_blocks_forbidden_raw_text_key():
    with pytest.raises(EnabizExportValidationError):
        validate_no_phi({"raw_text": "some report body"})


def test_blocks_patient_name_key():
    with pytest.raises(EnabizExportValidationError):
        validate_no_phi({"patient_name": "Example Person"})


def test_blocks_invalid_contract_missing_privacy(tmp_path):
    invalid = {
        "schema_version": "anonymized-enabiz-analytics-v0.1",
        "export_type": "aggregate_analytics",
        "cohort": {},
        "category_counts": {},
        "data_quality": {},
    }
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(invalid), encoding="utf-8")

    with pytest.raises(EnabizExportValidationError):
        load_enabiz_anonymized_export(path)


def test_blocks_raw_text_included_true(tmp_path):
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    data["privacy"]["raw_text_included"] = True

    path = tmp_path / "invalid_raw_text.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(EnabizExportValidationError):
        load_enabiz_anonymized_export(path)
