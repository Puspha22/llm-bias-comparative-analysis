FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy repository contents
COPY src/ ./src/
COPY data/ ./data/
COPY reports/ ./reports/
COPY tests/ ./tests/
COPY REPRODUCIBILITY.md .

# Default command runs unit tests and counterfactual audit
CMD ["python", "src/run_counterfactual_audit.py"]
