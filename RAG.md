# RAG-Based Barrier Detection Setup Guide

This guide explains how to use the new RAG (Retrieval-Augmented Generation) based barrier detection system.

## Overview

The RAG system replaces the regex-based approach with:
1. **Embeddings**: Uses sentence transformers to create vector embeddings of tender documents
2. **Retrieval**: Finds similar tender documents from the knowledge base
3. **Generation**: Uses LLM to analyze barriers based on retrieved context

## Installation

### Step 1: Install RAG Dependencies

```bash
# Install sentence-transformers (required for embeddings)
pip install sentence-transformers

# Or using uv
uv pip install sentence-transformers
```

### Step 2: Optional - Install OpenAI (for LLM)

If you want to use OpenAI's API for better analysis:

```bash
pip install openai

# Or using uv
uv pip install openai
```

## Configuration

### Environment Variables

The system can be configured using environment variables:

```bash
# Enable RAG (default: true)
export USE_RAG=true

# Use OpenAI API (default: false - uses fallback)
export USE_OPENAI=false

# OpenAI API Key (required if USE_OPENAI=true)
export OPENAI_API_KEY=your-api-key-here

# OpenAI Model (default: gpt-4o-mini)
export OPENAI_MODEL=gpt-4o-mini
```

### Windows PowerShell

```powershell
$env:USE_RAG="true"
$env:USE_OPENAI="false"
# If using OpenAI:
$env:OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Option 1: RAG with Local Fallback (Default)

By default, the system uses RAG with embeddings but falls back to regex-based analysis for the LLM step (since no local LLM is configured by default).

```bash
# Set environment variable
export USE_RAG=true
export USE_OPENAI=false

# Start the server
uvicorn src.procurement_analysis.api:app --reload
```

**How it works:**
- Uses embeddings to find similar tender documents
- Uses regex-based detector as fallback for analysis
- No API costs, works offline

### Option 2: RAG with OpenAI (Recommended for Best Results)

For the best analysis quality, use OpenAI API:

```bash
# Set environment variables
export USE_RAG=true
export USE_OPENAI=true
export OPENAI_API_KEY=your-api-key-here

# Start the server
uvicorn src.procurement_analysis.api:app --reload
```

**How it works:**
- Uses embeddings to find similar tender documents
- Sends context + query to OpenAI for analysis
- Returns structured JSON with barrier analysis

### Option 3: Regex-Based (Original)

To use the original regex-based approach:

```bash
# Disable RAG
export USE_RAG=false

# Start the server
uvicorn src.procurement_analysis.api:app --reload
```

## API Usage

The API endpoints remain the same. The system automatically uses RAG if enabled:

```bash
curl -X POST "http://localhost:8000/analyze_tender" \
  -H "Content-Type: application/json" \
  -d '{
    "tender_text": "Minimum 10 years uninterrupted trading history required."
  }'
```

## Knowledge Base

The RAG system uses `data/sample_tender_documents.json` as the knowledge base. You can:

1. **Add more tender documents** to improve retrieval
2. **Update existing documents** with better examples
3. **Use your own knowledge base** by modifying the `knowledge_base_path` parameter

### Knowledge Base Format

```json
[
  {
    "id": "TENDER_001",
    "title": "Example Tender",
    "text": "Full tender document text here..."
  }
]
```

## How RAG Works

1. **Embedding Creation**: When initialized, the system creates embeddings for all tender documents in the knowledge base using sentence transformers.

2. **Query Processing**: When you submit a tender text:
   - The system creates an embedding for your query
   - Finds top-k (default: 5) most similar tender documents using cosine similarity

3. **Context Building**: Similar documents are included as context in the LLM prompt

4. **Analysis**: The LLM analyzes the tender text with context and generates:
   - Flagged phrases
   - Categories
   - Scores
   - Recommendations

## Advantages of RAG

✅ **Context-Aware**: Uses similar tender examples for better understanding  
✅ **Flexible**: Can handle variations in language not covered by regex  
✅ **Learnable**: Improves as you add more examples to knowledge base  
✅ **Interpretable**: Shows which similar documents influenced the analysis  

## Performance Considerations

- **First Request**: Slower (embeddings are created on initialization)
- **Subsequent Requests**: Fast (embeddings cached)
- **OpenAI API**: Adds ~1-3 seconds per request (depends on model)
- **Local Fallback**: Similar speed to regex-based approach

## Troubleshooting

### "sentence-transformers not installed"

```bash
pip install sentence-transformers
```

### "OpenAI API error"

- Check your API key is set correctly
- Verify you have API credits
- Check network connectivity

### "Knowledge base file not found"

- Ensure `data/sample_tender_documents.json` exists
- Or specify custom path when initializing detector

### Slow Performance

- First initialization loads the embedding model (takes ~10-30 seconds)
- Subsequent requests are fast
- Consider using a smaller embedding model for faster startup

## Customization

### Using Different Embedding Model

Edit `src/procurement_analysis/rag_barrier_detector.py`:

```python
detector = RAGBarrierDetector(
    embedding_model="all-mpnet-base-v2"  # Larger, more accurate
)
```

Popular models:
- `all-MiniLM-L6-v2` (default, fast, 80MB)
- `all-mpnet-base-v2` (slower, more accurate, 420MB)
- `paraphrase-MiniLM-L6-v2` (good for similarity)

### Using Local LLM

To use a local LLM instead of OpenAI, modify `_call_llm()` method to use:
- Ollama
- LlamaCpp
- HuggingFace Transformers

## Example: Python Usage

```python
from src.procurement_analysis.rag_barrier_detector import RAGBarrierDetector

# Initialize with OpenAI
detector = RAGBarrierDetector(
    use_openai=True,
    openai_api_key="your-key",
    openai_model="gpt-4o-mini"
)

# Or without OpenAI (uses fallback)
detector = RAGBarrierDetector(use_openai=False)

# Analyze
flagged_phrases, score = detector.detect_barriers(
    "Minimum 10 years trading history required."
)

print(f"Barrier Score: {score}")
for fp in flagged_phrases:
    print(f"- {fp.phrase} ({fp.category}): {fp.score} points")
```

## Migration from Regex

The API interface remains the same, so no code changes needed! Just:

1. Install dependencies: `pip install sentence-transformers`
2. Set `USE_RAG=true` (default)
3. Restart your server

The system will automatically use RAG for all requests.

