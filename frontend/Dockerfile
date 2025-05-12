# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Add build argument for version tracking
ARG BUILD_NUMBER
ENV BUILD_NUMBER=$BUILD_NUMBER

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend app code
COPY . .

# Create templates directory if it doesn't exist
RUN mkdir -p templates

# Expose port for the Flask app
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=frontend.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1


# Command to run the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]