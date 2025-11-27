# Procurement Accessibility Analysis MVP

An AI platform to help public bodies identify language in tender documents that creates barriers for Small and Medium-sized Enterprises (SMEs).

## Overview

This MVP implements a rule-based NLP system that analyzes tender documents and identifies phrases that may exclude SMEs from participating in public procurement opportunities. The system calculates a barrier score (0-100) and provides recommendations for improving tender accessibility.

## Project Structure

```
Procurement-Accessibility-Analysis/
├── src/
│   └── procurement_analysis/
│       ├── __init__.py
│       ├── barrier_detector.py    # Core NLP barrier detection logic
│       ├── api.py                 # FastAPI application
│       └── main.py                # Application entry point
├── tests/
│   ├── __init__.py
│   ├── test_barrier_detector.py   # Unit tests for barrier detection
│   └── test_api.py                # Unit tests for API endpoints
├── data/
│   └── sample_tender_documents.json  # Sample tender documents
├── pyproject.toml                  # Project configuration (uv)
├── test_api.py                     # Test script for API
└── README.md                       # This file
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Install uv** (if not already installed):
   ```bash
   # On Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone or navigate to the project directory**:
   ```bash
   cd Procurement-Accessibility-Analysis
   ```

3. **Create a virtual environment and install dependencies**:
   ```bash
   uv venv
   uv pip install -e .
   ```

   Or if you prefer to use uv's project management:
   ```bash
   uv sync
   ```

4. **Activate the virtual environment**:
   ```bash
   # On Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

### Running the Application

#### Step 1: Start the FastAPI Server

**Option A: Using uvicorn directly (Recommended)**
```bash
uvicorn src.procurement_analysis.api:app --reload
```

**Option B: Using main.py**
```bash
python -m src.procurement_analysis.main
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### Step 2: Verify Server is Running

Open your browser and visit:
- **API Root**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

#### Step 3: Test the API

**Method 1: Using the Test Script (Easiest)**

Open a **new terminal** (keep the server running in the first terminal):
```bash
# Make sure you're in the project directory and virtual environment is activated
python test_api.py
```

**Method 2: Using curl (Command Line)**

**Windows PowerShell:**
```powershell
curl -X POST "http://localhost:8000/analyze_tender" `
  -H "Content-Type: application/json" `
  -d '{\"tender_text\": \"Minimum 10 years uninterrupted trading history required.\"}'
```

**Windows Command Prompt:**
```cmd
curl -X POST "http://localhost:8000/analyze_tender" ^
  -H "Content-Type: application/json" ^
  -d "{\"tender_text\": \"Minimum 10 years uninterrupted trading history required.\"}"
```

**macOS/Linux:**
```bash
curl -X POST "http://localhost:8000/analyze_tender" \
  -H "Content-Type: application/json" \
  -d '{"tender_text": "Minimum 10 years uninterrupted trading history required."}'
```

**Method 3: Using Python Requests**

Create a test file `test_manual.py`:
```python
import requests

BASE_URL = "http://localhost:8000"

# Test health check
response = requests.get(f"{BASE_URL}/health")
print("Health Check:", response.json())

# Test single analysis
response = requests.post(
    f"{BASE_URL}/analyze_tender",
    json={
        "tender_text": "Minimum 10 years uninterrupted trading history. Professional Indemnity Insurance of £25 million required."
    }
)
print("\nAnalysis Result:")
print(response.json())
```

Run it:
```bash
python test_manual.py
```

**Method 4: Using the Interactive API Docs (Swagger UI)**

1. Open browser: http://localhost:8000/docs
2. Click on `POST /analyze_tender`
3. Click "Try it out"
4. Enter JSON in the request body:
   ```json
   {
     "tender_text": "Minimum 10 years uninterrupted trading history required."
   }
   ```
5. Click "Execute"
6. See the response below

**Method 5: Using pytest (Unit Tests)**

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_barrier_detector.py
pytest tests/test_api.py

