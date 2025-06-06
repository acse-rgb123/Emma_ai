from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class TranscriptRequest(BaseModel):
    transcript: str = Field(..., description="The call/meeting transcript to analyze")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

class IncidentReport(BaseModel):
    date_time: datetime
    service_user_name: str
    location: str
    incident_type: str
    description: str
    immediate_actions: str
    first_aid_administered: bool
    emergency_services_contacted: bool
    who_was_notified: str
    witnesses: str
    agreed_next_steps: str
    risk_assessment_needed: bool
    risk_assessment_type: Optional[str] = None

class EmailDraft(BaseModel):
    to: List[str]
    cc: Optional[List[str]] = []
    subject: str
    body: str
    priority: str = "normal"
    attachments: Optional[List[str]] = []

class PolicyViolation(BaseModel):
    policy_section: str
    violation_type: str
    severity: str
    description: str
    required_action: str

class IncidentResponse(BaseModel):
    analysis_summary: str
    incident_report: Dict[str, Any]
    email_draft: Dict[str, Any]
    policy_violations: List[Dict[str, Any]]
    recommendations: List[str]
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
