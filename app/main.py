import os
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.tasks import process_pdf_task

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="API de Análise de Leis com LLM",
    description="Faça upload de PDFs de leis e consulte qual está em vigor.",
    version="0.1.0",
)


class QueryRequest(BaseModel):
    question: str


@app.post("/upload-lei/", status_code=202)
async def upload_lei_pdf(file: UploadFile = File(...)):
    """
    Endpoint para fazer upload de um arquivo PDF de uma lei.
    O processamento é feito em segundo plano.
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

    return {
        "message": "Arquivo recebido. O processamento foi iniciado em segundo plano.",
        "task_id": task.id,
    }


@app.post("/consultar-lei/")
async def consultar_lei(request: QueryRequest):
    """
    Endpoint para consultar qual lei está em vigor sobre um determinado tema.
    """
    if not request.question:
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

    from app.processing import query_legal_document

    try:
        response = query_legal_document(request.question)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ocorreu um erro ao processar sua consulta: {str(e)}",
        )


@app.get("/")
def health_check():
    return {"status": "API online"}
