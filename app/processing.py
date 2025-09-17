import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIRECTORY, GOOGLE_API_KEY

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY if GOOGLE_API_KEY is not None else ""


def get_vector_store():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return Chroma(
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        embedding_function=embeddings,
        collection_name=CHROMA_COLLECTION_NAME,
    )


def process_pdf_and_store(file_path: str):
    print(f"Iniciando processamento do PDF: {file_path}")

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    docs = text_splitter.split_documents(documents)

    for doc in docs:
        doc.metadata = {"source": os.path.basename(file_path)}

    print(f"PDF dividido em {len(docs)} chunks")

    vectordb = get_vector_store()
    vectordb.add_documents(docs)

    print(f"Documento {file_path} processado e armazenado com sucesso!")
    return True


def query_legal_document(question: str):
    vectordb = get_vector_store()
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.0)
    retriever = vectordb.as_retriever(search_kwargs={"k": 10})

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
