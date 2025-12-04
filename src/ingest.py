"""Utility script to load policy documents and build the LlamaIndex vector store."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

if TYPE_CHECKING:
    from llama_index.core.schema import Document

# --- Logging Setup ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- CONFIGURATION ---

POLICY_DOCS_DIR: str = "policy_documents"
INDEX_STORAGE_DIR: str = "policy_index"


def build_knowledge_base() -> None:
    """Load documents, create vector embeddings, and save the index to disk."""
    logger.info("Starting knowledge base ingestion...")

    policy_docs_path = Path(POLICY_DOCS_DIR)

    # 1. Ensure the document directory exists
    if not policy_docs_path.exists():
        logger.error(
            "Error: Directory '%s' not found. Please create it and add your policy files.",
            POLICY_DOCS_DIR,
        )
        return

    # 2. Load documents from the directory
    logger.info("Loading documents from %s...", POLICY_DOCS_DIR)

    documents: list[Document] = SimpleDirectoryReader(POLICY_DOCS_DIR).load_data()

    if not documents:
        logger.warning("No documents found. Please add policy files to the directory.")
        return

    # 3. Initialize the Embedding Model
    logger.info("Initializing HuggingFace Embedding Model...")
    embed_model: HuggingFaceEmbedding = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # 4. Create the Index
    logger.info("Creating vector embeddings and building index...")
    index: VectorStoreIndex = VectorStoreIndex.from_documents(
        documents,
        embed_model=embed_model,
        show_progress=True,
    )

    # 5. Save the Index to disk
    logger.info("Saving index to disk at %s...", INDEX_STORAGE_DIR)

    index_storage_path = Path(INDEX_STORAGE_DIR)

    if not index_storage_path.exists():
        index_storage_path.mkdir()

    index.storage_context.persist(persist_dir=INDEX_STORAGE_DIR)
    logger.info("✅ Knowledge base built successfully!")


if __name__ == "__main__":
    build_knowledge_base()
