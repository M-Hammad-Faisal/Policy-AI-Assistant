"""Core module for LlamaIndex setup, initialization, and RAG querying."""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI

from .logging_config import logger

if TYPE_CHECKING:
    from llama_index.core.base.response.schema import RESPONSE_TYPE
    from llama_index.core.embeddings import BaseEmbedding
    from llama_index.core.llms import LLM
    from llama_index.core.query_engine import BaseQueryEngine

QUERY_ENGINE: BaseQueryEngine | None = None

INDEX_STORAGE_DIR: str = "policy_index"


def initialize_rag_settings() -> None:
    """Configure global LlamaIndex settings (LLM and Embedding model)."""
    logger.info("Configuring global LlamaIndex settings...")

    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    Settings.llm = GoogleGenAI(model="gemini-2.5-flash")
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    logger.info("LLM and Embedding models configured.")


def initialize_query_engine() -> None:
    """Load the saved vector index and create the global query engine."""
    global QUERY_ENGINE

    logger.info("Loading vector index from disk...")
    try:
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_STORAGE_DIR)
        index = load_index_from_storage(storage_context)

        QUERY_ENGINE = index.as_query_engine(similarity_top_k=3)
        logger.info("✅ Query Engine successfully loaded.")

    except FileNotFoundError:
        logger.error("FATAL ERROR: Index directory '%s' not found. Exiting.", INDEX_STORAGE_DIR)
        os._exit(1)


def query_policy(query_text: str) -> RESPONSE_TYPE:
    """Run the query against the global RAG engine."""
    if QUERY_ENGINE is None:
        error_msg = "Query Engine is not initialized."
        raise RuntimeError(error_msg)

    return QUERY_ENGINE.query(query_text)
