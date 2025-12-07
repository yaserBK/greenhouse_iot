import json
import sys
from datetime import datetime

def log_event(event_type: str, **kwargs):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        **kwargs
    }
    sys.stdout.write(json.dumps(record) + "\n")
    sys.stdout.flush()

