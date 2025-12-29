from pydantic_settings import BaseSettings
from functools import lru_cache
import os
import sys


from dotenv import load_dotenv
load_dotenv()

API_VERSION = os.getenv("API_VERSION", "v1")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
ENV = os.getenv("ENV", "dev")
API_TITLE = os.getenv("API_TITLE", "Nitifications Service API")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@courtmate.com")
FROM_NAME = os.getenv("FROM_NAME", "CourtMate")


# Log all environment variables and warn if any are missing, but do not exit
def log_env_vars():
    """Log all relevant environment variables and warn if any are missing"""
    required_vars = {
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_SERVICE_ROLE_KEY": SUPABASE_SERVICE_ROLE_KEY,
        "SUPABASE_ANON_KEY": SUPABASE_ANON_KEY,
        "BREVO_API_KEY": BREVO_API_KEY,
    }
    print("\n--- Notification Service Environment Variables ---")
    for key, value in required_vars.items():
        print(f"{key}: {'<set>' if value else '<MISSING>'}")
    print("------------------------------------------------\n")
    missing = [key for key, value in required_vars.items() if not value]
    if missing:
        print(f"⚠️  WARNING: Missing environment variables: {', '.join(missing)}")
        print("The service will start, but may not function correctly until all are set.")

log_env_vars()



class Settings(BaseSettings):
    """Application settings"""
    
    # Supabase configuration
    supabase_url: str = SUPABASE_URL
    supabase_key: str = SUPABASE_SERVICE_ROLE_KEY
    
    # API configuration
    api_title: str = API_TITLE
    api_description: str = "Notifications Service handling user notifications and alerts."     
    
    api_version: str = API_VERSION
    
    env: str = ENV
    
    # Email configuration (Brevo)
    brevo_api_key: str = BREVO_API_KEY
    from_email: str = FROM_EMAIL
    from_name: str = FROM_NAME
    
    # CORS settings
    cors_origins: list[str] = [
        "http://localhost",
        "http://localhost:3000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
