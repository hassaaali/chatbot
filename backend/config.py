import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    MAX_RETRIEVAL_RESULTS = int(os.getenv("MAX_RETRIEVAL_RESULTS", "5"))
    
    # Legal-specific LLM configuration
    LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/Llama-3.1-70B-Instruct-Turbo")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4000"))
    LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))
    
    @classmethod
    def validate(cls):
        if not cls.TOGETHER_API_KEY:
            raise RuntimeError("TOGETHER_API_KEY not set in environment variables")
        return True