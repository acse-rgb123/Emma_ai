import json
import logging
from openai import OpenAI
import google.generativeai as genai
import anthropic
from typing import Dict, Any
from app.services.provider_manager import provider_manager

logger = logging.getLogger(__name__)

class DynamicAnalyzer:
    """Analyzer that dynamically switches between AI providers"""
    
    def __init__(self):
        self.provider_manager = provider_manager
    
    def _get_client(self):
        """Get the appropriate AI client based on current provider"""
        provider = self.provider_manager.get_current_provider()
        api_key = self.provider_manager.get_current_api_key()
        
        if not api_key:
            raise ValueError(f"No API key configured for {provider}")
        
        if provider == "openai":
            return OpenAI(api_key=api_key)
        elif provider == "claude":
            return anthropic.Client(api_key=api_key)
        elif provider == "gemini":
            genai.configure(api_key=api_key)
            return genai.GenerativeModel(self.provider_manager.get_current_model())
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def analyze(self, transcript: str, policies: str) -> Dict[str, Any]:
        """Analyze transcript using the current AI provider"""
        provider = self.provider_manager.get_current_provider()
        logger.info(f"Analyzing with provider: {provider}")
        
        try:
            client = self._get_client()
            prompt = self._create_prompt(transcript, policies)
            
            if provider == "openai":
                return await self._analyze_openai(client, prompt)
            elif provider == "claude":
                return await self._analyze_claude(client, prompt)
            elif provider == "gemini":
                return await self._analyze_gemini(client, prompt)
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except Exception as e:
            logger.error(f"Error with {provider}: {e}")
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
    
    async def _analyze_openai(self, client, prompt: str) -> Dict[str, Any]:
        """Analyze using OpenAI"""
        response = client.chat.completions.create(
            model=self.provider_manager.get_current_model(),
            messages=[
                {"role": "system", "content": "You are a social care compliance analyst."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    
    async def _analyze_claude(self, client, prompt: str) -> Dict[str, Any]:
        """Analyze using Claude"""
        response = client.messages.create(
            model=self.provider_manager.get_current_model(),
            max_tokens=2000,
            system="You are a social care compliance analyst. Always respond with valid JSON.",
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.content[0].text)
    
    async def _analyze_gemini(self, client, prompt: str) -> Dict[str, Any]:
        """Analyze using Gemini"""
        response = client.generate_content(prompt + "\n\nReturn only valid JSON.")
        json_str = response.text.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:-3]
        return json.loads(json_str)
    
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
