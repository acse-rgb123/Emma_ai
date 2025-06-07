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

logger = logging.getLogger(__name__)

class EmailGenerator:
    def __init__(self):
        if not OpenAI:
            raise ImportError("OpenAI package is required but not installed")
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required but not provided")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        
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
        """Use OpenAI to generate email"""
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
            
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                max_tokens=settings.openai_max_tokens,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": "You are a social care coordinator drafting incident notification emails. Be clear, professional, and action-oriented."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"OpenAI email generation failed: {e}")
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
        """Regenerate email with user feedback using OpenAI"""
        try:
            prompt = f"""
            Original email:
            {json.dumps(original, indent=2)}
            
            User feedback:
            {feedback}
            
            Generate an updated email incorporating the feedback.
            Maintain professionalism and all required information.
            """
            
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                max_tokens=settings.openai_max_tokens,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": "Update the email based on user feedback while maintaining professional standards."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error regenerating email with OpenAI: {e}")
            return original
