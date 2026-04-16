from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    tfe_address: str = "https://app.terraform.io"
    tfe_token: Optional[str] = None
    tfe_skip_tls_verify: bool = False
    
    log_level: str = "INFO"
    log_format: str = "text"
    
    transport_mode: str = "stdio"
    transport_host: str = "127.0.0.1"
    transport_port: int = 8080
    mcp_endpoint: str = "/mcp"
    
    mcp_allowed_origins: List[str] = []
    mcp_cors_mode: str = "strict"
    
    enable_tf_operations: bool = False
    
    # Tool filtering
    toolsets: str = "all"
    tools: str = ""

settings = Settings()
