from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "cliniq_cases"

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "cliniq-images"
    minio_secure: bool = False

    # Local LLM (Ollama or any OpenAI-compatible server)
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "llama3.2:1b"
    llm_api_key: str = "ollama"   # Ollama ignores this but openai SDK requires a non-empty value

    # Paths
    scaler_path: str = "../radiomic_scaler.pkl"
    segmentation_model_path: str = "models/segmentation"

    class Config:
        env_file = ".env"


settings = Settings()
