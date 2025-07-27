FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Pre-download the model during build
RUN pip install --no-cache-dir -r requirements.txt && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2', cache_folder='/app/models')"

EXPOSE 5000

CMD ["python", "app.py"]