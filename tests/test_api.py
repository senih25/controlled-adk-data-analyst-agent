from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "controlled-adk-data-analyst-agent-api"


def test_datasets_endpoint():
    response = client.get("/datasets")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "bigquery-public-data.cms_medicare" in data["datasets"]


def test_tables_endpoint():
    response = client.get("/tables")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "allowed_tables" in data


def test_query_blocks_destructive_sql():
    response = client.post(
        "/query",
        json={"sql": "DROP TABLE `bigquery-public-data.cms_medicare.inpatient_charges_2015`"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "blocked"
    assert data["reason"] is not None


def test_audit_endpoint():
    response = client.get("/audit")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "entries" in data

def test_enabiz_connector_summarize_endpoint():
    response = client.post(
        "/connectors/enabiz/summarize",
        json={"path": "fixtures/anonymized_enabiz_export_sample.json"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["safe_for_agent_analysis"] is True
    assert data["data_quality_score"] == 0.86
    assert len(data["missing_or_weak_documents"]) == 2