# Run with coverage
pytest --cov=src/procurement_analysis
```

#### Troubleshooting

**Port Already in Use:**
```bash
uvicorn src.procurement_analysis.api:app --reload --port 8001
```

**Module Not Found Errors:**
1. Make sure virtual environment is activated
2. Reinstall dependencies: `uv pip install -e .` or `pip install -e .`
3. You're in the project root directory

**Import Errors:**
```bash
# Reinstall in development mode
uv pip install -e . --force-reinstall
```

**Connection Refused:**
- Make sure the server is running
- Check the URL (should be http://localhost:8000)
- Verify no firewall is blocking the connection

#### Example Test Cases

**Low Barrier (SME-friendly):**
```json
{
  "tender_text": "We welcome applications from SMEs and new businesses. Flexible timescales available."
}
```
**Expected Score**: 0-25

**Medium Barrier:**
```json
{
  "tender_text": "Minimum 5 years trading history required. Public Liability Insurance of £5 million."
}
```
**Expected Score**: 18-20 (5 years = 10 points, £5M insurance = 5-8 points)

**High Barrier (Reference Guide Example):**
```json
{
  "tender_text": "The supplier must demonstrate a minimum of 10 years uninterrupted trading history in the public sector. Required insurances include Professional Indemnity Insurance of £25 million and Public Liability Insurance of £15 million."
}
```
**Expected Score**: 42 (10 years = 15 points, £25M PI = 15 points, £15M PL = 12 points)

**Very High Barrier:**
```json
{
  "tender_text": "Minimum 15 years uninterrupted trading history. Professional Indemnity Insurance of £50 million. Minimum turnover of £100 million required. ISO 9001, ISO 27001, ISO 20000 certifications mandatory."
}
```
**Expected Score**: 60-75 (15 years = 15, £50M insurance = 15, £100M turnover = 15, 3+ certifications = 12)

#### Stopping the Server

Press `CTRL+C` in the terminal where the server is running.

## API Usage

### Single Tender Analysis

**Endpoint**: `POST /analyze_tender`

**Request**:
```bash
curl -X POST "http://localhost:8000/analyze_tender" \
  -H "Content-Type: application/json" \
  -d '{
    "tender_text": "The supplier must demonstrate a minimum of 10 years uninterrupted trading history. Required insurances include Professional Indemnity Insurance of £25 million."
  }'
```

**Response**:
```json
{
  "barrier_score": 42,
  "flagged_phrases": [
    "10 years uninterrupted trading history",
    "Professional Indemnity Insurance of £25 million"
  ],
  "flagged_phrases_detailed": [
    {
      "phrase": "10 years uninterrupted trading history",
      "category": "Trading History",
      "score": 15
    },
    {
      "phrase": "Professional Indemnity Insurance of £25 million",
      "category": "Insurance",
      "score": 15
    }
  ],
  "recommendation": "Medium barrier risk - consider reviewing requirements"
}
```

### Batch Analysis

**Endpoint**: `POST /analyze_batch`

**Request**:
```bash
curl -X POST "http://localhost:8000/analyze_batch" \
  -H "Content-Type: application/json" \
  -d '{
    "tenders": [
      {"tender_text": "Minimum 10 years trading history required."},
      {"tender_text": "We welcome applications from SMEs."}
    ]
  }'
