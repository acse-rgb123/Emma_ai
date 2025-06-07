import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

from app.config import settings

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

class EmailGenerator:
    def __init__(self):
        self.ai_provider = settings.ai_provider
        self.api_key = settings.api_key
        self._setup_ai_client()
    
    def _setup_ai_client(self):
        """Setup AI client based on provider"""
        if self.ai_provider == "openai" and OpenAI:
            self.client = OpenAI(api_key=self.api_key)
        elif self.ai_provider == "claude" and anthropic:
            self.client = anthropic.Client(api_key=self.api_key)
        elif self.ai_provider == "gemini" and genai:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(settings.gemini_model)
        else:
            raise ImportError(f"AI provider {self.ai_provider} not available or not installed")
        
    async def generate_email(self, incident_report: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate email draft based on incident report and analysis"""
        try:
            email = await self._ai_generate(incident_report, analysis)
            if not email:
                email = self._fallback_generate(incident_report, analysis)
            return email
        except Exception as e:
            logger.error(f"Error generating email: {e}")
            return self._fallback_generate(incident_report, analysis)
    
    async def _ai_generate(self, incident_report: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to generate email"""
        try:
            prompt = f"""
            Generate a professional email to notify relevant parties about this incident.
            
            Incident Report:
            {json.dumps(incident_report, indent=2)}
            
            Analysis:
            {json.dumps(analysis, indent=2)}
            
            Create an email that:
            1. Clearly states the incident
            2. Outlines immediate actions taken
            3. Specifies required follow-up actions
            4. Maintains professional tone
            5. Includes all necessary recipients based on policy requirements
            
            Return as JSON with keys: to, cc, subject, body, priority
            """
            
            if self.ai_provider == "openai":
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": "You are a social care coordinator drafting incident notification emails. Be clear, professional, and action-oriented."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            
            elif self.ai_provider == "claude":
                response = self.client.messages.create(
                    model=settings.claude_model,
                    max_tokens=settings.claude_max_tokens,
                    system="You are a social care coordinator drafting incident notification emails. Be clear, professional, and action-oriented. Return valid JSON only.",
                    messages=[{"role": "user", "content": prompt}]
                )
                return json.loads(response.content[0].text)
            
            elif self.ai_provider == "gemini":
                prompt = f"""You are a social care coordinator drafting incident notification emails.
                {prompt}
                
                Return only valid JSON, no additional text or markdown.
                """
                response = self.client.generate_content(prompt)
                json_str = response.text.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
                return json.loads(json_str.strip())
            
        except Exception as e:
            logger.error(f"AI email generation failed: {e}")
            return None
    
    def _fallback_generate(self, incident_report: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate email using template approach"""
        logger.info("Using fallback email generation")
        
        # Determine recipients
        to_recipients = ["supervisor@emmacare.com"]
        cc_recipients = []
        
        # Check for specific notifications required
        for notification in analysis.get("notifications_required", []):
            if "risk assessor" in notification.lower():
                cc_recipients.append("riskassessment@emmacare.com")
            if "family" in notification.lower() or "next of kin" in notification.lower():
                to_recipients.append("family.contact@emmacare.com")
        
        # Determine priority
        priority = "normal"
        high_severity_count = sum(1 for v in analysis.get("violations", []) 
                                 if v.get("severity") == "high")
        if high_severity_count > 0:
            priority = "high"
        
        # Generate subject
        incident_type = incident_report.get("incident_type", "Incident")
        service_user = incident_report.get("service_user_name", "Service User")
        subject = f"URGENT: {incident_type} - {service_user}" if priority == "high" else f"Incident Report: {incident_type} - {service_user}"
        
        # Generate body
        body = self._generate_email_body(incident_report, analysis, priority)
        
        return {
            "to": to_recipients,
            "cc": cc_recipients,
            "subject": subject,
            "body": body,
            "priority": priority,
            "attachments": ["incident_report.pdf"]
        }
    
    def _generate_email_body(self, incident_report: Dict[str, Any], analysis: Dict[str, Any], priority: str) -> str:
        """Generate email body"""
        
        body_parts = []
        
        # Opening
        if priority == "high":
            body_parts.append("This email requires immediate attention.")
            body_parts.append("")
        
        body_parts.append("Dear Team,")
        body_parts.append("")
        body_parts.append(f"I am writing to inform you of an incident involving {incident_report.get('service_user_name', 'a service user')} that occurred on {self._format_datetime(incident_report.get('date_time', ''))}.")
        body_parts.append("")
        
        # Incident Summary
        body_parts.append("**Incident Summary:**")
        body_parts.append(f"- Type: {incident_report.get('incident_type', 'Unknown')}")
        body_parts.append(f"- Location: {incident_report.get('location', 'Unknown')}")
        body_parts.append(f"- Description: {incident_report.get('description', 'No description available')}")
        body_parts.append("")
        
        # Immediate Actions
        body_parts.append("**Immediate Actions Taken:**")
        body_parts.append(incident_report.get('immediate_actions', 'Standard support protocol initiated'))
        body_parts.append("")
        
        # Policy Concerns
        if analysis.get("violations"):
            body_parts.append("**Policy Concerns Identified:**")
            for violation in analysis["violations"]:
                body_parts.append(f"- {violation.get('policy_section', 'Policy')}: {violation.get('description', '')}")
            body_parts.append("")
        
        # Required Actions
        body_parts.append("**Required Follow-up Actions:**")
        for violation in analysis.get("violations", []):
            if violation.get("required_action"):
                body_parts.append(f"- {violation['required_action']}")
        
        # Risk Assessment
        if incident_report.get("risk_assessment_needed"):
            body_parts.append(f"- {incident_report.get('risk_assessment_type', 'Risk assessment')} required")
        body_parts.append("")
        
        # Next Steps
        body_parts.append("**Agreed Next Steps:**")
        body_parts.append(incident_report.get('agreed_next_steps', 'To be determined'))
        body_parts.append("")
        
        # Closing
        body_parts.append("Please review the attached incident report for full details. If you have any questions or require additional information, please contact me immediately.")
        body_parts.append("")
        body_parts.append("Best regards,")
        body_parts.append("Emma Care Coordination Team")
        
        return "\n".join(body_parts)
    
    def _format_datetime(self, datetime_str: str) -> str:
        """Format datetime string for email"""
        try:
            dt = datetime.fromisoformat(datetime_str)
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return datetime_str or "Unknown time"
    
    async def regenerate_with_feedback(self, original: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """Regenerate email with user feedback"""
        try:
            prompt = f"""
            Original email:
            {json.dumps(original, indent=2)}
            
            User feedback:
            {feedback}
            
            Generate an updated email incorporating the feedback.
            Maintain professionalism and all required information.
            """
            
            if self.ai_provider == "openai":
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": "Update the email based on user feedback while maintaining professional standards."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            
            elif self.ai_provider == "claude":
                response = self.client.messages.create(
                    model=settings.claude_model,
                    max_tokens=settings.claude_max_tokens,
                    system="Update the email based on user feedback while maintaining professional standards. Return valid JSON only.",
                    messages=[{"role": "user", "content": prompt}]
                )
                return json.loads(response.content[0].text)
            
            elif self.ai_provider == "gemini":
                prompt = f"""Update the email based on user feedback while maintaining professional standards.
                {prompt}
                
                Return only valid JSON, no additional text or markdown.
                """
                response = self.client.generate_content(prompt)
                json_str = response.text.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
                return json.loads(json_str.strip())
            
        except Exception as e:
            logger.error(f"Error regenerating email: {e}")
            return original
