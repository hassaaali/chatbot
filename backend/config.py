import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
    GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    MAX_RETRIEVAL_RESULTS = int(os.getenv("MAX_RETRIEVAL_RESULTS", "5"))
    
    # Drive sync settings
    DRIVE_SYNC_INTERVAL_HOURS = int(os.getenv("DRIVE_SYNC_INTERVAL_HOURS", "24"))
    DEFAULT_DRIVE_FOLDER_ID = os.getenv("DEFAULT_DRIVE_FOLDER_ID")  # Optional: set a default folder
    
    @classmethod
    def validate(cls):
        if not cls.TOGETHER_API_KEY:
            raise RuntimeError("TOGETHER_API_KEY not set in environment variables")
        return True