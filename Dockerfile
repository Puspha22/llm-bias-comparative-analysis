FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install minimal C compilation dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy active directories (relying on .dockerignore for heavy raw audit data)
COPY src/ ./src/
COPY data/ ./data/
COPY reports/ ./reports/
COPY README.md LICENSE ./

# Default fallback command runs the Table 1 metrics aggregator
CMD ["python", "src/statistical_analysis/compute_rigorous_metrics.py"]
