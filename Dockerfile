# Hugging Face Spaces — FastAPI + ONNX Runtime
FROM python:3.12-slim

WORKDIR /app

# Install system deps (OpenCV needs libgl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements-hf.txt .
RUN pip install --no-cache-dir -r requirements-hf.txt

# Copy application code
COPY app.py .
COPY src/ src/
COPY onnx/ onnx/
COPY data/validation_images/ data/validation_images/

# Expose the port HF Spaces expects
EXPOSE 7860

# Start the server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]