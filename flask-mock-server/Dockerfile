FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY data/ ./data/

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
