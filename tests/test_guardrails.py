from data_analyst_agent.tools.guardrails import (
    is_select_only,
    enforce_limit,
    resolve_allowed_table,
    query_uses_only_allowed_tables,
)


def test_select_query_is_allowed():
    assert is_select_only("SELECT * FROM `bigquery-public-data.cms_medicare.inpatient_charges_2015`")


def test_drop_query_is_blocked():
    assert not is_select_only("DROP TABLE `bigquery-public-data.cms_medicare.inpatient_charges_2015`")


def test_insert_query_is_blocked():
    assert not is_select_only("INSERT INTO table VALUES (1)")


def test_limit_is_added_when_missing():
    sql = "SELECT * FROM `bigquery-public-data.cms_medicare.inpatient_charges_2015`"
    assert enforce_limit(sql, 10).endswith("LIMIT 10")


def test_limit_is_capped():
    sql = "SELECT * FROM `bigquery-public-data.cms_medicare.inpatient_charges_2015` LIMIT 999999"
    assert "LIMIT 1000" in enforce_limit(sql)


def test_allowed_table_resolves_from_key():
    table_id = resolve_allowed_table("cms_medicare.inpatient_charges_2015")
    assert table_id == "bigquery-public-data.cms_medicare.inpatient_charges_2015"


def test_unknown_table_is_blocked():
    assert resolve_allowed_table("unknown.table") is None


def test_query_must_use_allowed_table():
    sql = "SELECT * FROM `bigquery-public-data.cms_medicare.inpatient_charges_2015` LIMIT 5"
    assert query_uses_only_allowed_tables(sql)


def test_query_with_unallowed_table_is_blocked():
    sql = "SELECT * FROM `some-project.some_dataset.some_table` LIMIT 5"
    assert not query_uses_only_allowed_tables(sql)
