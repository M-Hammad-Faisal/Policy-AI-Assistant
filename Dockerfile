# --- STAGE 1: Base Builder (Install Dependencies) ---
FROM python:3.11-slim as base-builder

RUN apt-get update && apt-get install -y curl git \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.8.3 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    VIRTUAL_ENV=/app/.venv \
    PATH=/app/.venv/bin:$PATH

RUN curl -sSL https://install.python-poetry.org/ -o install-poetry.py \
    && python3 install-poetry.py --version "${POETRY_VERSION}" \
    && rm install-poetry.py

WORKDIR /app

# Dependency Caching Optimization
COPY pyproject.toml poetry.lock ./
RUN $POETRY_HOME/bin/poetry install --only main --no-root


# --- STAGE 2: Ingest Builder (Create the Vector Index) ---
FROM base-builder as ingest-builder

COPY src/ ./src/
COPY policy_documents/ policy_documents/

# Build the index (creates 'policy_index/')
RUN python3 src/ingest.py


# --- STAGE 3: Final Image (Runtime) ---
FROM python:3.11-slim AS runtime

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH=/app/.venv/bin:$PATH \
    PYTHONPATH=/app/src

# Copy Python virtual environment
COPY --from=base-builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Copy application code
COPY src/ ./src/
COPY start.sh .

# Copy the generated index from the ingest stage
COPY --from=ingest-builder /app/policy_index/ policy_index/

RUN chmod +x start.sh

# Set placeholder environment variables
ENV SLACK_BOT_TOKEN="DUMMY"

EXPOSE 8080

CMD ["./start.sh"]