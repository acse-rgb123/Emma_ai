import os
import json
import logging
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from app.config import settings

# OpenAI import
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from .analyzer_fix import extract_name_from_transcript, extract_location_from_transcript
except ImportError:
    extract_name_from_transcript = lambda x: ""
    extract_location_from_transcript = lambda x: ""

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        if not OpenAI:
            raise ImportError("OpenAI package is required but not installed")
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required but not provided")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.template = self._load_template()
    
    def _load_template(self) -> Dict[str, str]:
        """Load incident report template"""
        try:
            template_path = Path(__file__).parent.parent / "data" / "incident_template.json"
            with open(template_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            return self._get_default_template()
    
    def _get_default_template(self) -> Dict[str, str]:
        """Return default template"""
        return {
            "date_time": "DateTime",
            "service_user_name": "Text",
            "location": "Text",
            "incident_type": "Text",
            "description": "Text",
            "immediate_actions": "Text",
            "first_aid_administered": "Boolean",
            "emergency_services_contacted": "Boolean",
            "who_was_notified": "Text",
            "witnesses": "Text",
            "agreed_next_steps": "Text",
            "risk_assessment_needed": "Boolean",
            "risk_assessment_type": "Text"
        }
    
    async def generate_report(self, transcript: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate incident report based on transcript and analysis"""
        try:
            report = await self._ai_generate(transcript, analysis)
            if not report:
                report = self._fallback_generate(transcript, analysis)
            return report
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return self._fallback_generate(transcript, analysis)
    
    async def _ai_generate(self, transcript: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Use OpenAI to generate report"""
        try:
            prompt = f"""
            Based on this call transcript and analysis, generate an incident report.
            
            Transcript:
            {transcript}
            
            Analysis:
            {json.dumps(analysis, indent=2)}
            
            Generate a complete incident report with these fields:
            {json.dumps(list(self.template.keys()), indent=2)}
            
            Extract all relevant information from the transcript. Be specific and detailed.
            Return as JSON object.
            """
            
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                max_tokens=settings.openai_max_tokens,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": "You are a social care incident report specialist. Generate detailed, accurate incident reports from transcripts."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            report = json.loads(response.choices[0].message.content)
            
            # Ensure all fields are present
            for field in self.template.keys():
                if field not in report:
                    report[field] = self._get_default_value(field)
                    
            return report
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return None
    
    def _fallback_generate(self, transcript: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report using rule-based approach"""
        logger.info("Using fallback report generation")
        
        # Extract information from transcript
        service_user_name = extract_name_from_transcript(transcript) or "Unknown"
        location = extract_location_from_transcript(transcript) or "Not specified"
        
        # Determine incident type from analysis
        incident_types = []
        for violation in analysis.get("violations", []):
            if "fall" in violation.get("violation_type", "").lower():
                incident_types.append("Fall")
            if "mental" in violation.get("violation_type", "").lower():
                incident_types.append("Mental Health Concern")
        
        report = {
            "date_time": datetime.now().isoformat(),
            "service_user_name": service_user_name,
            "location": location,
            "incident_type": ", ".join(incident_types) or "General Concern",
            "description": self._extract_description(transcript),
            "immediate_actions": "Provided reassurance and comfort. Assessed physical condition. Initiated support protocol.",
            "first_aid_administered": False,
            "emergency_services_contacted": False,
            "who_was_notified": ", ".join(analysis.get("notifications_required", [])),
            "witnesses": "None",
            "agreed_next_steps": self._generate_next_steps(analysis),
            "risk_assessment_needed": len(analysis.get("risk_assessments", [])) > 0,
            "risk_assessment_type": ", ".join(analysis.get("risk_assessments", []))
        }
        
        return report
    
    def _extract_description(self, transcript: str) -> str:
        """Extract incident description from transcript"""
        description_parts = []
        
        if "fallen" in transcript.lower():
            description_parts.append("Service user reported falling and being unable to get up independently.")
        
        if "confused" in transcript.lower() or "can't remember" in transcript.lower():
            description_parts.append("Service user exhibited signs of confusion and memory difficulties.")
        
        if "third time" in transcript.lower():
            description_parts.append("This is a recurring incident (third time this week).")
        
        return " ".join(description_parts) or "Service user contacted support line with concerns."
    
    def _generate_next_steps(self, analysis: Dict[str, Any]) -> str:
        """Generate next steps based on analysis"""
        steps = []
        
        for violation in analysis.get("violations", []):
            if "recurring falls" in violation.get("violation_type", "").lower():
                steps.append("Arrange immediate moving and handling risk assessment")
            elif "fall" in violation.get("violation_type", "").lower():
                steps.append("Monitor for additional falls")
            
            if "mental health" in violation.get("violation_type", "").lower():
                steps.append("Contact family to discuss cognitive concerns")
                steps.append("Consider cognitive assessment referral")
        
        if not steps:
            steps.append("Continue regular monitoring and support")
        
        return "; ".join(steps)
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for field type"""
        if "Boolean" in str(self.template.get(field, "")):
            return False
        elif "DateTime" in str(self.template.get(field, "")):
            return datetime.now().isoformat()
        else:
            return ""
    
    async def regenerate_with_feedback(self, original: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """Regenerate report with user feedback using OpenAI"""
        try:
            prompt = f"""
            Original report:
            {json.dumps(original, indent=2)}
            
            User feedback:
            {feedback}
            
            Generate an updated incident report incorporating the feedback.
            Maintain the same structure but adjust content based on feedback.
            """
            
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                max_tokens=settings.openai_max_tokens,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": "Update the incident report based on user feedback."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error regenerating report with OpenAI: {e}")
            return original
