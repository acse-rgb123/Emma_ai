# Standard library imports
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# Local application imports
from app.config import settings

# AI Provider imports
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)

class LLMAnalyzer:
    """Analyzer that primarily uses LLM for all extraction"""
    
    def __init__(self):
        if not OpenAI:
            raise ImportError("OpenAI package is required but not installed")
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required but not provided")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.policies = self._load_policies()
    
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
        """Analyze transcript using OpenAI - fallback to rules only if needed"""
        logger.info("Starting analysis with OpenAI")
        
        # Try OpenAI analysis first
        try:
            result = await self._openai_analysis(transcript)
            if result and self._validate_result(result):
                logger.info("OpenAI analysis successful")
                return result
            else:
                logger.warning("OpenAI result invalid, trying again with structured prompt")
                result = await self._openai_structured_analysis(transcript)
                if result and self._validate_result(result):
                    return result
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
        
        # Only use fallback if OpenAI completely fails
        logger.warning("Using rule-based fallback analysis")
        return self._rule_based_analysis(transcript)
    
    async def _openai_analysis(self, transcript: str) -> Optional[Dict[str, Any]]:
        """Primary OpenAI analysis with comprehensive extraction"""
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
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                max_tokens=settings.openai_max_tokens,
                messages=[
                    {"role": "system", "content": "You are an expert social care analyst. Extract all relevant information from transcripts."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3  # Lower temperature for more consistent extraction
            )
            return json.loads(response.choices[0].message.content)
                
        except Exception as e:
            logger.error(f"OpenAI analysis error: {e}")
            return None
    
    async def _openai_structured_analysis(self, transcript: str) -> Optional[Dict[str, Any]]:
        """Structured OpenAI analysis with step-by-step extraction"""
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
        
        return await self._openai_analysis(transcript)
    
    def _validate_result(self, result: Dict[str, Any]) -> bool:
        """Validate that OpenAI returned proper structure with actual data"""
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
        """Rule-based fallback - only used when OpenAI completely fails"""
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
                "openai_used": False,
                "fallback_reason": "OpenAI analysis failed"
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
