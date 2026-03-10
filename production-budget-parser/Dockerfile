FROM python:3.11-slim

WORKDIR /app

# System deps for pandas/numpy/matplotlib/reportlab
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .
COPY static/ static/
COPY templates/ templates/

# Create required directories
RUN mkdir -p uploads outputs instance

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# ANTHROPIC_API_KEY, SECRET_KEY, and BUDGET_API_KEY must be passed at runtime
ENV FLASK_ENV=production

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "web_app:app"]
