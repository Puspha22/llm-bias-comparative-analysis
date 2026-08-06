FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    r-base \
    r-cran-ggplot2 \
    r-cran-jsonlite \
    r-cran-scales \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy repository contents
COPY src/ ./src/
COPY data/ ./data/
COPY reports/ ./reports/
COPY tests/ ./tests/
COPY README.md LICENSE ./

# Default command runs unit tests
CMD ["python", "-m", "unittest", "tests/test_auditor.py"]
