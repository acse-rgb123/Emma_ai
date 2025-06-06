from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import json
from typing import Dict, Any, Optional
import os
from datetime import datetime

from app.models import TranscriptRequest, IncidentResponse
from app.services.analyzer import PolicyAnalyzer
from app.services.report_generator import ReportGenerator
from app.services.email_generator import EmailGenerator

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Emma Incident Response System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
policy_analyzer = PolicyAnalyzer()
report_generator = ReportGenerator()
email_generator = EmailGenerator()

# Store conversation context
conversation_contexts = {}

@app.get("/")
async def root():
    return {"message": "Emma Incident Response System API", "status": "active"}

@app.post("/analyze", response_model=IncidentResponse)
async def analyze_transcript(request: TranscriptRequest):
    """
    Analyze transcript against policies and generate incident report
    """
    try:
        logger.info(f"Received transcript for analysis: {request.transcript[:100]}...")
        
        # Get or create conversation context
        session_id = request.metadata.get("session_id", "default")
        context = conversation_contexts.get(session_id, {})
        
        # Step 1: Analyze transcript against policies
        logger.info("Starting policy analysis...")
        analysis_result = await policy_analyzer.analyze(request.transcript)
        logger.info(f"Analysis complete: {json.dumps(analysis_result, indent=2)}")
        
        # Step 2: Generate incident report
        logger.info("Generating incident report...")
        incident_report = await report_generator.generate_report(
            transcript=request.transcript,
            analysis=analysis_result
        )
        logger.info(f"Incident report generated: {json.dumps(incident_report, indent=2)}")
        
        # Step 3: Generate email draft
        logger.info("Generating email draft...")
        email_draft = await email_generator.generate_email(
            incident_report=incident_report,
            analysis=analysis_result
        )
        logger.info(f"Email draft generated: {json.dumps(email_draft, indent=2)}")
        
        # Store in context
        context["last_analysis"] = {
            "transcript": request.transcript,
            "analysis": analysis_result,
            "incident_report": incident_report,
            "email_draft": email_draft,
            "timestamp": datetime.now().isoformat()
        }
        conversation_contexts[session_id] = context
        
        # Prepare response
        response = IncidentResponse(
            analysis_summary=analysis_result.get("summary", "Analysis completed successfully."),
            incident_report=incident_report,
            email_draft=email_draft,
            policy_violations=analysis_result.get("violations", []),
            recommendations=analysis_result.get("recommendations", []),
            confidence_score=analysis_result.get("confidence_score", 0.95)
        )
        
        logger.info("Response prepared successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error processing transcript: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing transcript: {str(e)}")

@app.post("/update_analysis")
async def update_analysis(request: Dict[str, Any]):
    """
    Update existing analysis with new information
    """
    try:
        session_id = request.get("session_id", "default")
        new_info = request.get("new_information", "")
        update_type = request.get("update_type", "general")
        
        context = conversation_contexts.get(session_id, {})
        if not context.get("last_analysis"):
            raise ValueError("No previous analysis found. Please analyze a transcript first.")
        
        last_analysis = context["last_analysis"]
        
        # Combine original transcript with new information
        updated_context = f"""
Original Transcript:
{last_analysis['transcript']}

Additional Information ({update_type}):
{new_info}
"""
        
        # Re-analyze with updated context
        logger.info(f"Updating analysis with new information: {new_info[:100]}...")
        
        analysis_result = await policy_analyzer.analyze(updated_context)
        
        # Update reports if needed
        if update_type in ["incident_details", "all"]:
            incident_report = await report_generator.generate_report(
                transcript=updated_context,
                analysis=analysis_result
            )
            last_analysis["incident_report"] = incident_report
        else:
            incident_report = last_analysis["incident_report"]
        
        if update_type in ["email_update", "all"]:
            email_draft = await email_generator.generate_email(
                incident_report=incident_report,
                analysis=analysis_result
            )
            last_analysis["email_draft"] = email_draft
        else:
            email_draft = last_analysis["email_draft"]
        
        # Update context
        last_analysis["analysis"] = analysis_result
        last_analysis["last_update"] = datetime.now().isoformat()
        
        return {
            "status": "success",
            "analysis_summary": analysis_result.get("summary", ""),
            "incident_report": incident_report,
            "email_draft": email_draft,
            "policy_violations": analysis_result.get("violations", []),
            "recommendations": analysis_result.get("recommendations", [])
        }
        
    except Exception as e:
        logger.error(f"Error updating analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/regenerate/{component}")
async def regenerate_component(component: str, request: Dict[str, Any]):
    """
    Regenerate a specific component with user feedback
    """
    try:
        logger.info(f"Regenerating {component} with feedback: {request.get('feedback', '')[:100]}...")
        
        if component == "report":
            result = await report_generator.regenerate_with_feedback(
                original=request.get("original"),
                feedback=request.get("feedback")
            )
        elif component == "email":
            result = await email_generator.regenerate_with_feedback(
                original=request.get("original"),
                feedback=request.get("feedback")
            )
        else:
            raise ValueError(f"Invalid component: {component}")
        
        logger.info(f"Regeneration complete for {component}")
        return {"result": result}
        
    except Exception as e:
        logger.error(f"Error regenerating {component}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error regenerating {component}: {str(e)}")


@app.post("/api/update_keys")
async def update_api_keys(request: Dict[str, Any]):
    """Update API keys from frontend configuration"""
    try:
        # Update environment variables
        if request.get("openai_key"):
            os.environ["OPENAI_API_KEY"] = request["openai_key"]
        if request.get("claude_key"):
            os.environ["CLAUDE_API_KEY"] = request["claude_key"]
        if request.get("gemini_key"):
            os.environ["GEMINI_API_KEY"] = request["gemini_key"]
        
        # Update multi_settings if available
        try:
            from app.multi_provider_config import multi_settings
            multi_settings.openai_api_key = request.get("openai_key")
            multi_settings.claude_api_key = request.get("claude_key")
            multi_settings.gemini_api_key = request.get("gemini_key")
        except ImportError:
            pass
        
        # Reinitialize services
        global policy_analyzer, report_generator, email_generator
        policy_analyzer = PolicyAnalyzer()
        report_generator = ReportGenerator()
        email_generator = EmailGenerator()
        
        return {
            "status": "success",
            "message": "API keys updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating API keys: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    ai_configured = bool(os.getenv("API_KEY"))
    return {
        "status": "healthy",
        "ai_provider": os.getenv("AI_PROVIDER", "openai"),
        "ai_configured": ai_configured,
        "services": {
            "analyzer": "active",
            "report_generator": "active",
            "email_generator": "active"
        },
        "debug_info": {
            "active_sessions": len(conversation_contexts),
            "ai_key_length": len(os.getenv("API_KEY", "")) if ai_configured else 0
        }
    }

@app.post("/clear_context")
async def clear_context(request: Dict[str, Any]):
    """Clear conversation context for a session"""
    session_id = request.get("session_id", "default")
    if session_id in conversation_contexts:
        del conversation_contexts[session_id]
    return {"status": "context cleared"}
