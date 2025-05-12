# Use official Python base image
FROM python:3.12-slim

# Set working directory in container
WORKDIR /app

# Add build argument for version tracking
ARG BUILD_NUMBER
ENV BUILD_NUMBER=$BUILD_NUMBER

# Copy only requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY src/ ./src/
COPY models/ ./models/

# Set environment variable for Python
ENV PYTHONUNBUFFERED=1

# Expose FastAPI port
EXPOSE 8000

# Command to run the FastAPI app using uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]