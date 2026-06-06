FROM python:3.10-slim

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies lists
COPY requirements.txt requirements-ml.txt /app/

# Install requirements (defaults to local mode, can be upgraded with requirements-ml.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Copy source code
COPY ./app /app/app

# Command to run uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
