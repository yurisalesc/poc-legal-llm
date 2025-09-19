import os

from fastapi import FastAPI

from app.routes import api
from app.utils.helpers import ensure_directory_exists

UPLOAD_DIR = "temp_uploads"
ensure_directory_exists(UPLOAD_DIR)

# Configure Google API Key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

app = FastAPI(
    title="API de Análise de Leis com LLM",
    description="Faça upload de PDFs de leis e consulte qual está em vigor.",
    version="0.1.0",
)

app.include_router(api.router, prefix="/api")
