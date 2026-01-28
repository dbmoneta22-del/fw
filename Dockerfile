FROM python:3.11-slim

# Dipendenze di sistema COMPLETE
RUN apt-get update && \
    apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ita \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD gunicorn app:app --bind 0.0.0.0:$PORT
