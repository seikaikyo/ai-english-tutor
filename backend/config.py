import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = os.environ.get('ANTHROPIC_API_KEY', '')
    model: str = 'claude-sonnet-4-20250514'
    max_tokens: int = 300
    cors_origins: list[str] = [
        'http://localhost:5172',
        'http://127.0.0.1:5172',
    ]

    class Config:
        env_file = '.env'


settings = Settings()
