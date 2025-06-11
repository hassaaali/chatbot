import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    together_api_key: str = ""
    google_credentials_path: str = "credentials.json"
    chroma_db_path: str = "./chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_retrieval_results: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()