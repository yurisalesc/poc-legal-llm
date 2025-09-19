from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIRECTORY


def get_vector_store():
    """
    Inicializa e retorna uma instância do banco de dados vetorial ChromaDB.

    Esta função configura o ChromaDB com embeddings do Google AI para armazenamento
    e recuperação eficiente de documentos legais. O processo envolve:
    1. Inicialização do modelo de embeddings do Google AI
    2. Configuração do ChromaDB com diretório de persistência
    3. Definição da coleção específica para leis e decretos

    Returns:
        Chroma: Instância configurada do ChromaDB para armazenamento vetorial
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectordb = Chroma(
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        embedding_function=embeddings,
        collection_name=CHROMA_COLLECTION_NAME,
    )
    return vectordb
