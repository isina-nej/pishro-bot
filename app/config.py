from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Telegram Bot
    BOT_TOKEN: str = Field(..., description="Telegram Bot Token")
    WEBHOOK_URL: str | None = Field(None, description="Webhook URL for Telegram")
    
    # Database
    DATABASE_URL: str = Field(
        "postgresql+asyncpg://user:password@localhost:5432/investment_bot",
        description="PostgreSQL connection URL for async operations"
    )
    DATABASE_ECHO: bool = Field(False, description="Echo SQL queries")
    
    # Admin/Accountant Telegram IDs
    ADMIN_TELEGRAM_IDS: list[int] = Field(default_factory=list, description="List of admin Telegram IDs")
    ACCOUNTANT_TELEGRAM_IDS: list[int] = Field(default_factory=list, description="List of accountant Telegram IDs")
    
    # API
    API_HOST: str = Field("0.0.0.0", description="API host")
    API_PORT: int = Field(8000, description="API port")
    
    # Timezone
    TZ: str = Field("UTC", description="Timezone")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
