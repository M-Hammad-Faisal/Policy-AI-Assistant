# --- STAGE 1: Builder Stage ---
FROM python:3.11-slim as builder

# Install curl for Poetry installation
RUN apt-get update && apt-get install -y curl \
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

# Copy and install dependencies
COPY pyproject.toml poetry.lock ./
# --only main avoids errors with missing 'dev' group
RUN $POETRY_HOME/bin/poetry install --only main --no-root

# --- STAGE 2: Final Image (Runtime) ---
FROM python:3.11-slim AS runtime

WORKDIR /app

# Define VIRTUAL_ENV and update PATH for the runtime image
ENV VIRTUAL_ENV=/app/.venv \
    PATH=/app/.venv/bin:$PATH \
    # Set Python path for src layout
    PYTHONPATH=/app/src

# Copy the entire virtual environment from the builder stage
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Copy the application code and data
COPY src/ ./src/
COPY policy_documents/ policy_documents/
COPY policy_index/ policy_index/
COPY start.sh .

# Make the startup script executable
RUN chmod +x start.sh

# Set placeholder environment variables (Actual values set by Cloud Run Secrets)
ENV SLACK_BOT_TOKEN="DUMMY"
ENV GOOGLE_API_KEY="DUMMY"

EXPOSE 8080

CMD ["./start.sh"]