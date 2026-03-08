from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr



class Settings(BaseSettings):
    database_url: str = "sqlite:///./chatbot.db"
    GROK_API_KEY: str
    SHORT_TERM_MEMORY: int = 3     # keep the last 3 messages as recent memory
    SUMMARY_TRIGGER: int = 6       # start summarizing when messages >= 6
    ACCESS_TOKEN_EXPIRED_MINUTES: int =30
    SECRET_KEY: SecretStr
    ALGORITHIM: str = "HS256"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()