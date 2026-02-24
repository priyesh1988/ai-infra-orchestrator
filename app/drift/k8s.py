# In production, this would use Kubernetes API (client-python) to compare desired state vs live state.
# Here we keep it as a stub to demonstrate architecture wiring.
from datetime import datetime

def detect() -> list[dict]:
    return [{
        "type": "drift",
        "source": "k8s",
        "message": "Stub drift event: replicas changed 3 -> 7",
        "observed_at": datetime.utcnow().isoformat() + "Z",
        "details": {"service": "payment-api", "from": 3, "to": 7},
    }]
