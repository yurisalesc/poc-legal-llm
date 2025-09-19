import os
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.models import QueryRequest, QueryResponse, TaskResponse
from app.services.document_processor import process_pdf_task
from app.services.query_service import query_legal_document_self_query

router = APIRouter()

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-lei/", status_code=202, response_model=TaskResponse)
async def upload_lei_pdf(file: UploadFile = File(...)):
    """
    Endpoint para upload e processamento assíncrono de PDFs de legislação.

    Este endpoint realiza várias validações e processamentos:
    1. Verifica se o arquivo é um PDF válido
    2. Valida o nome do arquivo
    3. Salva o arquivo temporariamente
    4. Inicia processamento assíncrono via Celery

    Args:
        file (UploadFile): Arquivo PDF da lei/decreto a ser processado

    Returns:
        TaskResponse: Resposta contendo ID da tarefa para acompanhamento

    Raises:
        HTTPException: 
            - 400 se o arquivo não for PDF
            - 400 se o arquivo não tiver nome válido
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Tipo de arquivo inválido. Apenas PDFs são aceitos."
        )

    if not file.filename:
        raise HTTPException(
            status_code=400, detail="O arquivo enviado não possui um nome válido."
        )
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    task = process_pdf_task.delay(file_path)

    return TaskResponse(
        message="Arquivo recebido. O processamento foi iniciado em segundo plano.",
        task_id=task.id,
    )


@router.post("/consultar-lei/", response_model=QueryResponse)
async def consultar_lei(request: QueryRequest):
    """
    Endpoint para consulta de legislação usando processamento de linguagem natural.

    Este endpoint permite consultas em linguagem natural sobre a legislação e:
    1. Valida se a pergunta não está vazia
    2. Processa a pergunta usando o serviço de consulta
    3. Retorna resposta formatada com fontes consultadas

    O processamento utiliza:
    - Busca semântica em banco vetorial
    - Modelo de linguagem para interpretação
    - Recuperação de contexto relevante

    Args:
        request (QueryRequest): Objeto contendo a pergunta do usuário

    Returns:
        QueryResponse: Resposta processada e lista de fontes consultadas

    Raises:
        HTTPException: 
            - 400 se a pergunta estiver vazia
            - 500 se houver erro no processamento
    """
    if not request.question:
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

    try:
        response = query_legal_document_self_query(request.question)
        return QueryResponse(**response)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ocorreu um erro ao processar sua consulta: {str(e)}",
        )


@router.get("/health")
def health_check():
    """
    Endpoint para verificação de saúde da API.

    Retorna status simples para confirmar que a API está operacional.
    Útil para monitoramento e health checks de infraestrutura.

    Returns:
        dict: Status atual da API
    """
    return {"status": "API online"}
