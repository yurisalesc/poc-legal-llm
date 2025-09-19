from typing import Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.prompts import PromptTemplate
from langchain.retrievers.self_query.base import SelfQueryRetriever

from app.services.vector_store import get_vector_store


def get_prompt_template() -> PromptTemplate:
    """
    Retorna o template de prompt para a cadeia de pergunta e resposta.

    Este template define as instruções específicas para o modelo de linguagem:
    1. Define o papel do assistente como especialista em legislação
    2. Estabelece a necessidade de usar apenas o contexto fornecido
    3. Solicita identificação da legislação mais recente
    4. Pede clareza sobre revogações de leis
    5. Instrui sobre o formato da resposta

    Returns:
        PromptTemplate: Template configurado com variáveis para contexto e pergunta
    """
    template = """
    Você é um assistente de IA especialista em legislação. Sua tarefa é analisar
    os trechos de leis e decretos fornecidos abaixo para responder à pergunta do usuário.
    Se baseie SOMENTE no contexto fornecido.
    Identifique qual é a lei ou decreto mais recente que está em vigor sobre o assunto.
    Se uma lei revoga outra, deixe isso claro na sua resposta.
    A resposta deve ser crua, sem mais textos introdutórios e explicativos adicionais

    Contexto:
    {context}

    Pergunta:
    {question}

    Resposta detalhada:
    """
    return PromptTemplate(template=template, input_variables=["context", "question"])


def get_metadata_field_info() -> list[AttributeInfo]:
    """
    Retorna as informações dos campos de metadados para o recuperador de consultas.

    Define a estrutura e descrição dos metadados disponíveis para busca:
    - source: Identificação do arquivo fonte
    - lei_numero: Número da legislação para buscas específicas
    - data_publicacao: Data de publicação para análise temporal

    Returns:
        list[AttributeInfo]: Lista de descritores de metadados para busca
    """
    return [
        AttributeInfo(
            name="source",
            description="O nome do arquivo PDF de onde o texto foi extraído. Ex: 'lei_8666_1993.pdf'",
            type="string",
        ),
        AttributeInfo(
            name="lei_numero",
            description="O número oficial da lei ou decreto. Use isto para perguntas sobre uma lei específica. Ex: '8666', '10520'",
            type="string",
        ),
        AttributeInfo(
            name="data_publicacao",
            description="A data de publicação da lei. Ex: '21 DE JUNHO DE 1993'",
            type="string",
        ),
    ]


def query_legal_document_self_query(question: str) -> Dict[str, Any]:
    """
    Realiza consultas em documentos legais usando recuperação auto-construída.

    Esta é uma função complexa que implementa um pipeline completo de consulta:

    1. Inicialização:
       - Configura o banco de dados vetorial
       - Inicializa o modelo Gemini Pro com temperatura 0 para máxima precisão

    2. Configuração do Recuperador:
       - Utiliza SelfQueryRetriever para permitir consultas estruturadas
       - Configura descrição do conteúdo e campos de metadados
       - Habilita modo verboso para rastreamento

    3. Configuração da Cadeia QA:
       - Usa estratégia "stuff" para processamento de documentos
       - Incorpora template de prompt personalizado
       - Configura retorno de documentos fonte

    4. Processamento:
       - Executa a consulta
       - Extrai fontes únicas dos documentos
       - Formata a resposta final

    Args:
        question (str): Pergunta do usuário sobre a legislação

    Returns:
        Dict[str, Any]: Dicionário contendo:
            - result: Resposta processada do modelo
            - sources: Lista de fontes únicas consultadas
    """
    vectordb = get_vector_store()
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)

    document_content_description = (
        "Um trecho (chunk) de um documento legislativo brasileiro."
    )

    retriever = SelfQueryRetriever.from_llm(
        llm,
        vectordb,
        document_content_description,
        get_metadata_field_info(),
        verbose=True,
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": get_prompt_template()},
    )

    result = qa_chain({"query": question})
    sources = [doc.metadata.get("source", "N/A") for doc in result["source_documents"]]

    return {"result": result["result"], "sources": list(set(sources))}
