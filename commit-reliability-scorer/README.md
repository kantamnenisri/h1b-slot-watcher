# Commit Reliability Scorer

An AI-powered tool to evaluate the risk and reliability of GitHub commits using Python FastAPI and Gemini AI.

## Features
- **AI Analysis**: Uses Gemini 1.5 Flash to evaluate commit diffs for potential risks.
- **Reliability Scoring**: Generates a score from 0 to 100 for every change.
- **Impact Analysis**: Automatically identifies impacted components and recommends specific checks.
- **CI/CD Integrated**: Includes a GitHub Action to block PRs with `CRITICAL` risk levels.
- **Modern UI**: Clean dashboard built with Tailwind CSS.

## Setup

### Environment Variables
Create a `.env` file with:
```env
GEMINI_API_KEY=your_gemini_key
GITHUB_TOKEN=your_github_personal_access_token (Optional, for higher rate limits)
```

### Local Development
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker
```bash
docker build -t commit-scorer .
docker run -p 8000:8000 --env-file .env commit-scorer
```

## CI/CD Integration
To use the reliability check in your repository:
1. Copy `.github/workflows/reliability-check.yml` to your repo.
2. Deploy this app (e.g., to Render).
3. Add a GitHub secret named `SCORER_API_URL` with your deployed URL.


## 💡 Inspiration
This project is a reference implementation exploring concepts related to 
multi-cloud reliability engineering. The author holds USPTO patent 
applications in this domain (US 19/325,718 and US 19/344,864).

## Health Check
- Added /ping endpoint for automated health monitoring.
