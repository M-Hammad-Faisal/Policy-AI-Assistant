# 🤖 Policy AI Assistant

The Policy AI Assistant is a Slack-based Retrieval-Augmented Generation (RAG) system built with **LlamaIndex**, **Gemini
2.5 Flash**, and **Slack Bolt**. It is designed to quickly answer user questions by referencing internal policy
documents and providing source citations. The application is deployed as a single, highly available service on **Google
Cloud Run** using Socket Mode.

---

## 🚀 Key Features

* **RAG System:** Uses LlamaIndex to chunk, embed, and retrieve data from local policy documents.
* **Gemini 2.5 Flash:** Utilizes Google's fast and powerful model for final answer synthesis.
* **Slack Socket Mode:** Ensures reliable, persistent connection without needing external webhooks or a public IP.
* **Asynchronous UX:** Posts an immediate "working" placeholder message and then updates the thread with the final
  answer for a better user experience.
* **CI/CD Ready:** Includes a `cloudbuild.yaml` for automated deployment to Cloud Run.

---

## 🛠️ Prerequisites

Before starting, ensure you have the following accounts and credentials:

1. **Google Cloud Platform (GCP) Project:** With **Cloud Run**, **Cloud Build**, and **Secret Manager** APIs enabled.
2. **Slack Workspace:** Where you can create and manage a Slack App.
3. **Google Gemini API Key:** Required for the LLM connection.
4. **Hugging Face Account/Token:** Required to bypass rate limits when downloading the BGE embedding model.
5. **Local Tools:** Python 3.11+, Poetry, and the `gcloud` CLI.

---

## 🏗️ Local Setup and Indexing

### 1. Configure the Project

```bash
# Set up Python virtual environment and install dependencies
poetry install

# Activate the shell environment
poetry shell
````

### 2\. Add Policy Documents

Place your policy documents (PDFs, TXT, DOCX) inside the `policy_documents/` directory.

### 3\. Build the Knowledge Index

Run the ingestion script to process the documents and create the vector store. This must be done **before** building the
Docker image.

```bash
python src/ingest.py
```

> **Result:** A directory named `policy_index/` will be created, containing all the index data.

-----

## 🔒 Cloud Run Deployment Configuration

The application requires several sensitive environment variables. These must be secured using **Google Secret Manager**
and referenced in your `cloudbuild.yaml` and Cloud Run service settings.

| Secret Name       | Source                   | Purpose                                                                            |
|:------------------|:-------------------------|:-----------------------------------------------------------------------------------|
| `SLACK_BOT_TOKEN` | Slack App (`xoxb-***`)   | Bot API access (for posting messages).                                             |
| `SLACK_APP_TOKEN` | Slack App (`xapp-1-***`) | Socket Mode connection.                                                            |
| `GOOGLE_API_KEY`  | Google AI Studio         | Access to the Gemini 2.5 Flash model.                                              |
| `HF_TOKEN`        | Hugging Face Settings    | Read access token to prevent 429 rate limits when downloading the embedding model. |

### Slack App Scopes Required

Your Slack Bot Token must have these scopes enabled under **OAuth & Permissions**:

* `app_mentions:read`
* `chat:write`
* `chat:write.public` (If running in public channels)

-----

## 🚀 Automated Deployment (CI/CD)

This project uses **Cloud Build** and the provided `cloudbuild.yaml` for zero-touch deployment upon pushing to your main
branch.

### 1\. Define Custom Substitutions

When setting up your Cloud Build Trigger, you **must** define the following custom substitution variables.

| Variable           | Example Value          | Description                         |
|:-------------------|:-----------------------|:------------------------------------|
| `_REGION`          | `us-central1`          | The GCP region for deployment.      |
| `_SERVICE_NAME`    | `policy-assistant-bot` | The name of your Cloud Run service. |
| `_REPOSITORY_NAME` | `my-docker-repo`       | Artifact Registry repository name.  |
| `_LOCATION`        | `us-central1`          | Location of Artifact Registry.      |

### 2\. Connect and Deploy

1. **Commit** the updated code (including the generated `policy_index/` folder).
2. **Push** the changes to your Git repository (`main` branch).
3. **Cloud Build** will automatically:
    * Build the Docker image using the `Dockerfile`.
    * Push the image to Artifact Registry.
    * Deploy the new image to the specified Cloud Run service (`policy-assistant-bot`), referencing your secrets from
      Secret Manager.

### Manual Deployment (If CI/CD is not used)

If you must deploy manually, use these commands:

```bash
# 1. Build and push the image
gcloud builds submit --tag gcr.io/PROJECT_ID/policy-assistant-bot

# 2. Deploy to Cloud Run (Set secrets directly via the console or CLI)
gcloud run deploy policy-assistant-bot \
    --image gcr.io/PROJECT_ID/policy-assistant-bot \
    --region <YOUR_REGION> \
    --min-instances 1 \
    # NOTE: Add all --set-secrets here if not using the console
```

-----

## ❓ Usage

Once the bot is deployed and the status is **Ready**:

1. Invite the bot to a Slack channel.
2. Mention the bot with a question: `@PolicyAIAssistant What is the process for submitting an expense report?`

The bot will respond in two steps:

1. **Acknowledge:** Posts an immediate "working on your request" message.
2. **Update:** Edits the same message with the final AI-generated answer and source citations.