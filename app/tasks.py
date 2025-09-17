import os

from celery import Celery # type: ignore

from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from app.processing import process_pdf_and_store

celery_app = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


@celery_app.task
def process_pdf_task(file_path: str):
    try:
        process_pdf_and_store(file_path)
        os.remove(file_path)
        return {
            "status": "Sucesso",
            "message": f"Arquivo {os.path.basename(file_path)} processado.",
        }
    except Exception as e:
        return {"status": "Erro", "message": str(e)}
