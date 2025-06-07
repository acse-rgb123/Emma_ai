# Standard library imports
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Third-party imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Local application imports
from app.models import TranscriptRequest, IncidentResponse
from app.services.analyzer import PolicyAnalyzer
from app.services.email_generator import EmailGenerator
from app.services.email_updater import EmailUpdater
from app.services.report_generator import ReportGenerator
from app.services.report_updater import ReportUpdater

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
report_updater = ReportUpdater()
email_updater = EmailUpdater()

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
    Update existing analysis with new information using LLM-based approach
    """
    try:
        session_id = request.get("session_id", "default")
        new_info = request.get("new_information", "")
        update_type = request.get("update_type", "incident_report")  # Default to incident_report
        
        context = conversation_contexts.get(session_id, {})
        if not context.get("last_analysis"):
            raise ValueError("No previous analysis found. Please analyze a transcript first.")
        
        last_analysis = context["last_analysis"]
        
        logger.info(f"Updating {update_type} with new information: {new_info[:100]}...")
        
        # Create context for the updaters
        update_context = {
            "original_transcript": last_analysis["transcript"],
            "original_analysis": last_analysis["analysis"],
            "session_id": session_id
        }
        
        # Update based on type using LLM services
        if update_type == "incident_report":
            # Validate original report exists
            if not last_analysis.get("incident_report"):
                raise ValueError("No incident report found to update")
            
            logger.info(f"Updating incident report with: '{new_info[:100]}{'...' if len(new_info) > 100 else ''}'")
            
            # Log current report data for debugging
            current_report = last_analysis["incident_report"]
            logger.debug(f"Current report data being sent to LLM: {json.dumps(current_report, indent=2)}")
            
            # Update incident report using LLM
            updated_report = await report_updater.update_report(
                original_report=current_report,
                update_info=new_info,
                context=update_context
            )
            
            # Verify update was successful
            if updated_report == last_analysis["incident_report"]:
                logger.warning("No changes detected in updated report")
            else:
                logger.info("Incident report successfully updated")
                
            last_analysis["incident_report"] = updated_report
            incident_report = updated_report
            email_draft = last_analysis["email_draft"]  # Keep original email
            
        elif update_type == "email_update":
            # Validate original email exists
            if not last_analysis.get("email_draft"):
                raise ValueError("No email draft found to update")
            
            logger.info(f"Updating email draft with: '{new_info[:100]}{'...' if len(new_info) > 100 else ''}'")
            
            # Log current email data for debugging
            current_email = last_analysis["email_draft"]
            logger.debug(f"Current email data being sent to LLM: {json.dumps(current_email, indent=2)}")
            
            # Update email using LLM
            updated_email = await email_updater.update_email(
                original_email=current_email,
                update_info=new_info,
                context=update_context
            )
            
            # Verify update was successful
            if updated_email == last_analysis["email_draft"]:
                logger.warning("No changes detected in updated email")
            else:
                logger.info("Email draft successfully updated")
                
            last_analysis["email_draft"] = updated_email
            email_draft = updated_email
            incident_report = last_analysis["incident_report"]  # Keep original report
            
        elif update_type == "transcript_update":
            # Handle transcript updates by re-analyzing with additional transcript content
            logger.info(f"Updating analysis with additional transcript: '{new_info[:100]}{'...' if len(new_info) > 100 else ''}'")
            
            # Combine original transcript with new transcript information
            combined_transcript = f"""
Original Transcript:
{last_analysis['transcript']}

Additional Transcript Information:
{new_info}
"""
            
            # Re-analyze with combined transcript
            analysis_result = await policy_analyzer.analyze(combined_transcript)
            
            # Generate new report and email based on updated analysis
            updated_report = await report_generator.generate_report(
                transcript=combined_transcript,
                analysis=analysis_result
            )
            
            updated_email = await email_generator.generate_email(
                incident_report=updated_report,
                analysis=analysis_result
            )
            
            # Update stored data
            last_analysis["transcript"] = combined_transcript
            last_analysis["analysis"] = analysis_result
            last_analysis["incident_report"] = updated_report
            last_analysis["email_draft"] = updated_email
            
            incident_report = updated_report
            email_draft = updated_email
            
        else:
            # Fallback to original method for backward compatibility
            logger.warning(f"Unknown update_type: {update_type}, using fallback")
            incident_report = last_analysis["incident_report"]
            email_draft = last_analysis["email_draft"]
        
        # Update context with timestamp
        last_analysis["last_update"] = datetime.now().isoformat()
        last_analysis["last_update_type"] = update_type
        last_analysis["last_update_info"] = new_info
        
        return {
            "status": "success",
            "update_type": update_type,
            "analysis_summary": last_analysis["analysis"].get("summary", ""),
            "incident_report": incident_report,
            "email_draft": email_draft,
            "policy_violations": last_analysis["analysis"].get("violations", []),
            "recommendations": last_analysis["analysis"].get("recommendations", [])
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
        global policy_analyzer, report_generator, email_generator, report_updater, email_updater
        policy_analyzer = PolicyAnalyzer()
        report_generator = ReportGenerator()
        email_generator = EmailGenerator()
        report_updater = ReportUpdater()
        email_updater = EmailUpdater()
        
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
