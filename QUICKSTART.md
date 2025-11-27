# Quick Start Guide

## Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation (5 minutes)

1. **Install uv** (if needed):
   ```powershell
   # Windows PowerShell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Set up the project**:
   ```bash
   # Create virtual environment
   uv venv
   
   # Activate virtual environment
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # macOS/Linux:
   source .venv/bin/activate
   
   # Install dependencies
   uv pip install -e .
   ```

## Running the API (2 minutes)

1. **Start the server**:
   ```bash
   uvicorn src.procurement_analysis.api:app --reload
   ```

2. **Verify it's running**:
   - Open browser: http://localhost:8000/docs
   - Or check health: http://localhost:8000/health

## Testing (1 minute)

### Option 1: Use the test script
```bash
python test_api.py
```

### Option 2: Use curl
```bash
curl -X POST "http://localhost:8000/analyze_tender" ^
  -H "Content-Type: application/json" ^
  -d "{\"tender_text\": \"Minimum 10 years trading history required.\"}"
```

### Option 3: Use Python
```python
import requests

response = requests.post(
    "http://localhost:8000/analyze_tender",
    json={"tender_text": "Minimum 10 years trading history required."}
)
print(response.json())
```

## Running Tests

```bash
pytest
```

## Example Output

```json
{
  "barrier_score": 15,
  "flagged_phrases": ["10 years uninterrupted trading history"],
  "recommendation": "Medium barrier risk - consider reviewing requirements"
}
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API documentation at http://localhost:8000/docs
- Review the barrier detection logic in `src/procurement_analysis/barrier_detector.py`

