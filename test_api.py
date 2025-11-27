"""
Test script for the Procurement Barrier Analysis API.

Usage:
    python test_api.py

Or use curl commands (see README.md)
"""

import json
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def test_single_analysis():
    """Test single tender analysis endpoint."""
    print("\n" + "="*60)
    print("Testing Single Tender Analysis")
    print("="*60)
    
    # Test case 1: High barrier tender
    test_text = (
        "The supplier must demonstrate a minimum of 10 years uninterrupted "
        "trading history in the public sector. Required insurances include "
        "Professional Indemnity Insurance of £25 million and Public Liability "
        "Insurance of £15 million."
    )
    
    response = requests.post(
        f"{BASE_URL}/analyze_tender",
        json={"tender_text": test_text}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nBarrier Score: {result['barrier_score']}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"\nFlagged Phrases ({len(result['flagged_phrases'])}):")
        for i, phrase in enumerate(result['flagged_phrases'], 1):
            print(f"  {i}. {phrase}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def test_batch_analysis():
    """Test batch analysis endpoint."""
    print("\n" + "="*60)
    print("Testing Batch Analysis")
    print("="*60)
    
    # Load sample tenders
    try:
        with open("data/sample_tender_documents.json", "r") as f:
            tenders_data = json.load(f)
        
        # Take first 3 tenders for testing
        tenders = [
            {"tender_text": tender["text"]}
            for tender in tenders_data[:3]
        ]
        
        response = requests.post(
            f"{BASE_URL}/analyze_batch",
            json={"tenders": tenders}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nAnalyzed {len(result['results'])} tenders:")
            for i, res in enumerate(result['results'], 1):
                if res['status'] == 'success':
                    analysis = res['analysis']
                    print(f"\n  Tender {i}:")
                    print(f"    Score: {analysis['barrier_score']}")
                    print(f"    Phrases: {len(analysis['flagged_phrases'])}")
                else:
                    print(f"\n  Tender {i}: ERROR - {res.get('error', 'Unknown error')}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except FileNotFoundError:
        print("Sample tender documents file not found. Skipping batch test.")


def test_health_check():
    """Test health check endpoint."""
    print("\n" + "="*60)
    print("Testing Health Check")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print(f"Status: {response.json()['status']}")
    else:
        print(f"Error: {response.status_code}")


if __name__ == "__main__":
    print("Procurement Barrier Analysis API Test Script")
    print("="*60)
    print("Make sure the API server is running on http://localhost:8000")
    print("Start it with: uvicorn src.procurement_analysis.api:app --reload")
    
    try:
        test_health_check()
        test_single_analysis()
        test_batch_analysis()
        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60)
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to the API server.")
        print("Please make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\nERROR: {str(e)}")

