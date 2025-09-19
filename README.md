# Legal Document Analysis with LLM

Este é um sistema de análise de documentos legais que utiliza LLM (Large Language Model) para processar e consultar leis e decretos. O sistema permite carregar documentos PDF de legislação, processá-los e realizar consultas em linguagem natural sobre seu conteúdo.

## Funcionalidades

- Upload e processamento de documentos legais em PDF
- Extração automática de metadados (número da lei, data de publicação, artigos)
- Consultas em linguagem natural sobre a legislação
- Processamento assíncrono de documentos
- Identificação automática de leis em vigor e revogações

## Requisitos

- Python 3.8+
- Redis (para processamento assíncrono)
- Chave de API do Google (para o modelo Gemini)

## Configuração

1. Clone o repositório:
```bash
git clone https://github.com/yurisalesc/poc-legal-llm.git
cd poc-legal-llm
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
echo "GOOGLE_API_KEY=sua_chave_aqui" > .env
```

4. Inicie o Redis:
```bash
docker-compose up -d
```

5. Inicie o worker do Celery:
```bash
celery -A app.tasks worker --loglevel=info
```

6. Inicie a API:
```bash
uvicorn app.main:app --reload
```

## Scripts de Ingestão

### Processar Todos os PDFs
Para processar todos os PDFs em uma pasta:
```bash
python ingest.py /caminho/para/pasta/pdfs
```

### Processar Amostra de 500 PDFs
Para processar uma amostra aleatória de 500 PDFs:
```bash
python ingest_500_files.py /caminho/para/pasta/pdfs
```

## Usando a API

### Upload de Lei
```bash
curl -X POST http://localhost:8000/api/upload-lei/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/caminho/do/arquivo.pdf"
```

Resposta:
```json
{
    "message": "Arquivo recebido. O processamento foi iniciado em segundo plano.",
    "task_id": "12345-abcd-efgh"
}
```

### Consultar Legislação
```bash
curl -X POST http://localhost:8000/api/consultar-lei/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qual a lei mais recente sobre licitações?"
  }'
```

Resposta:
```json
{
    "result": "De acordo com a legislação analisada...",
    "sources": [
        "lei_14133_2021.pdf",
        "lei_8666_1993.pdf"
    ]
}
```

### Verificar Status da API
```bash
curl http://localhost:8000/api/health
```

Resposta:
```json
{
    "status": "API online"
}
```
