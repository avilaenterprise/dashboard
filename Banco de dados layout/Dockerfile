# Use Python 3.13 as base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8000 (Streamlit default for production)
EXPOSE 8000

# Create directory for logs
RUN mkdir -p /app/logs

# Run the application
CMD ["streamlit", "run", "main.py", "--server.port=8000", "--server.address=0.0.0.0", "--server.headless=true"]
