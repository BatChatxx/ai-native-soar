"""
LLM Configuration for AI-Native SOAR

Configuration for local LLM integration using Qwen 3.5 9B model.
"""
import os
from typing import Optional
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM Configuration Model"""
    
    # API Configuration
    api_key: str = Field(..., description="API key for LLM service")
    base_url: str = Field(default="http://127.0.0.1:56987", 
                          description="Base URL for LLM API")
    model: str = Field(default="qwen/qwen3.5-9b",
                       description="Model name/identifier")
    api_version: str = Field(default="1",
                             description="API version")
    
    # Connection Settings
    timeout: int = Field(default=120,
                         description="Request timeout in seconds")
    max_retries: int = Field(default=3,
                              description="Maximum retry attempts")
    
    # Safety Settings
    max_tokens: int = Field(default=4096,
                            description="Maximum tokens per response")
    temperature: float = Field(default=0.7,
                               description="Temperature for creative responses")
    
    class Config:
        env_file = "../../../.env"
        env_file_encoding = "utf-8"
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Create LLMConfig from environment variables"""
        return cls(
            api_key=os.getenv("LLM_API_KEY", ""),
            base_url=os.getenv("LLM_BASE_URL", "http://127.0.0.1:56987"),
            model=os.getenv("LLM_MODEL", "qwen/qwen3.5-9b"),
            api_version=os.getenv("LLM_API_VERSION", "1"),
            timeout=int(os.getenv("LLM_TIMEOUT", "120")),
            max_retries=int(os.getenv("LLM_MAX_RETRIES", "3")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        )
    
    def to_dict(self) -> dict:
        """Export configuration as dictionary"""
        return self.model_dump(exclude_defaults=True)
    
    @property
    def endpoint(self) -> str:
        """Get full API endpoint for chat completions"""
        return f"{self.base_url.rstrip('/')}/chat/completions"
    
    @property
    def models_endpoint(self) -> str:
        """Get models endpoint"""
        return f"{self.base_url.rstrip('/')}/models"


class LLMConfigError(Exception):
    """Exception raised for LLM configuration errors"""
    pass


def get_llm_config() -> LLMConfig:
    """Get LLM configuration from environment"""
    try:
        return LLMConfig.from_env()
    except Exception as e:
        LLMConfigError(f"Failed to load LLM configuration: {e}")


# Global configuration instance
_llm_config: Optional[LLMConfig] = None


def get_llm_config_cached() -> LLMConfig:
    """Get cached LLM configuration (singleton pattern)"""
    global _llm_config
    if _llm_config is None:
        _llm_config = get_llm_config()
    return _llm_config


def reset_llm_config() -> None:
    """Reset cached configuration (useful for testing)"""
    global _llm_config
    _llm_config = None
