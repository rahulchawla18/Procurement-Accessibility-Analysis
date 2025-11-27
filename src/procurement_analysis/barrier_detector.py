"""
NLP Barrier Detection System for Tender Documents

This module implements a rule-based system using regex patterns to detect phrases in tender
documents that create barriers for Small and Medium-sized Enterprises (SMEs).
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class FlaggedPhrase:
    """Represents a flagged barrier phrase with its details."""
    phrase: str
    category: str
    score: int


class BarrierDetector:
    """
    Rule-based NLP system for detecting barrier phrases in tender documents.
    
    Uses regex patterns for matching to identify phrases that create barriers for SMEs, 
    such as excessive trading history requirements, disproportionate insurance requirements, etc.
    """
    
    def __init__(self):
        """Initialize the barrier detector with pattern rules."""
        self.patterns = self._build_patterns()
    
    def _build_patterns(self) -> List[Dict]:
        """
        Build pattern rules for barrier detection using regex patterns.
        
        Returns:
            List of pattern dictionaries with regex patterns, category, and scoring logic
        """
        patterns = []
        
        # 1. Excessive Trading History Requirements
        # High barrier: >10 years (15 points), Medium: 5-10 years (10 points)
        patterns.extend([
            {
                "pattern": r"minimum\s+(?:of\s+)?(\d+)\s+years?\s+uninterrupted\s+trading\s+history",
                "category": "Trading History",
                "score_func": lambda m: 15 if int(m.group(1)) >= 10 else (10 if int(m.group(1)) >= 5 else 5),
            },
            {
                "pattern": r"(\d+)\+?\s+years?\s+uninterrupted\s+trading",
                "category": "Trading History",
                "score_func": lambda m: 15 if int(m.group(1)) >= 10 else (10 if int(m.group(1)) >= 5 else 5),
            },
            {
                "pattern": r"minimum\s+(?:of\s+)?(\d+)\s+years?\s+continuous\s+operation",
                "category": "Trading History",
                "score_func": lambda m: 15 if int(m.group(1)) >= 10 else (10 if int(m.group(1)) >= 5 else 5),
            },
            {
                "pattern": r"must\s+demonstrate\s+continuous\s+operation\s+since",
                "category": "Trading History",
                "score": 12,
            },
            {
                "pattern": r"evidence\s+of\s+trading\s+for\s+minimum\s+(\d+)\s+years?\s+required",
                "category": "Trading History",
                "score_func": lambda m: 15 if int(m.group(1)) >= 10 else (10 if int(m.group(1)) >= 5 else 5),
            },
            {
                "pattern": r"established\s+business\s+with\s+(\d+)\+?\s+years?\s+track\s+record",
                "category": "Trading History",
                "score_func": lambda m: 15 if int(m.group(1)) >= 10 else (10 if int(m.group(1)) >= 5 else 5),
            },
        ])
        
        # 2. Disproportionate Insurance Requirements
        # High barrier: >£20M (15 points), Medium: £10-20M (12 points), Low: <£10M (8 points)
        # Public Liability >£15M is high barrier (12 points)
        patterns.extend([
            {
                "pattern": r"professional\s+indemnity\s+insurance\s+(?:of\s+)?£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)",
                "category": "Insurance",
                "score_func": lambda m: 15 if float(m.group(1)) > 20 else (12 if float(m.group(1)) >= 10 else 8),
            },
            {
                "pattern": r"public\s+liability\s+insurance\s+(?:of|exceeding)?\s*£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)",
                "category": "Insurance",
                "score_func": lambda m: 15 if float(m.group(1)) > 20 else (12 if float(m.group(1)) >= 15 else (8 if float(m.group(1)) >= 10 else 5)),
            },
            {
                "pattern": r"liability\s+insurance\s+(?:of|exceeding)?\s*£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)",
                "category": "Insurance",
                "score_func": lambda m: 15 if float(m.group(1)) > 20 else (12 if float(m.group(1)) >= 10 else 8),
            },
            {
                "pattern": r"£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)\s+liability\s+insurance",
                "category": "Insurance",
                "score_func": lambda m: 15 if float(m.group(1)) > 20 else (12 if float(m.group(1)) >= 10 else 8),
            },
            {
                "pattern": r"multiple\s+insurance\s+policies?\s+each\s+exceeding\s+£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)",
                "category": "Insurance",
                "score_func": lambda m: 15 if float(m.group(1)) >= 10 else 12,
            },
            {
                "pattern": r"employer['\s]?s\s+liability\s+insurance\s+(?:of|exceeding)?\s*£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)",
                "category": "Insurance",
                "score_func": lambda m: 12 if float(m.group(1)) > 15 else 8,
            },
            {
                "pattern": r"insurance\s+requirements?:\s+£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)",
                "category": "Insurance",
                "score_func": lambda m: 15 if float(m.group(1)) > 20 else (12 if float(m.group(1)) >= 10 else 8),
            },
        ])
        
        # 3. Excessive Financial Thresholds
        # High barrier: >£50M (15 points), Medium: £10-50M (12 points)
        patterns.extend([
            {
                "pattern": r"minimum\s+(?:annual\s+)?turnover\s+(?:of\s+)?£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)\s+for\s+past\s+\d+\s+consecutive\s+years?",
                "category": "Financial Thresholds",
                "score_func": lambda m: 15 if float(m.group(1)) > 50 else (12 if float(m.group(1)) >= 10 else 8),
            },
            {
                "pattern": r"minimum\s+(?:annual\s+)?turnover\s+(?:of\s+)?£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)",
                "category": "Financial Thresholds",
                "score_func": lambda m: 15 if float(m.group(1)) > 50 else (12 if float(m.group(1)) >= 10 else 8),
            },
            {
                "pattern": r"turnover\s+exceeding\s+£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)",
                "category": "Financial Thresholds",
                "score_func": lambda m: 15 if float(m.group(1)) > 50 else (12 if float(m.group(1)) >= 10 else 8),
            },
            {
                "pattern": r"audited\s+accounts?\s+demonstrating\s+turnover\s+exceeding\s+£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)",
                "category": "Financial Thresholds",
                "score_func": lambda m: 15 if float(m.group(1)) > 50 else (12 if float(m.group(1)) >= 10 else 8),
            },
            {
                "pattern": r"minimum\s+£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)\s+annual\s+turnover",
                "category": "Financial Thresholds",
                "score_func": lambda m: 15 if float(m.group(1)) > 50 else (12 if float(m.group(1)) >= 10 else 8),
            },
            {
                "pattern": r"financial\s+stability\s+with\s+minimum\s+£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)\s+revenue",
                "category": "Financial Thresholds",
                "score_func": lambda m: 15 if float(m.group(1)) > 50 else (12 if float(m.group(1)) >= 10 else 8),
            },
            {
                "pattern": r"parent\s+company\s+guarantee\s+required",
                "category": "Financial Thresholds",
                "score": 10,
            },
        ])
        
        # 4. Unrealistic Time Constraints
        # High barrier: Zero tolerance (12 points), 48 hours mobilization (12 points)
        patterns.extend([
            {
                "pattern": r"completed\s+within\s+(\d+)\s+weeks?\s+(?:of\s+contract\s+award\s+)?with\s+zero\s+tolerance",
                "category": "Time Constraints",
                "score": 12,
            },
            {
                "pattern": r"project\s+completion\s+in\s+(\d+)\s+weeks?\s+with\s+zero\s+tolerance\s+for\s+delays?",
                "category": "Time Constraints",
                "score": 12,
            },
            {
                "pattern": r"no\s+extensions?\s+permitted\s+under\s+any\s+circumstances",
                "category": "Time Constraints",
                "score": 12,
            },
            {
                "pattern": r"no\s+extensions?\s+permitted",
                "category": "Time Constraints",
                "score": 10,
            },
            {
                "pattern": r"mobilization\s+required\s+within\s+(\d+)\s+hours?",
                "category": "Time Constraints",
                "score_func": lambda m: 12 if int(m.group(1)) <= 48 else 8,
            },
            {
                "pattern": r"completion\s+deadline[:\s]+(\d+)\s+weeks?\s+with\s+zero\s+tolerance",
                "category": "Time Constraints",
                "score": 12,
            },
            {
                "pattern": r"all\s+work\s+must\s+be\s+completed\s+within\s+(\d+)\s+weeks?",
                "category": "Time Constraints",
                "score_func": lambda m: 10 if int(m.group(1)) <= 8 else 6,
            },
        ])
        
        # 5. Excessive Certification Requirements
        # High barrier: 3+ certifications (12 points), Medium: 1-2 certifications (8 points)
        patterns.extend([
            {
                "pattern": r"(?:must\s+hold|required)\s+(?:ISO\s+\d+(?:,\s*)?){3,}",
                "category": "Certifications",
                "score": 12,
            },
            {
                "pattern": r"ISO\s+\d+(?:,\s*ISO\s+\d+){2,}",
                "category": "Certifications",
                "score": 12,
            },
            {
                "pattern": r"ISO\s+\d+(?:,\s*ISO\s+\d+){1,2}(?:,\s*[A-Za-z\s]+)?",
                "category": "Certifications",
                "score": 8,  # 1-2 certifications
            },
            {
                "pattern": r"(\d+)\s+certifications?\s+(?:required|mandatory)",
                "category": "Certifications",
                "score_func": lambda m: 12 if int(m.group(1)) >= 3 else 8,
            },
            {
                "pattern": r"must\s+hold\s+certification\s+from\s+[a-z\s]+body",
                "category": "Certifications",
                "score": 8,
            },
            {
                "pattern": r"all\s+proposed\s+staff\s+must\s+have\s+[a-z\s]+qualification",
                "category": "Certifications",
                "score": 8,
            },
        ])
        
        # 6. Geographic or Infrastructure Requirements
        patterns.extend([
            {
                "pattern": r"must\s+maintain\s+offices?\s+in\s+(?:[A-Z][a-z]+(?:,\s*)?){2,}",
                "category": "Geographic Requirements",
                "score": 10,
            },
            {
                "pattern": r"must\s+own\s+equipment\s+valued\s+at\s+minimum\s+£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)",
                "category": "Infrastructure",
                "score_func": lambda m: 12 if float(m.group(1)) > 5 else 8,
            },
            {
                "pattern": r"dedicated\s+site\s+office\s+with\s+minimum\s+(\d+)\s+full[- ]time\s+staff",
                "category": "Infrastructure",
                "score_func": lambda m: 10 if int(m.group(1)) >= 10 else 6,
            },
        ])
        
        # 7. Overly Specific Experience Requirements
        patterns.extend([
            {
                "pattern": r"must\s+have\s+completed\s+contracts?\s+with\s+minimum\s+(\d+)\s+central\s+government\s+departments?",
                "category": "Experience Requirements",
                "score": 12,
            },
            {
                "pattern": r"evidence\s+of\s+handling\s+cases?\s+exceeding\s+£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)\s+in\s+value",
                "category": "Experience Requirements",
                "score_func": lambda m: 12 if float(m.group(1)) >= 100 else (10 if float(m.group(1)) >= 50 else 8),
            },
            {
                "pattern": r"cases?\s+exceeding\s+£?\s*(\d+(?:\.\d+)?)\s*(?:million|m)\s+in\s+value",
                "category": "Experience Requirements",
                "score_func": lambda m: 12 if float(m.group(1)) >= 100 else (10 if float(m.group(1)) >= 50 else 8),
            },
            {
                "pattern": r"portfolio\s+must\s+demonstrate\s+projects?\s+for\s+fortune\s+500\s+clients?",
                "category": "Experience Requirements",
                "score": 12,
            },
            {
                "pattern": r"fortune\s+500\s+clients?",
                "category": "Experience Requirements",
                "score": 10,
            },
            {
                "pattern": r"previous\s+experience\s+with\s+[a-z\s]+(?:mandatory|required)",
                "category": "Experience Requirements",
                "score": 10,
            },
            {
                "pattern": r"top\s+(\d+)\s+(?:law\s+firm|consultancy\s+firm|global\s+consultancy)",
                "category": "Experience Requirements",
                "score": 12,
            },
        ])
        
        # 8. Excessive Resource Requirements
        patterns.extend([
            {
                "pattern": r"must\s+employ\s+at\s+least\s+(\d+)\s+full[- ]time",
                "category": "Resource Requirements",
                "score_func": lambda m: 12 if int(m.group(1)) >= 50 else (8 if int(m.group(1)) >= 20 else 5),
            },
            {
                "pattern": r"minimum\s+team\s+of\s+(\d+)\s+senior\s+consultants?",
                "category": "Resource Requirements",
                "score_func": lambda m: 10 if int(m.group(1)) >= 8 else 6,
            },
            {
                "pattern": r"minimum\s+(\d+)\s+years?\s+experience\s+(?:each|required)",
                "category": "Resource Requirements",
                "score_func": lambda m: 10 if int(m.group(1)) >= 10 else 6,
            },
            {
                "pattern": r"mobilize\s+(\d+)\+\s+workers?",
                "category": "Resource Requirements",
                "score_func": lambda m: 12 if int(m.group(1)) >= 50 else 8,
            },
        ])
        
        # 9. Disproportionate Penalty Clauses
        # High barrier: £50K/week (12 points), Performance bond 15-20% (12 points)
        patterns.extend([
            {
                "pattern": r"liquidated\s+damages[:\s]+£?\s*(\d+(?:,\d+)?)\s+per\s+week",
                "category": "Penalty Clauses",
                "score_func": lambda m: 12 if int(m.group(1).replace(',', '')) >= 50000 else 8,
            },
            {
                "pattern": r"performance\s+bond\s+of\s+(\d+)[-–]?(\d+)?%",
                "category": "Penalty Clauses",
                "score_func": lambda m: 12 if int(m.group(1)) >= 15 else 8,
            },
            {
                "pattern": r"performance\s+bond\s+of\s+(\d+)%",
                "category": "Penalty Clauses",
                "score_func": lambda m: 12 if int(m.group(1)) >= 15 else 8,
            },
            {
                "pattern": r"penalty\s+clauses?\s+with\s+zero\s+tolerance",
                "category": "Penalty Clauses",
                "score": 12,
            },
            {
                "pattern": r"penalties?\s+for\s+delays?",
                "category": "Penalty Clauses",
                "score": 6,
            },
        ])
        
        # 10. Sole Source or Proprietary Specifications
        patterns.extend([
            {
                "pattern": r"must\s+use\s+materials?\s+from\s+[a-z\s]+manufacturer\s+only",
                "category": "Proprietary Specifications",
                "score": 10,
            },
            {
                "pattern": r"sole\s+source\s+specifications?",
                "category": "Proprietary Specifications",
                "score": 10,
            },
            {
                "pattern": r"compliance\s+with\s+proprietary\s+frameworks?\s+mandatory",
                "category": "Proprietary Specifications",
                "score": 10,
            },
            {
                "pattern": r"proprietary\s+frameworks?\s+mandatory",
                "category": "Proprietary Specifications",
                "score": 10,
            },
            {
                "pattern": r"must\s+use\s+[a-z\s]+(?:software|system)\s+exclusively",
                "category": "Proprietary Specifications",
                "score": 10,
            },
            {
                "pattern": r"specific\s+manufacturer\s+requirements?",
                "category": "Proprietary Specifications",
                "score": 8,
            },
        ])
        
        return patterns
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better pattern matching.
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Preprocessed text with normalized whitespace
        """
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def detect_barriers(self, text: str) -> Tuple[List[FlaggedPhrase], int]:
        """
        Detect barrier phrases in tender text using regex patterns.
        
        Args:
            text: The tender document text to analyze
            
        Returns:
            Tuple of (list of flagged phrases, total barrier score)
        """
        if not text or not text.strip():
            return [], 0
        
        # Preprocess text (normalize whitespace)
        processed_text = self._preprocess_text(text)
        
        flagged_phrases = []
        seen_phrases = set()  # Avoid duplicate detections
        
        for pattern_dict in self.patterns:
            regex = re.compile(pattern_dict["pattern"], re.IGNORECASE | re.MULTILINE)
            
            for match in regex.finditer(processed_text):
                phrase = match.group(0)
                # Avoid counting the same phrase multiple times
                phrase_key = (phrase.lower(), match.start(), match.end())
                if phrase_key in seen_phrases:
                    continue
                seen_phrases.add(phrase_key)
                
                # Calculate score
                if "score_func" in pattern_dict:
                    try:
                        score = pattern_dict["score_func"](match)
                    except (ValueError, IndexError):
                        score = pattern_dict.get("score", 5)
                else:
                    score = pattern_dict.get("score", 5)
                
                flagged_phrases.append(FlaggedPhrase(
                    phrase=phrase,
                    category=pattern_dict["category"],
                    score=score
                ))
        
        # Calculate total barrier score (capped at 100)
        total_score = min(sum(fp.score for fp in flagged_phrases), 100)
        
        return flagged_phrases, total_score
    
    def get_recommendation(self, score: int) -> str:
        """
        Get recommendation based on barrier score.
        
        Args:
            score: The barrier score (0-100)
            
        Returns:
            Recommendation string
        """
        if score >= 76:
            return "Very high barrier risk - strongly recommend review and revision"
        elif score >= 51:
            return "High barrier risk - recommend review for SME accessibility"
        elif score >= 26:
            return "Medium barrier risk - consider reviewing requirements"
        else:
            return "Low barrier risk - tender appears SME-friendly"
