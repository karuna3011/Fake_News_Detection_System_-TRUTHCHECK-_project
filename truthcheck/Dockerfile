FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')" 2>/dev/null || true

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p database ai_model

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=0
ENV PORT=5000

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
