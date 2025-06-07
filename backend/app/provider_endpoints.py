import logging
from typing import Dict, Any

from fastapi import HTTPException

from app.multi_provider_config import multi_settings
from app.services.analyzer import PolicyAnalyzer
from app.services.report_generator import ReportGenerator
from app.services.email_generator import EmailGenerator

logger = logging.getLogger(__name__)

async def switch_provider(provider: str):
    """Switch the active AI provider"""
    available = multi_settings.get_available_providers()
    
    if provider not in available:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
    
    if not available[provider]:
        raise HTTPException(status_code=400, detail=f"Provider {provider} is not configured")
    
    # Update the active provider
    multi_settings.active_provider = provider
    
    # Reinitialize services with new provider
    
    # These would need to be globals in main.py
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

async def get_provider_status():
    """Get current provider status"""
    return {
        "active_provider": multi_settings.active_provider,
        "available_providers": multi_settings.get_available_providers(),
        "models": {
            "openai": multi_settings.openai_model,
            "claude": multi_settings.claude_model,
            "gemini": multi_settings.gemini_model
        }
    }
