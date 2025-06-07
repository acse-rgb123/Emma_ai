# Standard library imports
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# Local application imports
from app.config import settings
from app.services.provider_manager import provider_manager

# AI Provider imports
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

class LLMAnalyzer:
    """Analyzer that primarily uses LLM for all extraction"""
    
    def __init__(self):
        self.setup_ai_client()
        self.policies = self._load_policies()
        
    def setup_ai_client(self):
        """Setup AI client based on configured provider"""
        self.provider = provider_manager.get_current_provider()
        self.api_key = provider_manager.get_current_api_key()
        
        if not self.api_key:
            logger.warning(f"No API key found for {self.provider}, will use rule-based fallback")
            self.client = None
            return
            
        try:
            if self.provider == "openai" and OpenAI:
                self.client = OpenAI(api_key=self.api_key)
                self.model = provider_manager.get_current_model()
            elif self.provider == "claude" and anthropic:
                self.client = anthropic.Client(api_key=self.api_key)
                self.model = provider_manager.get_current_model()
            elif self.provider == "gemini" and genai:
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(provider_manager.get_current_model())
                self.model = provider_manager.get_current_model()
            else:
                logger.error(f"Unknown provider: {self.provider}")
                self.client = None
        except Exception as e:
            logger.error(f"Failed to setup AI client: {e}")
            self.client = None
    
    def _load_policies(self) -> str:
        """Load policies from file"""
        try:
            policy_path = Path(__file__).parent.parent / "data" / "policies.txt"
            with open(policy_path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading policies: {e}")
            return self._get_default_policies()
    
    def _get_default_policies(self) -> str:
        """Return default policies"""
        return """
        Section 3: Mobility & Moving
        - If a service user falls, email supervisor immediately
        - If recurring falls (2+ in a week), CC Risk Assessor
        
        Section 5: Mental Health
        - If confused/disoriented, alert family/next of kin
        """
    
    async def analyze(self, transcript: str) -> Dict[str, Any]:
        """Analyze transcript - LLM first, fallback to rules only if needed"""
        logger.info(f"Starting analysis with {self.provider}")
        
        # Try LLM analysis first
        if self.client:
            try:
                result = await self._llm_analysis(transcript)
                if result and self._validate_llm_result(result):
                    logger.info("LLM analysis successful")
                    return result
                else:
                    logger.warning("LLM result invalid, trying again with structured prompt")
                    result = await self._llm_structured_analysis(transcript)
                    if result and self._validate_llm_result(result):
                        return result
            except Exception as e:
                logger.error(f"LLM analysis failed: {e}")
        
        # Only use fallback if LLM completely fails
        logger.warning("Using rule-based fallback analysis")
        return self._rule_based_analysis(transcript)
    
    async def _llm_analysis(self, transcript: str) -> Optional[Dict[str, Any]]:
        """Primary LLM analysis with comprehensive extraction"""
        prompt = f"""
        Analyze this social care call transcript and extract ALL information.
        
        POLICIES:
        {self.policies}
        
        TRANSCRIPT:
        {transcript}
        
        Extract and return a JSON object with:
        {{
            "service_user_name": "Extract the actual name from transcript (or 'Unknown' if not found)",
            "service_user_age": "Extract age if mentioned (or null)",
            "location": "Extract where the incident occurred (or 'Not specified')",
            "incident_type": "Fall/Medical/Mental Health/Other",
            "incident_time": "When it happened if mentioned",
            "summary": "Brief summary of the incident",
            "violations": [
                {{
                    "policy_section": "Section name",
                    "violation_type": "Type of violation",
                    "severity": "high/medium/low",
                    "description": "What happened",
                    "required_action": "What must be done"
                }}
            ],
            "notifications_required": ["List of people/roles to notify"],
            "risk_assessments": ["List of assessments needed"],
            "recommendations": ["List of recommendations"],
            "extracted_facts": {{
                "injuries_mentioned": ["list any injuries"],
                "symptoms": ["list symptoms mentioned"],
                "frequency": "how often this happens",
                "witnesses": ["any witnesses mentioned"],
                "family_mentioned": ["family members mentioned"],
                "medical_conditions": ["any conditions mentioned"],
                "medications": ["any medications mentioned"]
            }}
        }}
        
        IMPORTANT: Extract the ACTUAL service user name from the transcript, not a placeholder.
        Look for phrases like "I'm [name]", "this is [name]", "my name is [name]", or "[name]: speaking".
        """
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert social care analyst. Extract all relevant information from transcripts."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3  # Lower temperature for more consistent extraction
                )
                return json.loads(response.choices[0].message.content)
                
            elif self.provider == "claude":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0.3,
                    system="You are an expert social care analyst. Always return valid JSON.",
                    messages=[{"role": "user", "content": prompt}]
                )
                return json.loads(response.content[0].text)
                
            elif self.provider == "gemini":
                response = self.client.generate_content(prompt + "\n\nReturn ONLY valid JSON, no markdown.")
                json_str = response.text.strip()
                if json_str.startswith("```"):
                    json_str = json_str.split("```")[1]
                    if json_str.startswith("json"):
                        json_str = json_str[4:]
                return json.loads(json_str.strip())
                
        except Exception as e:
            logger.error(f"LLM analysis error: {e}")
            return None
    
    async def _llm_structured_analysis(self, transcript: str) -> Optional[Dict[str, Any]]:
        """Structured LLM analysis with step-by-step extraction"""
        prompt = f"""
        Step 1: Find the service user's name in this transcript:
        {transcript}
        
        Look for:
        - "I'm [name]" or "I am [name]"
        - "This is [name]"
        - "My name is [name]"
        - "[name]:" at the start of dialogue
        - Someone addressing them by name
        
        Step 2: Find the location (bedroom, bathroom, kitchen, etc.)
        
        Step 3: Identify the incident type and policy violations based on:
        {self.policies}
        
        Return a complete JSON analysis following the structure provided.
        """
        
        return await self._llm_analysis(transcript)
    
    def _validate_llm_result(self, result: Dict[str, Any]) -> bool:
        """Validate that LLM returned proper structure with actual data"""
        required_fields = ["service_user_name", "location", "summary", "violations"]
        
        # Check required fields exist
        for field in required_fields:
            if field not in result:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Check that name isn't a placeholder
        name = result.get("service_user_name", "").lower()
        if name in ["", "unknown", "not found", "service user", "[name]", "greg jones"]:
            logger.warning(f"Invalid service user name: {name}")
            return False
        
        return True
    
    def _rule_based_analysis(self, transcript: str) -> Dict[str, Any]:
        """Rule-based fallback - only used when LLM completely fails"""
        logger.info("Using rule-based fallback analysis")
        
        # Import the rule-based extraction functions
        try:
            from .analyzer_fix import extract_name_from_transcript, extract_location_from_transcript
            service_user_name = extract_name_from_transcript(transcript) or "Unknown"
            location = extract_location_from_transcript(transcript) or "Not specified"
        except:
            service_user_name = "Unknown"
            location = "Not specified"
        
        analysis = {
            "service_user_name": service_user_name,
            "location": location,
            "incident_type": "Unknown",
            "summary": "Automated analysis unavailable - manual review required",
            "violations": [],
            "notifications_required": [],
            "risk_assessments": [],
            "recommendations": ["Manual review recommended due to analysis failure"],
            "extracted_facts": {
                "llm_used": False,
                "fallback_reason": "LLM analysis failed"
            }
        }
        
        # Basic keyword detection for violations
        transcript_lower = transcript.lower()
        
        if any(word in transcript_lower for word in ["fall", "fallen", "fell"]):
            analysis["incident_type"] = "Fall"
            analysis["violations"].append({
                "policy_section": "Section 3: Mobility & Moving",
                "violation_type": "Fall incident",
                "severity": "medium",
                "description": "Service user reported falling",
                "required_action": "Email supervisor immediately"
            })
            analysis["notifications_required"].append("Supervisor")
            
        if any(word in transcript_lower for word in ["confused", "disoriented", "can't remember"]):
            if analysis["incident_type"] == "Unknown":
                analysis["incident_type"] = "Mental Health Concern"
            analysis["violations"].append({
                "policy_section": "Section 5: Mental Health",
                "violation_type": "Cognitive concern",
                "severity": "high",
                "description": "Service user showing signs of confusion",
                "required_action": "Alert family or next of kin"
            })
            analysis["notifications_required"].append("Family/Next of Kin")
        
        return analysis
