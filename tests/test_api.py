"""
Unit tests for the FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.procurement_analysis.api import app

client = TestClient(app)


class TestAPI:
    """Test cases for API endpoints."""
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_analyze_tender_success(self):
        """Test successful tender analysis."""
        request_data = {
            "tender_text": "Minimum 10 years uninterrupted trading history required."
        }
        response = client.post("/analyze_tender", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "barrier_score" in data
        assert "flagged_phrases" in data
        assert "recommendation" in data
        assert isinstance(data["barrier_score"], int)
        assert 0 <= data["barrier_score"] <= 100
        assert isinstance(data["flagged_phrases"], list)
        assert isinstance(data["recommendation"], str)
    
    def test_analyze_tender_empty_text(self):
        """Test tender analysis with empty text."""
        request_data = {"tender_text": ""}
        response = client.post("/analyze_tender", json=request_data)
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
    
    def test_analyze_tender_whitespace_only(self):
        """Test tender analysis with whitespace-only text."""
        request_data = {"tender_text": "   "}
        response = client.post("/analyze_tender", json=request_data)
        assert response.status_code == 400
    
    def test_analyze_tender_no_barriers(self):
        """Test tender analysis with SME-friendly text."""
        request_data = {
            "tender_text": "We welcome applications from SMEs and new businesses."
        }
        response = client.post("/analyze_tender", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["barrier_score"] == 0
        assert len(data["flagged_phrases"]) == 0
    
    def test_analyze_batch_success(self):
        """Test successful batch analysis."""
        request_data = {
            "tenders": [
                {"tender_text": "Minimum 10 years trading history."},
                {"tender_text": "We welcome SMEs."}
            ]
        }
        response = client.post("/analyze_batch", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
        assert all(r["status"] == "success" for r in data["results"])
    
    def test_analyze_batch_empty_list(self):
        """Test batch analysis with empty list."""
        request_data = {"tenders": []}
        response = client.post("/analyze_batch", json=request_data)
        assert response.status_code == 400
    
    def test_analyze_batch_mixed_results(self):
        """Test batch analysis with mixed valid and invalid inputs."""
        request_data = {
            "tenders": [
                {"tender_text": "Minimum 10 years trading history."},
                {"tender_text": ""}  # Invalid - will be skipped
            ]
        }
        response = client.post("/analyze_batch", json=request_data)
        assert response.status_code == 200
        data = response.json()
        # Only successful analyses are returned (failed ones are skipped)
        assert len(data["results"]) >= 1
        assert data["results"][0]["status"] == "success"

