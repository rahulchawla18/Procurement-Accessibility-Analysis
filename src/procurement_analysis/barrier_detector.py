"""
RAG-based Barrier Detection System for Tender Documents

This module implements a RAG (Retrieval-Augmented Generation) system using:
- Text similarity (Jaccard) for retrieving similar tender documents
- Groq API for LLM-based barrier analysis

Detects phrases in tender documents that create barriers for Small and Medium-sized Enterprises (SMEs).
"""

import re
import json
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from project root
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try loading from current directory as fallback
        load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None


@dataclass
class FlaggedPhrase:
    """Represents a flagged barrier phrase with its details."""
    phrase: str
    category: str
    score: int


class BarrierDetector:
    """
    RAG-based barrier detection system for tender documents.
    
    Uses Groq API with text similarity for retrieval and LLM analysis.
    """
    
    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        groq_model: str = "llama-3.1-8b-instant",
        knowledge_base_path: Optional[str] = None
    ):
        """
        Initialize the barrier detector.
        
        Args:
            groq_api_key: Groq API key (required, can also be set via GROQ_API_KEY env var)
            groq_model: Groq model to use (default: llama-3.1-8b-instant)
            knowledge_base_path: Path to JSON file with tender documents
        """
        if not GROQ_AVAILABLE:
            raise ImportError("groq package not installed. Install with: pip install groq")
        
        api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "Groq API key required. Set GROQ_API_KEY env var or pass groq_api_key parameter"
            )
        
        self.groq_client = Groq(api_key=api_key)
        self.groq_model = groq_model
        
        # Load knowledge base
        if knowledge_base_path is None:
            project_root = Path(__file__).parent.parent.parent
            knowledge_base_path = project_root / "data" / "sample_tender_documents.json"
        
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        print(f"RAG-based barrier detector initialized. Loaded {len(self.knowledge_base)} tender documents.")
    
    def _load_knowledge_base(self, path: str) -> List[Dict]:
        """Load tender documents from JSON file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Knowledge base file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("Knowledge base must be a JSON array")
        
        return data
    
    def _simple_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity using word overlap (Jaccard similarity).
        No external dependencies needed.
        """
        # Normalize and tokenize
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _retrieve_similar_documents(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve top-k most similar tender documents using simple text similarity.
        
        Args:
            query_text: Input tender text
            top_k: Number of similar documents to retrieve
            
        Returns:
            List of similar tender documents with similarity scores
        """
        similarities = []
        for doc in self.knowledge_base:
            doc_text = doc.get("text", "")
            similarity = self._simple_text_similarity(query_text, doc_text)
            similarities.append((similarity, doc))
        
        # Sort by similarity and get top-k
        similarities.sort(reverse=True, key=lambda x: x[0])
        top_docs = []
        for similarity, doc in similarities[:top_k]:
            doc_copy = doc.copy()
            doc_copy['similarity_score'] = similarity
            top_docs.append(doc_copy)
        
        return top_docs
    
    def _create_rag_prompt(self, tender_text: str, similar_documents: List[Dict]) -> str:
        """Create prompt for Groq LLM analysis."""
        context_examples = ""
        for i, doc in enumerate(similar_documents, 1):
            context_examples += f"\nExample {i} (Similarity: {doc['similarity_score']:.3f}):\n"
            context_examples += f"Title: {doc.get('title', 'N/A')}\n"
            context_examples += f"Text: {doc.get('text', '')[:400]}...\n"
        
        prompt = f"""You are an expert in analyzing public procurement tender documents to identify barriers that exclude Small and Medium-sized Enterprises (SMEs).

Your task is to analyze the following tender document and identify:
1. Barrier phrases that may exclude SMEs
2. Categories of barriers (Trading History, Insurance, Financial Thresholds, Time Constraints, Certifications, Geographic Requirements, Experience Requirements, Resource Requirements, Penalty Clauses, Proprietary Specifications)
3. Barrier scores (0-15 points per phrase, based on severity)
4. Total barrier score (0-100, sum of all phrase scores, capped at 100)
5. Recommendation based on total score

Barrier Scoring Guidelines:
- Trading History: 10+ years = 15 points, 5-10 years = 10 points
- Insurance: >£20M = 15 points, £10-20M = 12 points, <£10M = 8 points
- Financial Thresholds: >£50M = 15 points, £10-50M = 12 points
- Time Constraints: Zero tolerance = 12 points, tight deadlines = 6-10 points
- Certifications: 3+ certifications = 12 points, 1-2 = 8 points
- Other barriers: 8-12 points depending on severity

Similar Tender Examples for Context:
{context_examples}

Tender Document to Analyze:
{tender_text}

Please analyze this tender document and provide a JSON response with the following structure:
{{
    "barrier_score": <integer 0-100>,
    "flagged_phrases": [
        {{
            "phrase": "<exact phrase from text>",
            "category": "<category name>",
            "score": <integer 0-15>
        }}
    ],
    "recommendation": "<recommendation text based on score>"
}}

Recommendation Guidelines:
- 0-25: "Low barrier risk - tender appears SME-friendly"
- 26-50: "Medium barrier risk - consider reviewing requirements"
- 51-75: "High barrier risk - recommend review for SME accessibility"
- 76-100: "Very high barrier risk - strongly recommend review and revision"

Return ONLY valid JSON, no additional text or explanation."""
        
        return prompt
    
    def _call_groq(self, prompt: str) -> str:
        """Call Groq API for LLM analysis."""
        try:
            response = self.groq_client.chat.completions.create(
                model=self.groq_model,
                messages=[
                    {"role": "system", "content": "You are an expert in procurement barrier analysis. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Groq API error: {str(e)}")
    
    def detect_barriers(self, text: str) -> Tuple[List[FlaggedPhrase], int]:
        """
        Detect barrier phrases in tender text using RAG with Groq API.
        
        Args:
            text: The tender document text to analyze
            
        Returns:
            Tuple of (list of flagged phrases, total barrier score)
        """
        if not text or not text.strip():
            return [], 0
        
        # Retrieve similar documents
        similar_docs = self._retrieve_similar_documents(text, top_k=5)
        
        # Create analysis prompt
        prompt = self._create_rag_prompt(text, similar_docs)
        
        # Call Groq API
        llm_response = self._call_groq(prompt)
        
        # Parse response
        try:
            result = json.loads(llm_response)
        except json.JSONDecodeError:
            # Try to extract JSON from response if wrapped in text
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise ValueError(f"Failed to parse Groq response as JSON: {llm_response}")
        
        # Convert to FlaggedPhrase objects
        flagged_phrases = [
            FlaggedPhrase(
                phrase=fp["phrase"],
                category=fp["category"],
                score=fp["score"]
            )
            for fp in result.get("flagged_phrases", [])
        ]
        
        barrier_score = result.get("barrier_score", 0)
        
        return flagged_phrases, barrier_score
    
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
