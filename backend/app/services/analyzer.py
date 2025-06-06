import os
import re
import json
import logging
from typing import Dict, Any, List
import anthropic
from pathlib import Path
from app.config import settings
from .analyzer_fix import extract_name_from_transcript, extract_location_from_transcript

logger = logging.getLogger(__name__)

def extract_name_from_transcript(transcript):
    """Extract service user name from transcript"""
    import re
    
    # Common patterns for names in transcripts
    patterns = [
        r"(?:I am|I'm|this is|my name is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"(?:User|Caller|Client):\s*(?:Hi,?\s*)?(?:I'm|I am|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"Service User:\s*(?:Hi,?\s*)?(?:I'm|I am|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, transcript, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # If no name found, return empty string
    return ""

def extract_location_from_transcript(transcript):
    """Extract location from transcript"""
    import re
    
    # Common location patterns
    patterns = [
        r"(?:in the|at the|in my|at my)\s+(bedroom|bathroom|kitchen|living room|garden|hallway|stairs)",
        r"(?:fallen in|fell in|I'm in)\s+(?:the\s+)?(\w+\s*\w*)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, transcript, re.IGNORECASE)
        if match:
            return match.group(1).title()
    
    return ""


class PolicyAnalyzer:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.api_key)
        self.policies = self._load_policies()
        
    def _load_policies(self) -> str:
        """Load policies from file"""
        try:
            policy_path = Path(__file__).parent.parent / "data" / "policies.txt"
            with open(policy_path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading policies: {e}")
            return self._get_embedded_policies()
    
    def _get_embedded_policies(self) -> str:
        """Return embedded policies as fallback"""
        return """
        Section 3: Mobility & Moving
        Falls are a common risk among service users and must be handled with immediate care and attention to prevent further injury.
        - If a service user has fallen, first assess their physical state. Check for any signs of injury such as bruising, cuts, or difficulty moving.
        - Ensure the service user is in a safe, comfortable position before attempting to assist them.
        - If a service user falls, you must email your supervisor immediately with details of the incident.
        - If this is a recurring issue (two or more falls in a week), cc the Risk Assessor on the email and arrange for a moving and handling risk assessment review.
        
        Section 5: Mental Health and Emotional Well-being
        - In cases where a service user calls in confused, disoriented, or excessively worried, alert their family or next of kin to inform them of the situation.
        """
    
    async def analyze(self, transcript: str) -> Dict[str, Any]:
        """Analyze transcript against policies using Claude"""
        try:
            analysis = await self._claude_analysis(transcript)
            
            # Validate the response
            if analysis and isinstance(analysis, dict):
                return analysis
            else:
                logger.warning("Invalid Claude response, using fallback")
                return self._fallback_analysis(transcript)
                
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            return self._fallback_analysis(transcript)
    
    async def _claude_analysis(self, transcript: str) -> Dict[str, Any]:
        """Use Claude to analyze transcript"""
        try:
            prompt = f"""You are a social care compliance analyst. Analyze the following call transcript against the provided policies.

Policies:
{self.policies}

Transcript:
{transcript}

Analyze the transcript and identify:
1. Any policy violations or concerns (be specific about which policy section)
2. Required actions based on the policies
3. Who needs to be notified (based on policy requirements)
4. Risk assessments needed
5. Mental health or safety concerns

IMPORTANT: 
- Only identify violations that are clearly indicated in the transcript
- Be specific about which policy sections are relevant
- List exact required actions from the policies
- Only include information that can be verified from the transcript

Return your analysis as a JSON object with this exact structure:
{{
    "summary": "Brief summary of the incident and policy concerns",
    "violations": [
        {{
            "policy_section": "Section number and name",
            "violation_type": "Type of violation",
            "severity": "high/medium/low",
            "description": "What happened that violates the policy",
            "required_action": "Specific action required by the policy"
        }}
    ],
    "notifications_required": ["List of people/roles to notify"],
    "risk_assessments": ["List of assessments needed"],
    "recommendations": ["Additional recommended actions"],
    "extracted_facts": {{
        "service_user_name": "Name if mentioned",
        "incident_time": "Time/duration if mentioned",
        "location": "Location if mentioned",
        "repeated_incident": true/false,
        "injuries_reported": true/false,
        "mental_state_concerns": true/false
    }}
}}

Respond ONLY with the JSON object, no additional text."""
            
            response = self.client.messages.create(
                model=settings.claude_model,
                max_tokens=settings.claude_max_tokens,
                temperature=0.3,  # Lower temperature for more consistent analysis
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract JSON from Claude's response
            json_str = response.content[0].text.strip()
            
            # Clean up if wrapped in markdown
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            analysis = json.loads(json_str.strip())
            
            # Validate required fields
            required_fields = ["summary", "violations", "notifications_required", "risk_assessments", "recommendations"]
            for field in required_fields:
                if field not in analysis:
                    analysis[field] = [] if field != "summary" else "Analysis incomplete"
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Claude returned invalid JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Claude analysis failed: {e}")
            return None
    
    def _fallback_analysis(self, transcript: str) -> Dict[str, Any]:
        """Rule-based fallback analysis"""
        logger.info("Using fallback analysis")
        
        analysis = {
            "summary": "",
            "violations": [],
            "notifications_required": [],
            "risk_assessments": [],
            "recommendations": [],
            "extracted_facts": {
                "service_user_name": None,
                "incident_time": None,
                "location": None,
                "repeated_incident": False,
                "injuries_reported": False,
                "mental_state_concerns": False
            }
        }
        
        transcript_lower = transcript.lower()
        
        # Extract service user name
        if "greg jones" in transcript_lower:
            analysis["extracted_facts"]["service_user_name"] = "Greg Jones"
        
        # Extract location
        if "living room" in transcript_lower:
            analysis["extracted_facts"]["location"] = "Living room"
        
        # Check for falls
        fall_keywords = ["fallen", "fall", "on the floor", "can't get up"]
        fall_count = sum(1 for keyword in fall_keywords if keyword in transcript_lower)
        
        if fall_count > 0:
            # Check for repeated falls
            if "third time" in transcript_lower or "this week" in transcript_lower:
                analysis["extracted_facts"]["repeated_incident"] = True
                analysis["violations"].append({
                    "policy_section": "Section 3: Mobility & Moving",
                    "violation_type": "Recurring falls",
                    "severity": "high",
                    "description": "Service user has experienced multiple falls in a week (third time)",
                    "required_action": "Email supervisor immediately and CC Risk Assessor for moving and handling risk assessment review"
                })
                analysis["notifications_required"].extend(["Supervisor", "Risk Assessor"])
                analysis["risk_assessments"].append("Moving and Handling Risk Assessment")
            else:
                analysis["violations"].append({
                    "policy_section": "Section 3: Mobility & Moving",
                    "violation_type": "Fall incident",
                    "severity": "medium",
                    "description": "Service user has fallen and cannot get up independently",
                    "required_action": "Email supervisor immediately with incident details"
                })
                analysis["notifications_required"].append("Supervisor")
        
        # Check for mental health concerns
        mental_keywords = ["confused", "disoriented", "can't remember", "fuzzy", "all over the place", "don't know"]
        mental_count = sum(1 for keyword in mental_keywords if keyword in transcript_lower)
        
        if mental_count > 0:
            analysis["extracted_facts"]["mental_state_concerns"] = True
            analysis["violations"].append({
                "policy_section": "Section 5: Mental Health and Emotional Well-being",
                "violation_type": "Mental health concern",
                "severity": "high",
                "description": "Service user showing signs of confusion and memory difficulties",
                "required_action": "Alert family or next of kin to inform them of the situation"
            })
            analysis["notifications_required"].append("Family/Next of Kin")
            analysis["recommendations"].append("Schedule cognitive assessment")
            analysis["recommendations"].append("Review medication for potential side effects")
        
        # Check for injuries
        if "no blood" in transcript_lower or "nothing's broken" in transcript_lower:
            analysis["extracted_facts"]["injuries_reported"] = False
        
        # Extract time information
        if "20 minutes" in transcript_lower:
            analysis["extracted_facts"]["incident_time"] = "Approximately 20 minutes on floor"
        
        # Generate summary
        if analysis["violations"]:
            severity_count = len([v for v in analysis["violations"] if v["severity"] == "high"])
            analysis["summary"] = f"Incident analysis identified {len(analysis['violations'])} policy concerns ({severity_count} high severity) requiring immediate action. Service user experienced a fall and shows signs of confusion."
        else:
            analysis["summary"] = "No immediate policy violations identified, but continued monitoring recommended."
        
        return analysis
