import os
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_BIGQUERY_INTEGRATION_TESTS") != "1",
    reason="BigQuery integration tests require credentials and RUN_BIGQUERY_INTEGRATION_TESTS=1",
)

from data_analyst_agent.tools.bigquery_tools import (
    list_allowed_tables,
    get_table_schema,
    run_safe_select_query,
    top_5_drg_by_discharges,
)


def test_list_allowed_tables_contains_inpatient_charges():
    result = list_allowed_tables()

    assert result["job_project"] == "trustable-ai-100mph"
    assert "cms_medicare.inpatient_charges_2015" in result["allowed_tables"]


def test_get_table_schema_for_allowed_table():
    result = get_table_schema("cms_medicare.inpatient_charges_2015")

    assert result["status"] == "success"
    assert result["job_project"] == "trustable-ai-100mph"

    column_names = [column["name"] for column in result["columns"]]

    assert "drg_definition" in column_names
    assert "total_discharges" in column_names


def test_get_table_schema_blocks_unknown_table():
    result = get_table_schema("unknown.table")

    assert result["status"] == "blocked"
    assert result["reason"] == "Table is not in the allowlist."


def test_top_5_drg_by_discharges_returns_rows():
    result = top_5_drg_by_discharges()

    assert result["job_project"] == "trustable-ai-100mph"
    assert result["source_table"] == "bigquery-public-data.cms_medicare.inpatient_charges_2015"
    assert len(result["results"]) == 5
    assert result["results"][0]["total_discharges"] >= result["results"][-1]["total_discharges"]


def test_run_safe_select_query_success():
    sql = """
    SELECT
      drg_definition,
      SUM(total_discharges) AS total_discharges
    FROM `bigquery-public-data.cms_medicare.inpatient_charges_2015`
    GROUP BY drg_definition
    ORDER BY total_discharges DESC
    LIMIT 5
    """

    result = run_safe_select_query(sql)

    assert result["status"] == "success"
    assert result["job_project"] == "trustable-ai-100mph"
    assert result["bytes_processed_estimate"] > 0
    assert len(result["rows"]) == 5


def test_run_safe_select_query_blocks_drop():
    result = run_safe_select_query(
        "DROP TABLE `bigquery-public-data.cms_medicare.inpatient_charges_2015`"
    )

    assert result["status"] == "blocked"
    assert result["reason"] == "Only SELECT queries are allowed."


def test_run_safe_select_query_blocks_unallowed_table():
    sql = "SELECT * FROM `some-project.some_dataset.some_table` LIMIT 5"

    result = run_safe_select_query(sql)

    assert result["status"] == "blocked"
    assert "allowlisted" in result["reason"]
