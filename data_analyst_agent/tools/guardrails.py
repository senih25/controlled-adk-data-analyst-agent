import re

from data_analyst_agent.config import (
    DEFAULT_QUERY_LIMIT,
    MAX_QUERY_LIMIT,
    ALLOWED_TABLES,
)

FORBIDDEN_SQL_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "MERGE",
    "GRANT",
    "REVOKE",
    "CALL",
    "EXPORT",
]


def normalize_sql(sql: str) -> str:
    return re.sub(r"\s+", " ", sql.strip())


def is_select_only(sql: str) -> bool:
    normalized = normalize_sql(sql).upper()

    if not normalized.startswith("SELECT"):
        return False

    for keyword in FORBIDDEN_SQL_KEYWORDS:
        if re.search(rf"\b{keyword}\b", normalized):
            return False

    return True


def enforce_limit(sql: str, default_limit: int = DEFAULT_QUERY_LIMIT) -> str:
    normalized = normalize_sql(sql)

    match = re.search(r"\bLIMIT\s+(\d+)\b", normalized, flags=re.IGNORECASE)
    if match:
        current_limit = int(match.group(1))
        if current_limit > MAX_QUERY_LIMIT:
            return re.sub(
                r"\bLIMIT\s+\d+\b",
                f"LIMIT {MAX_QUERY_LIMIT}",
                normalized,
                flags=re.IGNORECASE,
            )
        return normalized

    return f"{normalized} LIMIT {default_limit}"


def is_allowed_table(table_id: str) -> bool:
    return table_id in ALLOWED_TABLES.values()


def resolve_allowed_table(table_key_or_id: str) -> str | None:
    if table_key_or_id in ALLOWED_TABLES:
        return ALLOWED_TABLES[table_key_or_id]

    if table_key_or_id in ALLOWED_TABLES.values():
        return table_key_or_id

    return None


def query_uses_only_allowed_tables(sql: str) -> bool:
    normalized = normalize_sql(sql)

    table_refs = re.findall(r"`([^`]+)`", normalized)

    if not table_refs:
        return False

    return all(table_ref in ALLOWED_TABLES.values() for table_ref in table_refs)
