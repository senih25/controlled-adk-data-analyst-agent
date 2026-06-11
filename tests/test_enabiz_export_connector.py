import json
from pathlib import Path

import pytest

from connectors.enabiz_export import (
    EnabizExportValidationError,
    load_and_summarize_enabiz_export,
    load_enabiz_anonymized_export,
    validate_contract,
    validate_no_phi,
)


FIXTURE_PATH = Path("fixtures/anonymized_enabiz_export_sample.json")


def _fixture_data() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_load_valid_anonymized_export():
    data = load_enabiz_anonymized_export(FIXTURE_PATH)

    assert data["schema_version"] == "anonymized-enabiz-analytics-v0.1"
    assert data["source"] == "enabiz-local-health-assistant"
    assert data["export_type"] == "aggregate_analytics"
    assert data["privacy"]["phi_free"] is True
    assert data["privacy"]["raw_text_included"] is False
    assert data["privacy"]["pseudonymized"] is True


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


def test_blocks_unsupported_schema_version():
    data = _fixture_data()
    data["schema_version"] = "anonymized-enabiz-analytics-v0.2"

    with pytest.raises(EnabizExportValidationError, match="schema_version must be"):
        validate_contract(data)


def test_blocks_non_pseudonymized_export():
    data = _fixture_data()
    data["privacy"]["pseudonymized"] = False

    with pytest.raises(EnabizExportValidationError, match="privacy.pseudonymized must be true"):
        validate_contract(data)


def test_blocks_invalid_contract_missing_privacy():
    invalid = {
        "schema_version": "anonymized-enabiz-analytics-v0.1",
        "source": "enabiz-local-health-assistant",
        "export_type": "aggregate_analytics",
        "cohort": {},
        "category_counts": {},
        "diagnosis_frequency": [],
        "document_completeness": [],
        "timeline_completeness": {},
        "data_quality": {},
    }

    with pytest.raises(EnabizExportValidationError, match="Missing required top-level keys"):
        validate_contract(invalid)


def test_blocks_raw_text_included_true():
    data = _fixture_data()
    data["privacy"]["raw_text_included"] = True

    with pytest.raises(EnabizExportValidationError, match="privacy.raw_text_included must be false"):
        validate_contract(data)


def test_blocks_export_path_outside_allowed_roots(tmp_path):
    export_path = tmp_path / "unsafe_export.json"
    export_path.write_text(json.dumps(_fixture_data()), encoding="utf-8")

    with pytest.raises(EnabizExportValidationError, match="allowed local export root"):
        load_enabiz_anonymized_export(export_path)


def test_blocks_non_json_extension(tmp_path):
    export_path = tmp_path / "unsafe_export.txt"
    export_path.write_text(json.dumps(_fixture_data()), encoding="utf-8")

    with pytest.raises(EnabizExportValidationError, match=r"must point to a \.json file"):
        load_enabiz_anonymized_export(export_path)
