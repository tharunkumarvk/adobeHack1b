FROM python:3.9-slim
RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir \
    PyMuPDF==1.23.5 \
    transformers==4.41.2 \
    torch==2.3.1 \
    numpy==1.24.3
WORKDIR /app
COPY main.py .
CMD ["python", "main.py"]