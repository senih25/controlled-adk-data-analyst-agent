#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://127.0.0.1:8080}"
PRODUCER_EXPORT="../enabiz-local-health-assistant/exports/anonymized/anonymized_enabiz_analytics.json"
LOCAL_EXPORT="exports/anonymized/anonymized_enabiz_analytics.json"

echo "== Health check =="
curl -fsS "${API_URL}/health"
echo
echo

echo "== Direct producer path smoke =="
if curl -fsS -X POST "${API_URL}/connectors/enabiz/summarize" -H "Content-Type: application/json" -d "{\"path\":\"${PRODUCER_EXPORT}\"}"; then
  echo
  echo "PASS: direct producer path accepted"
  exit 0
fi

echo
echo "Direct path failed. Trying copied local path..."
mkdir -p exports/anonymized
cp "../enabiz-local-health-assistant/exports/anonymized/anonymized_enabiz_analytics.json" "${LOCAL_EXPORT}"

curl -fsS -X POST "${API_URL}/connectors/enabiz/summarize" -H "Content-Type: application/json" -d "{\"path\":\"${LOCAL_EXPORT}\"}"
echo
echo "PASS: local copied path accepted"
