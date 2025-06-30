import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Together AI API Configuration
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
    TOGETHER_API_URL = os.getenv("TOGETHER_API_URL", "https://api.together.xyz/v1/chat/completions")
    
    # Legal-specific model configuration - Optimized for legal reasoning
    LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/Llama-2-70b-chat-hf")  # Best for legal analysis
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))  # Low temperature for precise legal analysis
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "3000"))  # Increased for detailed legal responses
    LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))
    
    # Vector Store Configuration
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Document Processing - Optimized for legal documents
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))  # Larger chunks for legal context
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))  # More overlap for legal continuity
    MAX_RETRIEVAL_RESULTS = int(os.getenv("MAX_RETRIEVAL_RESULTS", "4"))  # More context for legal analysis
    
    # Memory optimization settings
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "3"))  # Reduced for 70B model
    
    # Together AI specific settings - Optimized for larger model
    TOGETHER_REQUEST_TIMEOUT = int(os.getenv("TOGETHER_REQUEST_TIMEOUT", "180"))  # Longer timeout for 70B
    TOGETHER_MAX_RETRIES = int(os.getenv("TOGETHER_MAX_RETRIES", "3"))
    
    @classmethod
    def validate(cls):
        if not cls.TOGETHER_API_KEY:
            raise RuntimeError("TOGETHER_API_KEY not set in environment variables")
        return True
    
    @classmethod
    def get_recommended_legal_models(cls):
        """Get models ranked by legal analysis capability"""
        return [
            {
                "model": "meta-llama/Llama-2-70b-chat-hf",
                "name": "Llama 2 70B (Recommended)",
                "description": "Best for complex legal reasoning and comprehensive analysis",
                "use_case": "Complex contracts, legal research, detailed analysis",
                "performance": "Highest",
                "speed": "Slower"
            },
            {
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "name": "Mixtral 8x7B",
                "description": "Excellent for legal document analysis with good speed",
                "use_case": "Contract review, legal document analysis",
                "performance": "High",
                "speed": "Fast"
            },
            {
                "model": "meta-llama/Llama-2-13b-chat-hf",
                "name": "Llama 2 13B",
                "description": "Balanced performance for most legal tasks",
                "use_case": "General legal Q&A, document review",
                "performance": "Good",
                "speed": "Fast"
            },
            {
                "model": "mistralai/Mistral-7B-Instruct-v0.1",
                "name": "Mistral 7B",
                "description": "Good instruction following for structured legal tasks",
                "use_case": "Specific legal instructions, quick analysis",
                "performance": "Good",
                "speed": "Very Fast"
            },
            {
                "model": "codellama/CodeLlama-13b-Instruct-hf",
                "name": "CodeLlama 13B",
                "description": "Excellent for legal logic and structured reasoning",
                "use_case": "Contract logic, legal procedures, compliance",
                "performance": "Good",
                "speed": "Fast"
            }
        ]