import os

from celery import Celery # type: ignore

from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from app.processing import process_pdf_and_store

celery_app = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


@celery_app.task
def process_pdf_task(file_path: str):
    """
    Tarefa Celery para processamento assíncrono de arquivos PDF.

    Esta tarefa:
    1. Processa o arquivo PDF utilizando o serviço de processamento
    2. Remove o arquivo temporário após processamento
    3. Retorna resultado indicando sucesso ou falha

    O processamento é feito de forma assíncrona para:
    - Não bloquear a API durante uploads
    - Permitir processamento em paralelo
    - Gerenciar falhas de forma adequada

    Args:
        file_path (str): Caminho para o arquivo PDF temporário

    Returns:
        dict: Dicionário contendo:
            - status: "Sucesso" ou "Erro"
            - message: Mensagem descritiva do resultado
    """
    try:
        process_pdf_and_store(file_path)
        os.remove(file_path)
        return {
            "status": "Sucesso",
            "message": f"Arquivo {os.path.basename(file_path)} processado.",
        }
    except Exception as e:
        return {"status": "Erro", "message": str(e)}
