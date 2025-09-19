import os
import re

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.prompts import PromptTemplate
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIRECTORY, GOOGLE_API_KEY

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY if GOOGLE_API_KEY is not None else ""


def get_vector_store():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectordb = Chroma(
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        embedding_function=embeddings,
        collection_name=CHROMA_COLLECTION_NAME,
    )
    return vectordb


def process_pdf_and_store(file_path: str):
    print(f"Iniciando processamento do PDF: {file_path}")
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    full_text = " ".join([doc.page_content for doc in documents])

    lei_match = re.search(
        r"(LEI|DECRETO)\s*N?[º°]?\s*([\d\.]+)", full_text, re.IGNORECASE
    )
    data_match = re.search(
        r"DE\s*(\d{1,2}\s*DE\s*\w+\s*DE\s*\d{4})", full_text, re.IGNORECASE
    )

    base_metadata = {"source": os.path.basename(file_path)}
    if lei_match:
        base_metadata["lei_numero"] = lei_match.group(2).replace(".", "")
    if data_match:
        base_metadata["data_publicacao"] = data_match.group(1)

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


def query_legal_document(question: str):
    vectordb = get_vector_store()
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.0)
    retriever = vectordb.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 8, "fetch_k": 20},
    )

    prompt_template = """
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

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT},
    )

    result = qa_chain.invoke({"query": question})
    sources = [doc.metadata.get("source", "N/A") for doc in result["source_documents"]]
    return {"resposta": result["result"], "fontes": list(set(sources))}


def query_legal_document_self_query(question: str):
    vectordb = get_vector_store()
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)

    metadata_field_info = [
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
    document_content_description = (
        "Um trecho (chunk) de um documento legislativo brasileiro."
    )

    retriever = SelfQueryRetriever.from_llm(
        llm, vectordb, document_content_description, metadata_field_info, verbose=True
    )

    prompt_template = """
    Você é um assistente de IA especialista em legislação brasileira. Sua tarefa é analisar
    os trechos de leis e decretos fornecidos abaixo para responder à pergunta do usuário.
    Se baseie SOMENTE no contexto fornecido.
    Identifique qual é a lei ou decreto mais recente que está em vigor sobre o assunto.
    Se uma lei revoga outra, deixe isso claro na sua resposta.

    Contexto:
    {context}

    Pergunta:
    {question}

    Resposta detalhada:
    """

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT},
    )

    result = qa_chain({"query": question})

    sources = [doc.metadata.get("source", "N/A") for doc in result["source_documents"]]

    response = {"resposta": result["result"], "fontes": list(set(sources))}

    return response
