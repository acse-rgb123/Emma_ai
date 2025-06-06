
# Add these imports at the top
from app.multi_provider_config import multi_settings

# Add these endpoints
@app.post("/switch_provider/{provider}")
async def switch_ai_provider(provider: str):
    """Switch between AI providers"""
    try:
        available = multi_settings.get_available_providers()
        
        if provider not in available:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
        
        if not available[provider]:
            raise HTTPException(status_code=400, detail=f"Provider {provider} is not configured. Please add API key.")
        
        # Update the active provider
        multi_settings.active_provider = provider
        os.environ["AI_PROVIDER"] = provider
        
        # Reinitialize services
        global policy_analyzer, report_generator, email_generator
        policy_analyzer = PolicyAnalyzer()
        report_generator = ReportGenerator()
        email_generator = EmailGenerator()
        
        logger.info(f"Switched to provider: {provider}")
        
        return {
            "status": "success",
            "active_provider": provider,
            "available_providers": available
        }
        
    except Exception as e:
        logger.error(f"Error switching provider: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/provider_status")
async def get_provider_status():
    """Get current provider status and available providers"""
    return {
        "active_provider": multi_settings.active_provider,
        "available_providers": multi_settings.get_available_providers(),
        "models": {
            "openai": multi_settings.openai_model,
            "claude": multi_settings.claude_model,
            "gemini": multi_settings.gemini_model
        }
    }
