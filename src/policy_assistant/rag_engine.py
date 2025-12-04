import os
from typing import Optional, Any
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.query_engine import BaseQueryEngine
from llama_index.core import Settings
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from .logging_config import logger

INDEX_STORAGE_DIR: str = "policy_index"
QUERY_ENGINE: Optional[BaseQueryEngine] = None


def initialize_rag_settings() -> None:
    """Configures global LlamaIndex settings (LLM and Embedding model)."""
    logger.info("Configuring global LlamaIndex settings...")

    # Suppress tokenizers warning by disabling parallelism
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    try:
        # Requires GOOGLE_API_KEY
        Settings.llm = GoogleGenAI(model="gemini-2.5-flash")
        # Requires HF_TOKEN
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        logger.info("LLM and Embedding models configured.")
    except Exception as e:
        logger.error(f"FATAL: Failed to configure LLM/Embedding: {e}", exc_info=True)
        os._exit(1)


def initialize_query_engine() -> None:
    """Loads the saved vector index and creates the global query engine."""
    global QUERY_ENGINE

    logger.info("Loading vector index from disk...")
    try:
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_STORAGE_DIR)
        index = load_index_from_storage(storage_context)

        QUERY_ENGINE = index.as_query_engine(similarity_top_k=3)
        logger.info("✅ Query Engine successfully loaded.")

    except FileNotFoundError:
        logger.error(f"FATAL ERROR: Index directory '{INDEX_STORAGE_DIR}' not found. Exiting.")
        os._exit(1)


def query_policy(query_text: str) -> Any:
    """Runs the query against the global RAG engine."""
    if QUERY_ENGINE is None:
        raise RuntimeError("Query Engine is not initialized.")

    return QUERY_ENGINE.query(query_text)
