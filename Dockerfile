FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    curl \
    unzip \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Set display for headless operation
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (required by Render)
EXPOSE 10000

# Make start script executable
RUN chmod +x start.sh

# Start command
CMD ["./start.sh"]