import os
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Import the configured logger and the RAG functions
from .logging_config import logger
from .rag_engine import (
    initialize_rag_settings,
    initialize_query_engine,
    query_policy,
    QUERY_ENGINE
)

# --- APP SETUP ---

load_dotenv()
initialize_rag_settings()  # Configure LLM/Embedding first

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


# --- EVENT HANDLER ---

@app.event("app_mention")
def handle_policy_query(body: Dict[str, Any], say: Any, logger: logging.Logger) -> None:
    """
    Handles user mention, posts a placeholder, runs RAG query, and updates the message.
    """
    if QUERY_ENGINE is None:
        say("I am still initializing my knowledge base. Please try again in a minute.")
        logger.warning("Attempted query while QUERY_ENGINE was still None.")
        return

    # Extract IDs and clean text
    raw_text: str = body['event']['text']
    user_id: str = body['event']['user']
    channel_id: str = body['event']['channel']
    query_text: str = re.sub(r'<@\w+>', '', raw_text).strip()

    logger.info(f"Received query from user {user_id}: {query_text}")

    # 1. Acknowledge and CAPTURE THE TIMESTAMP (ts)
    ack_message: str = f"Thanks, <@{user_id}>! I'm looking up '{query_text}' now. Please wait a moment..."
    ack_response: Dict[str, Any] = say(ack_message)
    message_ts: str = ack_response['ts']

    try:
        # 2. Query the RAG Engine (Calls function in rag_engine.py)
        logger.info("Running RAG query...")
        response: Any = query_policy(query_text)
        logger.info("RAG query completed.")

        # 3. Format the Final Response (similar to previous version)
        sources: set = set()
        for node in response.source_nodes:
            sources.add(node.metadata.get('file_name', 'Unknown Source'))
        source_list: str = "\n".join([f"- {s}" for s in sources])

        final_answer_text: str = f"""{str(response)}\n\n---\n\n*📚 Sources Used:*{source_list}\n\n_Disclaimer: This information is AI-generated..._"""

        # 4. UPDATE the placeholder message
        logger.info(f"Updating message {message_ts} with final answer.")
        app.client.chat_update(channel=channel_id, ts=message_ts, text=final_answer_text)
        logger.info("Message update successful.")

    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        error_message: str = "Oops! I hit an error while trying to find that information. Please check the logs or try rephrasing your question."
        app.client.chat_update(channel=channel_id, ts=message_ts, text=error_message)


# --- STARTUP SCRIPT ---

if __name__ == "__main__":
    logger.info("--- ATTEMPTING SOCKET MODE CONNECTION ---")

    # Initialization is now a quick call to the external function
    initialize_query_engine()

    logger.info("\n🚀 Policy AI Assistant is starting up in Socket Mode...")

    # Requires SLACK_APP_TOKEN
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
