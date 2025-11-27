"""
FastAPI Application for Procurement Barrier Analysis
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from .barrier_detector import BarrierDetector


# Request models
class TenderAnalysisRequest(BaseModel):
    """Request model for single tender analysis."""
    tender_text: str = Field(..., description="The tender document text to analyze")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tender_text": "The supplier must demonstrate a minimum of 10 years uninterrupted trading history."
            }
        }


class BatchTenderAnalysisRequest(BaseModel):
    """Request model for batch tender analysis."""
    tenders: List[TenderAnalysisRequest] = Field(..., description="List of tender documents to analyze")


# Response models
class FlaggedPhraseResponse(BaseModel):
    """Response model for a flagged phrase."""
    phrase: str
    category: str
    score: int


class TenderAnalysisResponse(BaseModel):
    """Response model for tender analysis."""
    barrier_score: int = Field(..., description="Barrier score from 0-100")
    flagged_phrases: List[str] = Field(..., description="List of flagged barrier phrases")
    flagged_phrases_detailed: Optional[List[FlaggedPhraseResponse]] = Field(
        None, 
        description="Detailed information about flagged phrases"
    )
    recommendation: str = Field(..., description="Recommendation based on barrier score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "barrier_score": 45,
                "flagged_phrases": ["10 years uninterrupted trading history"],
                "recommendation": "Medium barrier risk - consider reviewing requirements"
            }
        }


class BatchAnalysisResult(BaseModel):
    """Result for a single tender in batch analysis."""
    status: str
    analysis: Optional[TenderAnalysisResponse] = None


class BatchAnalysisResponse(BaseModel):
    """Response model for batch analysis."""
    results: List[BatchAnalysisResult]

# Initialize FastAPI app
app = FastAPI(
    title="Procurement Barrier Analysis API",
    description="API for analyzing barriers in procurement tender documents",
    version="1.0.0"
)

# Initialize barrier detector
detector = BarrierDetector()


# Health check endpoint
@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "message": "Procurement Barrier Analysis API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze_tender": "Analyze a single tender document for barriers",
            "POST /analyze_batch": "Analyze multiple tender documents at once",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Main analysis endpoint
@app.post("/analyze_tender", response_model=TenderAnalysisResponse)
def analyze_tender(request: TenderAnalysisRequest):
    """
    Analyze a tender document for SME barriers.
    
    Args:
        request: TenderAnalysisRequest containing the tender text
        
    Returns:
        TenderAnalysisResponse with barrier score, flagged phrases, and recommendation
        
    Raises:
        HTTPException: If tender_text is empty or invalid
    """
    # Validate input
    if not request.tender_text or len(request.tender_text.strip()) == 0:
        raise HTTPException(
            status_code=400, 
            detail="tender_text cannot be empty"
        )
    
    try:
        # Detect barriers
        flagged_phrases, barrier_score = detector.detect_barriers(request.tender_text)
        
        # Get recommendation
        recommendation = detector.get_recommendation(barrier_score)
        
        # Prepare response
        flagged_phrases_list = [fp.phrase for fp in flagged_phrases]
        flagged_phrases_detailed = [
            FlaggedPhraseResponse(
                phrase=fp.phrase,
                category=fp.category,
                score=fp.score
            )
            for fp in flagged_phrases
        ]
        
        return TenderAnalysisResponse(
            barrier_score=barrier_score,
            flagged_phrases=flagged_phrases_list,
            flagged_phrases_detailed=flagged_phrases_detailed,
            recommendation=recommendation
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing tender: {str(e)}"
        )


# Batch analysis endpoint
@app.post("/analyze_batch", response_model=BatchAnalysisResponse)
def analyze_batch(request: BatchTenderAnalysisRequest):
    """
    Analyze multiple tender documents at once.
    
    Args:
        request: BatchTenderAnalysisRequest containing list of tender documents
        
    Returns:
        BatchAnalysisResponse with results for each tender
    """
    if not request.tenders:
        raise HTTPException(
            status_code=400,
            detail="tenders list cannot be empty"
        )
    
    results = []
    for tender in request.tenders:
        try:
            result = analyze_tender(tender)
            results.append(BatchAnalysisResult(
                status="success",
                analysis=result
            ))
        except Exception:
            # Skip failed tenders silently - only include successful analyses
            continue
    
    return BatchAnalysisResponse(results=results)

