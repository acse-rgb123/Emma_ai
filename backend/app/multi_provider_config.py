import os
from typing import Optional, Dict
from pydantic_settings import BaseSettings

class MultiProviderSettings(BaseSettings):
    # API Keys for all providers
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    claude_api_key: Optional[str] = os.getenv("CLAUDE_API_KEY")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Current active provider
    active_provider: str = os.getenv("AI_PROVIDER", "openai")
    
    # Model configurations
    openai_model: str = "gpt-4"
    claude_model: str = "claude-3-opus-20240229"
    gemini_model: str = "gemini-pro"
    
    # Get active API key
    def get_active_api_key(self) -> Optional[str]:
        if self.active_provider == "openai":
            return self.openai_api_key
        elif self.active_provider == "claude":
            return self.claude_api_key
        elif self.active_provider == "gemini":
            return self.gemini_api_key
        return None
    
    # Check which providers are configured
    def get_available_providers(self) -> Dict[str, bool]:
        return {
            "openai": bool(self.openai_api_key),
            "claude": bool(self.claude_api_key),
            "gemini": bool(self.gemini_api_key)
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = False

multi_settings = MultiProviderSettings()
