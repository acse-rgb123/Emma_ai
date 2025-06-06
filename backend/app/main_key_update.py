
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
        
        # Update multi_settings
        from app.multi_provider_config import multi_settings
        multi_settings.openai_api_key = request.get("openai_key")
        multi_settings.claude_api_key = request.get("claude_key")
        multi_settings.gemini_api_key = request.get("gemini_key")
        
        # Reinitialize services
        global policy_analyzer, report_generator, email_generator
        policy_analyzer = PolicyAnalyzer()
        report_generator = ReportGenerator()
        email_generator = EmailGenerator()
        
        return {
            "status": "success",
            "message": "API keys updated successfully",
            "available_providers": multi_settings.get_available_providers()
        }
        
    except Exception as e:
        logger.error(f"Error updating API keys: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