```

**Response**:
```json
{
  "results": [
    {
      "status": "success",
      "analysis": {
        "barrier_score": 15,
        "flagged_phrases": ["Minimum 10 years trading history required."],
        "flagged_phrases_detailed": [
          {
            "phrase": "Minimum 10 years trading history required.",
            "category": "Trading History",
            "score": 15
          }
        ],
        "recommendation": "Medium barrier risk - consider reviewing requirements"
      }
    },
    {
      "status": "success",
      "analysis": {
        "barrier_score": 0,
        "flagged_phrases": [],
        "flagged_phrases_detailed": [],
        "recommendation": "Low barrier risk - tender appears SME-friendly"
      }
    }
  ]
}
```

**Note**: Failed tenders are silently skipped and not included in the response. Only successful analyses are returned.

### Health Check

**Endpoint**: `GET /health`

```bash
curl http://localhost:8000/health
```

## Approach and Methodology

### Barrier Detection System

The system uses a **rule-based approach** with regex pattern matching to identify barrier phrases. This approach was chosen for the MVP because:

1. **Interpretability**: Rules are transparent and explainable
2. **No training data required**: Can be deployed immediately
3. **Fast execution**: Pattern matching is computationally efficient
4. **Domain-specific**: Can be tailored to procurement-specific language
5. **No external dependencies**: Pure Python regex implementation

### Barrier Categories Detected

The system detects 10 major categories of barriers:

1. **Excessive Trading History Requirements** (e.g., "10+ years trading history")
2. **Disproportionate Insurance Requirements** (e.g., "£25M Professional Indemnity")
3. **Excessive Financial Thresholds** (e.g., "£50M annual turnover")
4. **Unrealistic Time Constraints** (e.g., "6 weeks with zero tolerance")
5. **Excessive Certification Requirements** (e.g., "3+ ISO certifications")
6. **Geographic/Infrastructure Requirements** (e.g., "offices in multiple cities")
7. **Overly Specific Experience Requirements** (e.g., "Fortune 500 clients only")
8. **Excessive Resource Requirements** (e.g., "100+ full-time developers")
9. **Disproportionate Penalty Clauses** (e.g., "£50K/week liquidated damages")
10. **Sole Source/Proprietary Specifications** (e.g., "specific manufacturer only")

### Scoring Logic

The scoring system is based on the Barrier Phrases Reference Guide and assigns points based on barrier severity:

**High Barrier Phrases (10-15 points each):**
- Trading history ≥10 years: **15 points**
- Insurance >£20 million: **15 points**
- Insurance £15-20 million (Public Liability): **12 points**
- Turnover requirements >£50 million: **15 points**
- Multiple certifications (3+): **12 points**
- Zero tolerance completion clauses: **12 points**
- Mobilization within 48 hours: **12 points**
- Performance bond ≥15%: **12 points**
- Liquidated damages ≥£50,000/week: **12 points**

**Medium Barrier Phrases (5-9 points each):**
- Trading history 5-10 years: **10 points**
- Insurance £10-20 million: **12 points** (Professional Indemnity)
- Insurance £10-15 million: **8 points**
- Turnover £10-50 million: **12 points**
- 1-2 certifications: **8 points**
- Tight but potentially realistic timelines: **6-10 points**

**Low Barrier Phrases (1-4 points each):**
- Reasonable insurance requirements (<£10M): **5-8 points**
- Standard qualifications: **3-5 points**
- Flexible timelines: **0-3 points**

**Total Score Interpretation:**
- **0-25**: Low barrier (SME-friendly)
- **26-50**: Medium barrier (some concerns)
- **51-75**: High barrier (significant SME exclusion risk)
- **76-100**: Very high barrier (likely excludes majority of SMEs)

**Example Analysis** (from reference guide):
- "10 years uninterrupted trading history" → **15 points**
- "Professional Indemnity Insurance of £25 million" → **15 points** (>£20M)
- "Public Liability Insurance of £15 million" → **12 points** (≥£15M)
- **Total Score: 42** (Medium-High barrier)

### Pattern Matching Strategy

1. **Case-insensitive matching**: Handles variations in capitalization
2. **Flexible number extraction**: Captures amounts in various formats (£25M, £25 million, 25 million)
3. **Context-aware scoring**: Same phrase type scored differently based on magnitude (e.g., 5 years vs 15 years)
4. **Duplicate detection**: Prevents counting the same phrase multiple times

## Trade-offs and Design Decisions

### Why Rule-Based Over ML?

**Chosen**: Rule-based pattern matching
- **Pros**: 
  - No training data needed
  - Immediate deployment
  - Fully interpretable
  - Easy to maintain and update
- **Cons**:
  - May miss novel barrier phrases
  - Requires manual pattern updates
  - Less robust to language variations

**Alternative**: Supervised ML model
- Would require labeled training data
- Better generalization to unseen phrases
- Less interpretable (black box)
- Requires ongoing retraining

### Why Regex Patterns Only?

**Chosen**: Regex patterns for pattern matching
- **Pros**:
  - No external NLP dependencies required
  - Fast execution
  - Easy to debug and maintain
  - Precise control over matching patterns
  - Simple deployment (no data downloads needed)
- **Cons**:
  - Less robust to grammatical variations than full NLP pipelines
  - Manual pattern maintenance required
  - May miss variations in phrasing

**Note**: The system uses regex patterns exclusively for barrier phrase detection. Text is preprocessed (whitespace normalization) before pattern matching.

### Scoring System Design

- **Additive scoring**: Multiple barriers accumulate
- **Capped at 100**: Prevents extreme scores
- **Category-based**: Different categories weighted by severity
- **Magnitude-aware**: Higher thresholds score more points

## Testing

### Running Tests

**Unit Tests (pytest):**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/procurement_analysis

# Run specific test file
pytest tests/test_barrier_detector.py
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

**Manual API Testing:**
```bash
# Start the API server first, then run:
python test_api.py
```

**Note**: There are two test files:
- `tests/test_api.py` - Unit tests using pytest (no server required)
- `test_api.py` - Manual test script (requires running API server)

### Test Coverage

- Unit tests for barrier detection logic
- API endpoint tests
- Edge case handling (empty text, malformed input)
- Score calculation validation
- Recommendation generation
- Tests aligned with Barrier Phrases Reference Guide scoring

## Future Improvements

### Short-term Enhancements

1. **Enhanced Pattern Matching**:
   - Add more comprehensive regex patterns for edge cases
   - Implement synonym handling (e.g., "turnover" = "revenue" = "income")
   - Add support for more currency formats and abbreviations

2. **Context Awareness**:
   - Consider contract value when evaluating insurance requirements
   - Adjust scoring based on industry/procurement type
   - Detect positive language (e.g., "we welcome SMEs") to reduce scores

3. **Better Text Preprocessing**:
   - Enhanced whitespace normalization
   - Handle abbreviations and acronyms
   - Normalize currency formats
   - Extract structured information (dates, amounts, percentages)

### Supervised ML Approach (If Labeled Data Available)

If we had labeled training data (tender documents with expert-annotated barrier phrases), we could evolve this into a supervised ML model:

1. **Data Collection**:
   - Annotate 500-1000 tender documents
   - Label barrier phrases with categories and severity scores
   - Create train/validation/test splits

2. **Model Architecture Options**:
   - **BERT-based NER**: Fine-tune BERT for named entity recognition of barrier phrases
   - **Sequence Labeling**: Use BiLSTM-CRF or Transformer-based models for token-level classification
   - **Text Classification**: Multi-label classification for barrier categories
   - **Regression**: Predict barrier scores directly

3. **Feature Engineering**:
   - Embed barrier phrases using sentence transformers
   - Extract numerical features (amounts, years, percentages)
   - Include metadata (contract value, industry sector)

4. **Training Pipeline**:
   ```python
   # Pseudo-code for ML approach
   from transformers import AutoTokenizer, AutoModelForTokenClassification
   
   model = AutoModelForTokenClassification.from_pretrained("bert-base-uncased")
   tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
   
   # Fine-tune on labeled barrier phrases
   trainer = Trainer(
       model=model,
       train_dataset=train_dataset,
       eval_dataset=val_dataset
   )
   trainer.train()
   ```

5. **Evaluation Metrics**:
   - **Precision**: Of all flagged phrases, how many are actually barriers?
   - **Recall**: Of all actual barriers, how many did we detect?
   - **F1-Score**: Harmonic mean of precision and recall
   - **Barrier Score Accuracy**: Mean absolute error between predicted and actual scores
   - **Category Classification**: Per-category precision/recall

6. **Hybrid Approach**:
   - Use ML model for detection
   - Use rule-based system for scoring (more interpretable)
   - Combine both for final barrier score

### Model Evaluation Considerations

**Precision vs Recall Trade-off**:

- **High Precision** (fewer false positives):
  - Better for automated flagging (less manual review needed)
  - Reduces "cry wolf" effect
  - **Use case**: Automated tender review system
  
- **High Recall** (fewer false negatives):
  - Catches more barriers (better for compliance)
  - May flag some non-barriers (requires manual review)
  - **Use case**: Comprehensive accessibility audit

**Recommended Approach**:
- Start with **high recall** (detect all potential barriers)
- Use **confidence scores** to prioritize manual review
- Allow users to **tune threshold** based on use case
- Provide **explainability** (show why phrase was flagged)

**Metrics to Track**:
- Precision@K: Precision for top K flagged phrases
- Recall@K: Recall for top K most severe barriers
- Category-wise metrics: Precision/recall per barrier category
- Score calibration: Predicted scores vs expert-annotated scores

## Docker Containerization (Bonus)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY data/ ./data/

# Install dependencies
RUN uv pip install --system -e .

EXPOSE 8000

CMD ["uvicorn", "src.procurement_analysis.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Commands

```bash
# Build image
docker build -t procurement-analysis .

# Run container
docker run -p 8000:8000 procurement-analysis

# Run with volume mount (for development)
docker run -p 8000:8000 -v $(pwd):/app procurement-analysis
```

## Contributing

This is an MVP implementation. Future improvements welcome:
- Additional barrier pattern rules
- Enhanced NLP capabilities
- Performance optimizations
- Extended test coverage

## License

See LICENSE file for details.

## Contact

For questions or feedback, please refer to the project repository.
