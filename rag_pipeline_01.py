# =========================
# Environment Setup
# -------------------------
# Load .env file first before any other imports
# so all os.getenv() calls work correctly.
# =========================
import os
from dotenv import load_dotenv
load_dotenv()

# =========================
# Imports
# -------------------------
# LangChain utilities for loading, splitting,
# and storing documents in vector databases.
# =========================
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS, Chroma
from langchain_core.embeddings import Embeddings
from huggingface_hub import InferenceClient  # ✅ Moved here — was duplicated below


# =========================
# Custom Embeddings Class
# -------------------------
# Wraps HuggingFace InferenceClient to implement
# LangChain's Embeddings interface.
# Used to embed both documents and user queries
# via the HF Inference API (no local GPU needed).
# =========================

api_key = os.getenv("HF_TOKEN")

class HFInferenceEmbeddings(Embeddings):
    def __init__(self, model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = model
        self.client = InferenceClient(
            provider="hf-inference",
            api_key=os.getenv("HF_TOKEN")  # Loaded from .env
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # ✅ Use list comprehension instead of manual loop + append
        return [
            self.client.feature_extraction(text, model=self.model).tolist()
            for text in texts
        ]

    def embed_query(self, text: str) -> list[float]:
        # ✅ Added .tolist() — feature_extraction returns a numpy array;
        #    FAISS/Chroma expect a plain Python list
        return self.client.feature_extraction(text, model=self.model).tolist()


# =========================
# Path Configuration
# -------------------------
# Central place for all file/folder paths.
# Directories are created upfront so later
# steps never fail on missing folders.
# =========================
DATA_PATH  = "Data_cleaned"
FAISS_PATH = "vectorstores/faiss"
CHROMA_PATH = "vectorstores/chroma"

os.makedirs(FAISS_PATH,  exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)


# =========================
# Step 1 — Load & Chunk
# -------------------------
# Reads a .md/.txt file and splits it into
# overlapping chunks so large documents fit
# within the embedding model's token limit.
# =========================
def load_and_chunk(file_path: str, chunk_size=500, chunk_overlap=100):
    print(f"\n📄 Loading: {file_path}")

    documents = TextLoader(file_path, encoding="utf-8").load()

    chunks = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    ).split_documents(documents)

    print(f"✅ {len(chunks)} chunks created")
    return chunks


# =========================
# Step 2 — Embedding Model
# -------------------------
# Returns a single shared embedding instance.
# Centralised here so the model name is only
# defined in one place.
# =========================
def get_embedding() -> HFInferenceEmbeddings:
    return HFInferenceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")


# =========================
# Step 3 — Build FAISS Store
# -------------------------
# Creates an in-memory FAISS index from chunks
# and saves it to disk for later retrieval.
# Fast similarity search; ideal for prototyping.
# =========================
def create_faiss(chunks, db_name: str, embedding):
    save_path = os.path.join(FAISS_PATH, db_name)
    print(f"\n⚡ Building FAISS → {save_path}")

    FAISS.from_documents(chunks, embedding).save_local(save_path)

    print(f"✅ FAISS saved at: {save_path}")


# =========================
# Step 4 — Build Chroma Store
# -------------------------
# Creates a persistent Chroma vector store.
# Auto-persists on creation in Chroma ≥ 0.4.x,
# so db.persist() is no longer needed (removed).
# =========================
def create_chroma(chunks, db_name: str, embedding):
    persist_dir = os.path.join(CHROMA_PATH, db_name)
    print(f"\n🧠 Building Chroma → {persist_dir}")

    Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=persist_dir
        # ✅ Removed db.persist() — deprecated and auto-called since Chroma 0.4
    )

    print(f"✅ Chroma saved at: {persist_dir}")


# =========================
# Step 5 — Full Pipeline
# -------------------------
# Orchestrates loading, chunking, and indexing
# for every data source. Add new sources by
# appending to the `sources` list — no copy-paste.
# =========================
def build_all_vectorstores():
    print("\n🚀 Starting RAG pipeline (HF API + FAISS + Chroma)...")

    embedding = get_embedding()

    # ✅ Data sources in one list — easy to extend without repeating code
    sources = [
        ("faq_stc_cleaned.md", "stc_db"),
        ("faq_we_cleaned.md",  "we_db"),
    ]

    for file_name, db_name in sources:
        chunks = load_and_chunk(os.path.join(DATA_PATH, file_name))
        create_faiss(chunks, db_name, embedding)
        create_chroma(chunks, db_name, embedding)

    print("\n🎯 RAG pipeline completed successfully!")


# =========================
# Entry Point
# =========================
if __name__ == "__main__":
    build_all_vectorstores()