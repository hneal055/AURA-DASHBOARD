FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for numpy/pandas optimization)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set python path to root so imports work correctly
ENV PYTHONPATH=/app
ENV FLASK_APP=src.app:app

EXPOSE 5000

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app:app"]
