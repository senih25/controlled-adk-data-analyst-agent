PROJECT_ID = "trustable-ai-100mph"

ALLOWED_DATASETS = {
    "cms_medicare": "bigquery-public-data.cms_medicare",
}

ALLOWED_TABLES = {
    "cms_medicare.inpatient_charges_2015": "bigquery-public-data.cms_medicare.inpatient_charges_2015",
    "cms_medicare.hospital_general_info": "bigquery-public-data.cms_medicare.hospital_general_info",
    "cms_medicare.outpatient_charges_2015": "bigquery-public-data.cms_medicare.outpatient_charges_2015",
}

DEFAULT_QUERY_LIMIT = 100
MAX_QUERY_LIMIT = 1000

MAX_BYTES_PROCESSED = 100_000_000

AUDIT_LOG_PATH = "logs/bigquery_audit.log"
