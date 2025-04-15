# AWS Alert Notifier

A real-time notification dashboard designed to receive and display AWS health and service alerts. It provides a centralized view of incidents with severity-based highlighting and a built-in simulation engine.

## Features
- **Real-time Alert Feed**: Reverse chronological display of service alerts.
- **Severity Highlighting**: Instant visual cues for INFO, WARNING, and CRITICAL incidents.
- **Alert Ingestion API**: Simple REST API to receive JSON-based alerts from any source.
- **Simulation Dashboard**: Built-in UI to trigger test alerts and verify notifications.
- **Zero Dependencies**: Core logic uses only the Python standard library for maximum compatibility.

## Setup

### Local Execution (No Install Required)
1. Run the server:
   ```bash
   python app/main.py
   ```
2. Open `http://localhost:8000` in your browser.

### Docker
1. Build the image:
   ```bash
   docker build -t aws-alert-notifier .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 aws-alert-notifier
   ```

## API Usage
You can post alerts manually via `curl`:
```bash
curl -X POST http://localhost:8000/api/alerts \
     -H "Content-Type: application/json" \
     -d '{"service": "EC2", "region": "us-east-1", "severity": "CRITICAL", "message": "High API latency"}'
```

## 💡 Inspiration
This project is a reference implementation exploring concepts related to 
multi-cloud reliability engineering. The author holds USPTO patent 
applications in this domain (US 19/325,718 and US 19/344,864).

## Health Check
- Added /ping endpoint for automated health monitoring.
