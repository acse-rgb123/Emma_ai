import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    api_title: str = "Emma Incident Response System"
    api_version: str = "1.0.0"
    api_description: str = "AI-Enhanced Incident Response System for Social Care"
    
    # AI Provider Configuration
    ai_provider: str = os.getenv("AI_PROVIDER", "openai")
    api_key: Optional[str] = os.getenv("API_KEY")
    
    # OpenAI specific
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000
    
    # Claude specific
    claude_model: str = "claude-3-opus-20240229"
    claude_max_tokens: int = 2000
    
    # Gemini specific
    gemini_model: str = "gemini-pro"
    
    # CORS Configuration
    cors_origins: list = ["*"]
    
    # Logging Configuration
    log_level: str = "INFO"
    
    # Data paths
    policies_path: str = "app/data/policies.txt"
    template_path: str = "app/data/incident_template.json"
    
    # Email defaults
    default_supervisor_email: str = "supervisor@emmacare.com"
    default_risk_assessor_email: str = "riskassessment@emmacare.com"
    default_family_contact_email: str = "family.contact@emmacare.com"
    
    # Feature flags
    enable_ai_fallback: bool = True
    enable_email_notifications: bool = False
    enable_audit_logging: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
