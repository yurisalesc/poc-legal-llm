from typing import List, Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    """
    Modelo para requisições de consulta à base de leis.

    Attributes:
        question (str): A pergunta ou consulta que será feita sobre a legislação
    """
    question: str


class QueryResponse(BaseModel):
    """
    Modelo para respostas das consultas à base de leis.

    Attributes:
        result (str): A resposta gerada pelo modelo de linguagem
        sources (List[str]): Lista de fontes (arquivos) consultados para gerar a resposta
    """
    result: str
    sources: List[str]


class TaskResponse(BaseModel):
    """
    Modelo para respostas de tarefas assíncronas.

    Attributes:
        message (str): Mensagem descritiva sobre o status da tarefa
        task_id (str): Identificador único da tarefa para acompanhamento posterior
    """
    message: str
    task_id: str


class ProcessingResult(BaseModel):
    """
    Modelo para resultados de processamento.

    Attributes:
        status (str): Status do processamento ('Sucesso' ou 'Erro')
        message (str): Mensagem detalhando o resultado do processamento
    """
    status: str
    message: str


class DocumentMetadata(BaseModel):
    """
    Modelo para metadados extraídos de documentos legais.

    Attributes:
        source (str): Nome do arquivo fonte
        lei_numero (Optional[str]): Número da lei ou decreto (ex: '8666')
        data_publicacao (Optional[str]): Data de publicação no formato 'DD DE MÊS DE AAAA'
        artigo (Optional[str]): Número do artigo, se aplicável
    """
    source: str
    lei_numero: Optional[str] = None
    data_publicacao: Optional[str] = None
    artigo: Optional[str] = None
