# Multi-Cloud Failover Simulator

A real-time simulator that monitors health metrics for AWS, GCP, and Azure. It uses a weighted reliability formula to score each provider and automatically fails over to the healthiest provider when the active one drops below a threshold.

## Features
- **FastAPI Backend**: Real-time state management and scoring engine.
- **Reliability Scoring**: Weighted formula considering Latency, Error Rate, and CPU.
- **Auto-Failover**: Instant transition to the highest-scoring provider when health is compromised.
- **Tailwind CSS Dashboard**: Modern, responsive UI for monitoring and simulation.
- **Docker Ready**: Includes a Dockerfile for containerized deployment.
- **Render Support**: Includes `render.yaml` for one-click deployment.

## Scoring Formula
Health Score (0-100) = `(1.0 - error_rate/100) * 40 + (1.0 - latency/1000) * 30 + (1.0 - cpu/100) * 30`

- **Failover Threshold**: 60.0

## Setup

### Local Execution
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Open `http://localhost:8000` in your browser.

### Docker
1. Build the image:
   ```bash
   docker build -t failover-simulator .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 failover-simulator
   ```

## Simulation
Use the dashboard to manually update metrics for any provider. To trigger a failover, set high latency (e.g., 800ms) or high error rate (e.g., 20%) for the currently active provider.
