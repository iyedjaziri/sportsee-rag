# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install poetry or use pip directly. Since we used pip/requirements style in this session mostly (despite pyproject.toml), 
# let's stick to pip to ensure compatibility with what we just tested.
# However, for a clean build, let's copy requirements.
# We don't have a requirements.txt generated from the current state yet.
# Let's generate one or use pyproject.toml if we were strictly using poetry.
# Given the mix, I will generate requirements.txt first in the workflow or assume it exists.
# For now, let's install the known packages.

COPY pyproject.toml .
# We'll use pip to install from pyproject.toml or just install the list we know.
# To be safe and robust:
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run command
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
