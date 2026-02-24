from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ProvisionRequestIn(BaseModel):
    service: str
    environment: str = "dev"
    replicas: int = 1
    risk_profile: str = "medium"
    resources: Dict[str, str] = Field(default_factory=dict)
    changes: Dict[str, Any] = Field(default_factory=dict)

class RemediateIn(BaseModel):
    request_id: str
    mode: str = "auto"  # auto|approve
    max_risk: float = 0.6
    actor: str = "system"
