from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ChatBot RAG"
    debug: bool = False

    database_url: str

    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "gemma3"

    cors_origins: list[str] = ["http://localhost:3000"]

    # AWS — opcional: se não definido, boto3 usa IAM profile automaticamente
    aws_region: str = "us-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
