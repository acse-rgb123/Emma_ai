import os
import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class ProviderManager:
    """Manages AI provider switching and configuration"""
    
    _instance = None
    _current_provider = None
    _providers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProviderManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._current_provider = os.getenv("AI_PROVIDER", "openai")
        self._load_providers()
    
    def _load_providers(self):
        """Load all configured providers"""
        self._providers = {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": "gpt-4",
                "available": bool(os.getenv("OPENAI_API_KEY"))
            },
            "claude": {
                "api_key": os.getenv("CLAUDE_API_KEY"),
                "model": "claude-3-opus-20240229",
                "available": bool(os.getenv("CLAUDE_API_KEY"))
            },
            "gemini": {
                "api_key": os.getenv("GEMINI_API_KEY"),
                "model": "gemini-pro",
                "available": bool(os.getenv("GEMINI_API_KEY"))
            }
        }
    
    def get_current_provider(self) -> str:
        """Get current active provider"""
        return self._current_provider
    
    def get_current_api_key(self) -> Optional[str]:
        """Get API key for current provider"""
        return self._providers.get(self._current_provider, {}).get("api_key")
    
    def get_current_model(self) -> str:
        """Get model for current provider"""
        return self._providers.get(self._current_provider, {}).get("model", "")
    
    def switch_provider(self, provider: str) -> Dict[str, Any]:
        """Switch to a different provider"""
        if provider not in self._providers:
            raise ValueError(f"Unknown provider: {provider}")
        
        if not self._providers[provider]["available"]:
            raise ValueError(f"Provider {provider} is not configured")
        
        self._current_provider = provider
        os.environ["AI_PROVIDER"] = provider
        
        logger.info(f"Switched to provider: {provider}")
        
        return {
            "active_provider": provider,
            "available_providers": self.get_available_providers()
        }
    
    def get_available_providers(self) -> Dict[str, bool]:
        """Get all available providers"""
        return {
            provider: info["available"] 
            for provider, info in self._providers.items()
        }
    
    def update_api_key(self, provider: str, api_key: str):
        """Update API key for a provider"""
        if provider in self._providers:
            self._providers[provider]["api_key"] = api_key
            self._providers[provider]["available"] = bool(api_key)
            
            # Update environment variable
            env_key = f"{provider.upper()}_API_KEY"
            if api_key:
                os.environ[env_key] = api_key
            elif env_key in os.environ:
                del os.environ[env_key]

# Global instance
provider_manager = ProviderManager()
