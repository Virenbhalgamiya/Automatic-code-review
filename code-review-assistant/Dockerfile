FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (build tools, PostgreSQL client library)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration and setup files first for caching
COPY requirements.txt setup.py ./

# Install packages
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -e .

# Copy application and test code
COPY src/ ./src/
COPY tests/ ./tests/
COPY sample_code.py ./sample_code.py


# Set Environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Default command to run the API
CMD ["uvicorn", "src.main_api:app", "--host", "0.0.0.0", "--port", "8000"]
