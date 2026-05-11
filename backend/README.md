# OpsPilot Backend

Python 3.11+ required

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

- `GET /healthz` - Health check
- `POST /incidents/runs` - Create incident run
- `GET /incidents/runs/{run_id}` - Get run status
- `GET /incidents/runs/{run_id}/events` - Get run events
- `GET /incidents/runs/{run_id}/rca` - Get RCA report
- `GET /approvals/pending` - List pending approvals
- `GET /approvals/{approval_id}` - Get approval details
- `POST /approvals/{approval_id}/decision` - Submit approval decision
