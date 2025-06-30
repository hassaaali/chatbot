import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Together AI API Configuration
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
    TOGETHER_API_URL = os.getenv("TOGETHER_API_URL", "https://api.together.xyz/v1/chat/completions")
    
    # Legal-specific model configuration
    LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/Llama-2-7b-chat-hf")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))
    
    # Vector Store Configuration
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Document Processing
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
    MAX_RETRIEVAL_RESULTS = int(os.getenv("MAX_RETRIEVAL_RESULTS", "3"))
    
    # Memory optimization settings
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "5"))
    
    # Together AI specific settings
    TOGETHER_REQUEST_TIMEOUT = int(os.getenv("TOGETHER_REQUEST_TIMEOUT", "120"))
    TOGETHER_MAX_RETRIES = int(os.getenv("TOGETHER_MAX_RETRIES", "3"))
    
    @classmethod
    def validate(cls):
        if not cls.TOGETHER_API_KEY:
            raise RuntimeError("TOGETHER_API_KEY not set in environment variables")
        return True