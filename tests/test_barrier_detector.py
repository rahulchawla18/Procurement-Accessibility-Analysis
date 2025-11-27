"""
Unit tests for the BarrierDetector class.
"""

import pytest
from src.procurement_analysis.barrier_detector import BarrierDetector, FlaggedPhrase


class TestBarrierDetector:
    """Test cases for BarrierDetector."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = BarrierDetector()
    
    def test_empty_text(self):
        """Test that empty text returns no barriers."""
        phrases, score = self.detector.detect_barriers("")
        assert phrases == []
        assert score == 0
        
        phrases, score = self.detector.detect_barriers("   ")
        assert phrases == []
        assert score == 0
    
    def test_no_barriers(self):
        """Test text with no barrier phrases."""
        text = "We welcome applications from SMEs and new businesses."
        phrases, score = self.detector.detect_barriers(text)
        assert score == 0
        assert len(phrases) == 0
    
    def test_trading_history_barrier(self):
        """Test detection of trading history barriers."""
        text = "Minimum 10 years uninterrupted trading history required."
        phrases, score = self.detector.detect_barriers(text)
        assert len(phrases) > 0
        assert score >= 15  # 10 years should score 15 points
        assert any("trading history" in fp.phrase.lower() for fp in phrases)
        # Check that 10 years gets high barrier score
        trading_phrases = [fp for fp in phrases if "trading" in fp.phrase.lower()]
        assert any(fp.score == 15 for fp in trading_phrases)
    
    def test_insurance_barrier(self):
        """Test detection of insurance barriers."""
        text = "Professional Indemnity Insurance of £25 million required."
        phrases, score = self.detector.detect_barriers(text)
        assert len(phrases) > 0
        assert score >= 15  # £25M should score 15 points (>£20M)
        assert any("insurance" in fp.phrase.lower() for fp in phrases)
        # Check that £25M gets high barrier score
        insurance_phrases = [fp for fp in phrases if "insurance" in fp.phrase.lower()]
        assert any(fp.score == 15 for fp in insurance_phrases)
    
    def test_financial_threshold_barrier(self):
        """Test detection of financial threshold barriers."""
        text = "Minimum annual turnover of £50 million required."
        phrases, score = self.detector.detect_barriers(text)
        assert len(phrases) > 0
        assert score > 0
        assert any("turnover" in fp.phrase.lower() for fp in phrases)
    
    def test_multiple_barriers(self):
        """Test detection of multiple barrier types."""
        text = (
            "Minimum 10 years uninterrupted trading history. "
            "Professional Indemnity Insurance of £25 million. "
            "Minimum turnover of £50 million."
        )
        phrases, score = self.detector.detect_barriers(text)
        assert len(phrases) >= 3
        # Should be at least 15 (trading) + 15 (insurance) + 15 (turnover) = 45
        assert score >= 45
    
    def test_score_capping(self):
        """Test that barrier score is capped at 100."""
        # Create text with many barriers
        text = (
            "Minimum 20 years trading history. "
            "Professional Indemnity Insurance of £50 million. "
            "Public Liability Insurance of £30 million. "
            "Minimum turnover of £100 million. "
            "Must employ at least 100 full-time developers. "
            "ISO 9001, ISO 27001, ISO 20000 certifications required."
        )
        phrases, score = self.detector.detect_barriers(text)
        assert score <= 100
    
    def test_recommendation_low(self):
        """Test recommendation for low barrier score."""
        recommendation = self.detector.get_recommendation(20)
        assert "Low barrier" in recommendation or "SME-friendly" in recommendation
    
    def test_recommendation_medium(self):
        """Test recommendation for medium barrier score."""
        recommendation = self.detector.get_recommendation(35)
        assert "Medium barrier" in recommendation
    
    def test_recommendation_high(self):
        """Test recommendation for high barrier score."""
        recommendation = self.detector.get_recommendation(60)
        assert "High barrier" in recommendation
    
    def test_recommendation_very_high(self):
        """Test recommendation for very high barrier score."""
        recommendation = self.detector.get_recommendation(80)
        assert "Very high barrier" in recommendation
    
    def test_flagged_phrase_structure(self):
        """Test that flagged phrases have correct structure."""
        text = "Minimum 10 years uninterrupted trading history required."
        phrases, score = self.detector.detect_barriers(text)
        
        if phrases:
            fp = phrases[0]
            assert hasattr(fp, 'phrase')
            assert hasattr(fp, 'category')
            assert hasattr(fp, 'score')
            assert isinstance(fp.phrase, str)
            assert isinstance(fp.category, str)
            assert isinstance(fp.score, int)
            assert fp.score > 0
    
    def test_time_constraints(self):
        """Test detection of time constraint barriers."""
        text = "All work must be completed within 6 weeks with zero tolerance."
        phrases, score = self.detector.detect_barriers(text)
        assert len(phrases) > 0
        assert score >= 12  # Zero tolerance should score 12 points
        assert any("zero tolerance" in fp.phrase.lower() or "completed within" in fp.phrase.lower() 
                  for fp in phrases)
    
    def test_certification_requirements(self):
        """Test detection of excessive certification requirements."""
        text = "ISO 9001, ISO 27001, ISO 20000 certifications mandatory."
        phrases, score = self.detector.detect_barriers(text)
        assert len(phrases) > 0
        assert score >= 12  # 3+ certifications should score 12 points
        assert any("iso" in fp.phrase.lower() for fp in phrases)
    
    def test_penalty_clauses(self):
        """Test detection of penalty clauses."""
        text = "Liquidated damages: £50,000 per week for delays."
        phrases, score = self.detector.detect_barriers(text)
        assert len(phrases) > 0
        assert score >= 12  # £50K/week should score 12 points
        assert any("liquidated" in fp.phrase.lower() or "damages" in fp.phrase.lower() 
                  for fp in phrases)

