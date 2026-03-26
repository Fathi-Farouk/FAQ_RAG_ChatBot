import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# Imports (LCEL)
# =========================
from langchain_community.vectorstores import FAISS, Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

# Your embedding class
from rag_pipeline_01 import HFInferenceEmbeddings


# =========================
# Config
# =========================
FAISS_PATH = "vectorstores/faiss"
CHROMA_PATH = "vectorstores/chroma"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# =========================
# Load Embedding
# =========================
def get_embedding():
    return HFInferenceEmbeddings(model=EMBEDDING_MODEL)


# =========================
# Load Vector Store
# =========================
def load_db(source="stc", db_type="faiss"):
    embedding = get_embedding()

    if db_type == "faiss":
        path = f"{FAISS_PATH}/{source}_db"
        db = FAISS.load_local(path, embedding, allow_dangerous_deserialization=True)

    elif db_type == "chroma":
        path = f"{CHROMA_PATH}/{source}_db"
        db = Chroma(persist_directory=path, embedding_function=embedding)

    else:
        raise ValueError("Invalid DB type")

    return db


# =========================
# Format Docs
# =========================
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# =========================
# Build RAG Chain (LCEL)
# =========================
def build_rag_chain(source="stc", db_type="faiss"):
    db = load_db(source, db_type)

    retriever = db.as_retriever(search_kwargs={"k": 3})

    # Prompt
    prompt = ChatPromptTemplate.from_template("""
You are a telecom FAQ assistant.

Answer ONLY from the provided context.
If the answer is not found, say: "I don't know."

Context:
{context}

Question:
{question}

Answer:
""")
    
    ANTHROPIC_API_KEY = os.getenv("Anthropic_Claude_API")

    if not ANTHROPIC_API_KEY:
        raise ValueError("❌ Anthropic_Claude_API not found in .env")

    # Claude
    llm = ChatAnthropic(
        model="claude-sonnet-4-5",
        temperature=0,
        anthropic_api_key=ANTHROPIC_API_KEY
    )

    # LCEL Chain
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


# =========================
# Ask Function
# =========================
def ask(query, source="stc", db_type="faiss"):
    print(f"\n🧠 Query: {query}")
    print(f"📂 Source: {source.upper()} | DB: {db_type.upper()}")

    rag_chain = build_rag_chain(source, db_type)

    response = rag_chain.invoke(query)

    print("\n🤖 Answer:\n")
    print(response)


# =========================
# Run Example
# =========================
if __name__ == "__main__":
    ask(
        query="Where can I buy WE lines?",
        source="we",       # "stc" or "we"
        db_type="faiss"     # "faiss" or "chroma"
    )