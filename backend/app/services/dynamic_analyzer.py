import json
import logging
from typing import Dict, Any
from app.config import settings

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)

class DynamicAnalyzer:
    """Analyzer that uses OpenAI for analysis"""
    
    def __init__(self):
        if not OpenAI:
            raise ImportError("OpenAI package is required but not installed")
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required but not provided")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def analyze(self, transcript: str, policies: str) -> Dict[str, Any]:
        """Analyze transcript using OpenAI"""
        logger.info("Analyzing with OpenAI")
        
        try:
            prompt = self._create_prompt(transcript, policies)
            return await self._analyze_openai(prompt)
                
        except Exception as e:
            logger.error(f"Error with OpenAI: {e}")
            # Fallback to rule-based analysis
            return self._fallback_analysis(transcript)
    
    def _create_prompt(self, transcript: str, policies: str) -> str:
        """Create analysis prompt"""
        return f"""
        Analyze the following social care call transcript against these policies:
        
        {policies}
        
        Transcript:
        {transcript}
        
        Identify:
        1. Any policy violations or concerns
        2. Required actions based on policies
        3. Who needs to be notified
        4. Risk assessments needed
        5. Mental health concerns
        
        Return analysis in JSON format with keys: summary, violations, notifications_required, risk_assessments, recommendations
        """
    
    async def _analyze_openai(self, prompt: str) -> Dict[str, Any]:
        """Analyze using OpenAI"""
        response = self.client.chat.completions.create(
            model=settings.openai_model,
            max_tokens=settings.openai_max_tokens,
            messages=[
                {"role": "system", "content": "You are a social care compliance analyst."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    
    def _fallback_analysis(self, transcript: str) -> Dict[str, Any]:
        """Fallback rule-based analysis"""
        # ... (existing fallback logic)
        return {
            "summary": "Fallback analysis used",
            "violations": [],
            "notifications_required": [],
            "risk_assessments": [],
            "recommendations": []
        }
