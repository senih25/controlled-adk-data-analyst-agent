from datetime import datetime, timezone
from pathlib import Path
import json

from data_analyst_agent.config import AUDIT_LOG_PATH


def write_audit_log(event: dict) -> None:
    path = Path(AUDIT_LOG_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **event,
    }

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
