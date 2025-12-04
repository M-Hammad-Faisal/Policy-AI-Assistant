# --- STAGE 1: Base Builder (Install Dependencies) ---
FROM python:3.11-slim as base-builder

# Install necessary utilities and Git
RUN apt-get update && apt-get install -y curl git \
    && rm -rf /var/lib/apt/lists/*

# Environment variables for Poetry and venv location
ENV POETRY_VERSION=1.8.3 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    VIRTUAL_ENV=/app/.venv \
    PATH=/app/.venv/bin:$PATH

# Install Poetry
RUN curl -sSL https://install.python-poetry.org/ -o install-poetry.py \
    && python3 install-poetry.py --version "${POETRY_VERSION}" \
    && rm install-poetry.py

WORKDIR /app

# Copy lock files and install dependencies
COPY pyproject.toml poetry.lock ./
# Install only main dependencies (no dev group)
RUN $POETRY_HOME/bin/poetry install --only main --no-root


# --- STAGE 2: Ingest Builder (Create the Vector Index) ---
FROM base-builder as ingest-builder

# Copy source code and policy documents
COPY src/ ./src/
COPY policy_documents/ policy_documents/

# Build the index. This generates the 'policy_index/' directory.
RUN python3 src/ingest.py


# --- STAGE 3: Final Image (Runtime) ---
FROM python:3.11-slim AS runtime

WORKDIR /app

# Set environment and PATH for the application
ENV VIRTUAL_ENV=/app/.venv \
    PATH=/app/.venv/bin:$PATH \
    PYTHONPATH=/app/src

# Copy the Python virtual environment (dependencies)
COPY --from=base-builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Copy the application code and startup script
COPY src/ ./src/
COPY start.sh .

# Copy the generated policy_index from the ingest-builder stage
COPY --from=ingest-builder /app/policy_index/ policy_index/

# Set executable permission for the entrypoint script
RUN chmod +x start.sh

# Set placeholder environment variables for clarity
ENV SLACK_BOT_TOKEN="xoxb-"
ENV SLACK_APP_TOKEN="xapp-1-"
ENV GOOGLE_API_KEY="AIza"

EXPOSE 8080

CMD ["./start.sh"]