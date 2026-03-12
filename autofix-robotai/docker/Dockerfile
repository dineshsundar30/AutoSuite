FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for git and basic compilation
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set python path so we can import from the project root
ENV PYTHONPATH=/app

# Default command 
ENTRYPOINT ["python", "-m", "cli.main"]
CMD ["--help"]
