from .models import CloudMetrics

def calculate_score(metrics: CloudMetrics) -> float:
    """
    Calculates a reliability score from 0-100.
    Formula: 
    - 40% Weight: Error Rate (Inverted)
    - 30% Weight: Latency (Normalized to 1000ms, Inverted)
    - 30% Weight: CPU Utilization (Inverted)
    """
    # Normalize error rate: 0% is 1.0, 100% is 0.0
    error_score = (100.0 - metrics.error_rate) / 100.0
    
    # Normalize latency: 0ms is 1.0, 1000ms+ is 0.0
    latency_score = max(0.0, (1000.0 - metrics.latency) / 1000.0)
    
    # Normalize CPU: 0% is 1.0, 100% is 0.0
    cpu_score = (100.0 - metrics.cpu) / 100.0
    
    final_score = (error_score * 40.0) + (latency_score * 30.0) + (cpu_score * 30.0)
    return round(final_score, 2)
