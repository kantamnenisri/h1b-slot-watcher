from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CloudMetrics(BaseModel):
    latency: float = Field(..., ge=0, le=1000, description="Latency in milliseconds")
    error_rate: float = Field(..., ge=0, le=100, description="Error rate in percentage")
    cpu: float = Field(..., ge=0, le=100, description="CPU usage in percentage")

class ProviderStatus(BaseModel):
    name: str
    metrics: CloudMetrics
    score: float
    is_active: bool

class FailoverEvent(BaseModel):
    timestamp: datetime
    from_provider: str
    to_provider: str
    reason: str

class DashboardState(BaseModel):
    providers: List[ProviderStatus]
    active_provider: str
    history: List[FailoverEvent]
