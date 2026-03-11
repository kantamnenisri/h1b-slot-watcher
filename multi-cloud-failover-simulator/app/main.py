from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import os

from .models import CloudMetrics, ProviderStatus, FailoverEvent, DashboardState
from .scoring import calculate_score

app = FastAPI(title="Multi-Cloud Failover Simulator")

# In-memory state
state = {
    "active_provider": "AWS",
    "providers": {
        "AWS": ProviderStatus(name="AWS", metrics=CloudMetrics(latency=120, error_rate=0.1, cpu=45), score=88.5, is_active=True),
        "GCP": ProviderStatus(name="GCP", metrics=CloudMetrics(latency=150, error_rate=0.2, cpu=30), score=86.3, is_active=False),
        "Azure": ProviderStatus(name="Azure", metrics=CloudMetrics(latency=200, error_rate=0.5, cpu=60), score=80.1, is_active=False),
    },
    "history": []
}

FAILOVER_THRESHOLD = 60.0

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

@app.get("/api/dashboard", response_model=DashboardState)
async def get_dashboard():
    return DashboardState(
        providers=list(state["providers"].values()),
        active_provider=state["active_provider"],
        history=state["history"]
    )

@app.post("/api/update/{provider_name}")
async def update_metrics(provider_name: str, metrics: CloudMetrics):
    if provider_name not in state["providers"]:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Calculate new score
    new_score = calculate_score(metrics)
    
    # Update provider state
    provider = state["providers"][provider_name]
    provider.metrics = metrics
    provider.score = new_score
    
    # Check for failover if active provider drops below threshold
    active_name = state["active_provider"]
    active_provider = state["providers"][active_name]
    
    if active_provider.score < FAILOVER_THRESHOLD:
        # Find best available provider
        best_provider = max(state["providers"].values(), key=lambda p: p.score)
        
        if best_provider.name != active_name:
            # Trigger failover
            event = FailoverEvent(
                timestamp=datetime.now(),
                from_provider=active_name,
                to_provider=best_provider.name,
                reason=f"{active_name} score ({active_provider.score}) fell below threshold ({FAILOVER_THRESHOLD})"
            )
            state["history"].insert(0, event)
            
            # Update active status
            active_provider.is_active = False
            best_provider.is_active = True
            state["active_provider"] = best_provider.name
            
            return {"message": "Failover triggered", "event": event}

    return {"message": "Metrics updated", "current_active": state["active_provider"]}

# Mount static files (must be after defining other routes to avoid shadowing '/')
app.mount("/static", StaticFiles(directory="static"), name="static")
