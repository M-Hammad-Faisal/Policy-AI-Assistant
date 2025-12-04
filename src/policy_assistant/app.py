"""Main Slack application module for the Policy Assistant."""
from __future__ import annotations

import os
import re
from typing import Any

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from .logging_config import logger
from .rag_engine import (
    QUERY_ENGINE,
    initialize_query_engine,
    initialize_rag_settings,
    query_policy,
)

# --- APP SETUP ---

load_dotenv()
initialize_rag_settings()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


# --- EVENT HANDLER ---


# UP006 Fix: Use dict instead of Dict
@app.event("app_mention")
def handle_policy_query(body: dict[str, Any], say: Any) -> None:
    """Handle user mention, post a placeholder, run RAG query, and update the message."""
    if QUERY_ENGINE is None:
        say("I am still initializing my knowledge base. Please try again in a minute.")
        logger.warning("Attempted query while QUERY_ENGINE was still None.")
        return

    # Extract IDs and clean text
    raw_text: str = body["event"]["text"]
    user_id: str = body["event"]["user"]
    channel_id: str = body["event"]["channel"]
    query_text: str = re.sub(r"<@\w+>", "", raw_text).strip()

    logger.info("Received query from user %s: %s", user_id, query_text)  # G004 Fix

    # 1. Acknowledge and CAPTURE THE TIMESTAMP (ts)
    ack_message: str = (
        f"Thanks, <@{user_id}>! I'm looking up '{query_text}' now. Please " "wait a moment..."
    )

    ack_response: dict[str, Any] = say(ack_message)
    message_ts: str = ack_response["ts"]
    logger.info("Placeholder message posted with ts: %s", message_ts)  # G004 Fix

    try:
        # 2. Query the RAG Engine
        logger.info("Running RAG query...")
        response: Any = query_policy(query_text)
        logger.info("RAG query completed.")

        # 3. Format the Final Response
        sources: set[str] = set()
        for node in response.source_nodes:
            sources.add(node.metadata.get("file_name", "Unknown Source"))
        source_list: str = "\n".join([f"- {s}" for s in sources])

        final_answer_text: str = f"""
        {response!s}

        ---

        *📚 Sources Used:*
        {source_list}

        _Disclaimer: This information is AI-generated based on the latest company policies and should be used as a guide._
        """

        # 4. UPDATE the placeholder message
        logger.info("Updating message %s with final answer.", message_ts)
        app.client.chat_update(channel=channel_id, ts=message_ts, text=final_answer_text)
        logger.info("Message update successful.")

    except Exception as e:
        logger.exception("Error processing query: %s", e)
        error_message: str = (
            "Oops! I hit an error while trying to find that information. Please check the logs or try "
            "rephrasing your question."
        )
        app.client.chat_update(channel=channel_id, ts=message_ts, text=error_message)


# --- STARTUP SCRIPT ---

if __name__ == "__main__":
    logger.info("--- ATTEMPTING SOCKET MODE CONNECTION ---")

    initialize_query_engine()

    logger.info("\n🚀 Policy AI Assistant is starting up in Socket Mode...")

    # Requires SLACK_APP_TOKEN
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
