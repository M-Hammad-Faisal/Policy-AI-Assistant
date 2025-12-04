import os
import logging
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from typing import List
from llama_index.core.schema import Document

# --- Logging Setup ---
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- CONFIGURATION ---

POLICY_DOCS_DIR: str = "policy_documents"
INDEX_STORAGE_DIR: str = "policy_index"


def build_knowledge_base() -> None:
    """
    Loads documents, creates vector embeddings, and saves the index to disk.
    """
    logger.info("Starting knowledge base ingestion...")

    # 1. Ensure the document directory exists
    if not os.path.exists(POLICY_DOCS_DIR):
        logger.error(
            f"Error: Directory '{POLICY_DOCS_DIR}' not found. Please create it and add your policy files."
        )
        return

    # 2. Load documents from the directory
    logger.info(f"Loading documents from {POLICY_DOCS_DIR}...")
    documents: List[Document] = SimpleDirectoryReader(POLICY_DOCS_DIR).load_data()

    if not documents:
        logger.warning("No documents found. Please add policy files to the directory.")
        return

    # 3. Initialize the Embedding Model
    logger.info("Initializing HuggingFace Embedding Model...")
    embed_model: HuggingFaceEmbedding = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    # 4. Create the Index
    logger.info("Creating vector embeddings and building index...")
    index: VectorStoreIndex = VectorStoreIndex.from_documents(
        documents, embed_model=embed_model, show_progress=True
    )

    # 5. Save the Index to disk
    logger.info(f"Saving index to disk at {INDEX_STORAGE_DIR}...")

    if not os.path.exists(INDEX_STORAGE_DIR):
        os.makedirs(INDEX_STORAGE_DIR)

    index.storage_context.persist(persist_dir=INDEX_STORAGE_DIR)
    logger.info("✅ Knowledge base built successfully!")


if __name__ == "__main__":
    build_knowledge_base()
