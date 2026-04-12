from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "dev-secret-key"
    export_key: str = "dev-export-key"
    tavily_api_key: str = ""
    supabase_url: str = ""
    supabase_key: str = ""
    cookie_name: str = "lions_feed_uid"
    cookie_max_age: int = 60 * 60 * 24 * 30  # 30 days

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
