from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Try both locations: project root (local dev) and current dir (Docker/tests)
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    sync_database_url: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"
    pinecone_api_key: str
    pinecone_index_name: str = "post-care-agent"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    gemini_api_key: str
    sendgrid_api_key: str
    sendgrid_from_email: str
    alert_recipient_email: str


settings = Settings()
