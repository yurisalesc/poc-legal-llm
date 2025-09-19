import os
import re
from typing import Dict, Any

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.services.vector_store import get_vector_store


def extract_metadata(text: str) -> Dict[str, Any]:
    """
    Extrai metadados do texto do documento legal.

    Esta função utiliza expressões regulares para identificar e extrair informações
    importantes do texto, como:
    - Número da lei ou decreto
    - Data de publicação no formato oficial brasileiro

    Args:
        text (str): Texto completo do documento legal

    Returns:
        Dict[str, Any]: Dicionário contendo os metadados extraídos:
            - lei_numero: Número da lei/decreto sem pontuação
            - data_publicacao: Data no formato 'DD DE MÊS DE AAAA'
    """
    lei_match = re.search(r"(LEI|DECRETO)\s*N?[º°]?\s*([\d\.]+)", text, re.IGNORECASE)
    data_match = re.search(
        r"DE\s*(\d{1,2}\s*DE\s*\w+\s*DE\s*\d{4})", text, re.IGNORECASE
    )

    metadata = {}
    if lei_match:
        metadata["lei_numero"] = lei_match.group(2).replace(".", "")
    if data_match:
        metadata["data_publicacao"] = data_match.group(1)

    return metadata


def process_pdf_and_store(file_path: str) -> bool:
    """
    Processa um arquivo PDF de documento legal e armazena seu conteúdo no banco de dados vetorial.

    Este é um processo complexo que envolve várias etapas:
    1. Carregamento do PDF usando PyPDFLoader
    2. Extração do texto completo e metadados básicos
    3. Divisão do documento em chunks menores para processamento eficiente
    4. Identificação e extração de números de artigos para cada chunk
    5. Enriquecimento dos chunks com metadados
    6. Armazenamento no banco de dados vetorial

    Parâmetros importantes:
    - Tamanho do chunk: 1000 caracteres
    - Sobreposição: 150 caracteres (para manter contexto entre chunks)

    Args:
        file_path (str): Caminho completo para o arquivo PDF

    Returns:
        bool: True se o processamento foi bem-sucedido

    Exemplo de metadados extraídos para cada chunk:
        {
            "source": "nome_do_arquivo.pdf",
            "lei_numero": "8666",
            "data_publicacao": "21 DE JUNHO DE 1993",
            "artigo": "42"
        }
    """
    print(f"Iniciando processamento do PDF: {file_path}")
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    full_text = " ".join([doc.page_content for doc in documents])
    base_metadata = {
        "source": os.path.basename(file_path),
        **extract_metadata(full_text),
    }

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)

    for doc in docs:
        artigo_match = re.search(r"Art\.\s*(\d+)", doc.page_content, re.IGNORECASE)
        artigo_numero = artigo_match.group(1) if artigo_match else "N/A"
        doc.metadata = {**base_metadata, "artigo": artigo_numero}

    print(f"PDF dividido em {len(docs)} chunks com metadados enriquecidos.")

    vectordb = get_vector_store()
    vectordb.add_documents(docs)
    vectordb.persist()

    print(f"Documento {file_path} processado e armazenado com sucesso.")
    return True
