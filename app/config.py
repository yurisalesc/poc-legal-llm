import os

from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

CHROMA_PERSIST_DIRECTORY = "chroma_db"
CHROMA_COLLECTION_NAME = "leis_decretos"
