from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str
    
    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    # Token expiration time in minutes (60 hours)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3600
    
    # Email settings
    SMTP_HOST: str
    SMTP_PORT: int
    GMAIL_EMAIL: str
    GMAIL_PASSWORD: str

    class Config:
        env_file = ".env"

settings = Settings()
