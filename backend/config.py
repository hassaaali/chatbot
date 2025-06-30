import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Hugging Face API Configuration
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    HUGGINGFACE_API_URL = os.getenv("HUGGINGFACE_API_URL", "https://api-inference.huggingface.co/models")
    
    # Legal-specific model configuration - using smaller models for memory efficiency
    LLM_MODEL = os.getenv("LLM_MODEL", "microsoft/DialoGPT-medium")  # Changed to medium for memory
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))  # Reduced from 2000
    LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))
    
    # Vector Store Configuration - optimized for memory
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")  # Lightweight model
    
    # Document Processing - reduced for memory efficiency
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "300"))  # Reduced from 500
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))  # Reduced from 100
    MAX_RETRIEVAL_RESULTS = int(os.getenv("MAX_RETRIEVAL_RESULTS", "2"))  # Reduced from 3
    
    # Memory optimization settings - more aggressive
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "5242880"))  # Reduced to 5MB from 10MB
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "2"))  # Reduced from 5
    
    # Hugging Face specific settings
    HF_REQUEST_TIMEOUT = int(os.getenv("HF_REQUEST_TIMEOUT", "60"))  # Reduced timeout
    HF_MAX_RETRIES = int(os.getenv("HF_MAX_RETRIES", "2"))  # Reduced retries
    
    @classmethod
    def validate(cls):
        if not cls.HUGGINGFACE_API_KEY:
            raise RuntimeError("HUGGINGFACE_API_KEY not set in environment variables")
        return True