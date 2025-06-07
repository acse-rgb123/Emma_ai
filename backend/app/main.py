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

# OpenAI import
from openai import OpenAI

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


@app.post("/api/test_openai")
async def test_openai_connection(request: Dict[str, Any]):
    """Test OpenAI API connection"""
    try:
        api_key = request.get("api_key")
        if not api_key:
            return {
                "success": False,
                "error": "API key is required"
            }
        
        if not api_key.startswith("sk-"):
            return {
                "success": False,
                "error": "Invalid API key format. OpenAI API keys start with 'sk-'"
            }
        
        # Test the API key with a simple request
        client = OpenAI(api_key=api_key)
        
        # Make a minimal test request with timeout
        logger.info("Testing OpenAI API connection...")
        
        # Try different approach for testing
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5,
                timeout=10.0  # 10 second timeout
            )
        except Exception as chat_error:
            logger.warning(f"Chat completion failed, trying models list: {chat_error}")
            # Fallback: try listing models (simpler API call)
            try:
                models = client.models.list()
                logger.info("Models list successful - API key is valid")
                return {
                    "success": True,
                    "message": "Connection successful (verified via models list)",
                    "model": "gpt-4o-mini"
                }
            except Exception as models_error:
                logger.error(f"Both tests failed - chat: {chat_error}, models: {models_error}")
                raise chat_error  # Raise original error
        
        logger.info("OpenAI connection test successful")
        return {
            "success": True,
            "message": "Connection successful",
            "model": "gpt-4o-mini",
            "usage": response.usage.total_tokens if response.usage else 0
        }
        
    except ImportError:
        logger.error("OpenAI package not installed")
        return {
            "success": False,
            "error": "OpenAI package is not installed. Please install it with: pip install openai"
        }
    except Exception as e:
        error_str = str(e)
        logger.error(f"OpenAI connection test failed: {error_str}")
        
        # Handle common error types
        if "401" in error_str or "Unauthorized" in error_str:
            return {
                "success": False,
                "error": "Invalid API key. Please check your OpenAI API key."
            }
        elif "403" in error_str or "Forbidden" in error_str:
            return {
                "success": False,
                "error": "API key doesn't have permission. Please check your OpenAI account."
            }
        elif "429" in error_str or "rate_limit" in error_str.lower():
            return {
                "success": False,
                "error": "Rate limit exceeded. Please try again later."
            }
        elif "timeout" in error_str.lower() or "connection" in error_str.lower():
            return {
                "success": False,
                "error": "Connection timeout. Please check your internet connection and try again."
            }
        elif "proxy" in error_str.lower():
            return {
                "success": False,
                "error": "Proxy error. Please check your network configuration."
            }
        else:
            return {
                "success": False,
                "error": f"Connection failed: {error_str}"
            }

@app.post("/api/update_keys")
async def update_api_keys(request: Dict[str, Any]):
    """Update OpenAI API key"""
    try:
        openai_key = request.get("openai_key")
        if not openai_key:
            raise ValueError("OpenAI API key is required")
        
        # Update environment variable
        os.environ["OPENAI_API_KEY"] = openai_key
        
        # Update settings
        from app.config import settings
        settings.openai_api_key = openai_key
        
        # Reinitialize services
        global policy_analyzer, report_generator, email_generator, report_updater, email_updater
        try:
            policy_analyzer = PolicyAnalyzer()
            report_generator = ReportGenerator()
            email_generator = EmailGenerator()
            report_updater = ReportUpdater()
            email_updater = EmailUpdater()
        except Exception as e:
            logger.error(f"Error reinitializing services: {str(e)}")
            raise ValueError(f"Failed to initialize services with new API key: {str(e)}")
        
        return {
            "success": True,
            "message": "OpenAI API key updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating API key: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "status": "healthy",
        "ai_provider": "openai",
        "ai_configured": openai_configured,
        "services": {
            "analyzer": "active" if openai_configured else "not_configured",
            "report_generator": "active" if openai_configured else "not_configured",
            "email_generator": "active" if openai_configured else "not_configured"
        },
        "debug_info": {
            "active_sessions": len(conversation_contexts),
            "openai_key_configured": openai_configured,
            "openai_key_length": len(os.getenv("OPENAI_API_KEY", "")) if openai_configured else 0
        }
    }

@app.post("/clear_context")
async def clear_context(request: Dict[str, Any]):
    """Clear conversation context for a session"""
    session_id = request.get("session_id", "default")
    if session_id in conversation_contexts:
        del conversation_contexts[session_id]
    return {"status": "context cleared"}
