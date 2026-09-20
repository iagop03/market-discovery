from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    github_token: str = ""
    database_url: str = "sqlite:///./market_discovery.db"
    webhook_url: str = ""
