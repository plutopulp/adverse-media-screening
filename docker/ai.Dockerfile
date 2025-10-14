FROM python:3.13-slim

# Set up non-root user for security (use UID/GID 1000 for bind-mount friendliness)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -g 1000 app && useradd -u 1000 -g 1000 -r uvicorn-user

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy Poetry configuration (paths relative to build context root)
COPY services/ai/pyproject.toml services/ai/poetry.lock* ./

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false 

RUN poetry install --no-interaction --no-ansi --no-root

RUN mkdir -p /app/app /app/downloads && chown -R 1000:1000 /app
# Copy application code
COPY services/ai/app /app/app
    
# Copy entrypoint script
COPY docker/ai.entrypoint.sh .
RUN chmod +x /app/ai.entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 

# Expose the port the server runs on
EXPOSE 5000

# Switch to non-root user
USER uvicorn-user

# Use entrypoint script
ENTRYPOINT ["/app/ai.entrypoint.sh"] 