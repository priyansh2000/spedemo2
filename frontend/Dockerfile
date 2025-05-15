# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Add build argument for version tracking
ARG BUILD_NUMBER
ENV BUILD_NUMBER=$BUILD_NUMBER

# Copy requirements file
COPY requirements.txt .

# Add prometheus-client to requirements or install it directly
RUN pip install --no-cache-dir -r requirements.txt prometheus-client

# Copy frontend app code
COPY . .

# Create templates directory if it doesn't exist
RUN mkdir -p templates

# Create metrics script
RUN echo 'import time\nfrom prometheus_client import start_http_server, Counter, Gauge\nimport os\n\n# Create metrics\nREQUEST_COUNT = Counter("frontend_requests_total", "Total frontend requests")\nACTIVE_REQUESTS = Gauge("frontend_active_requests", "Active frontend requests")\n\n# Start server\nstart_http_server(8001)\nprint("Metrics server started on port 8001")\n\n# Keep the process alive\nwhile True:\n    time.sleep(1)' > metrics_server.py

# Expose ports for Flask app and metrics
EXPOSE 5000 8001

# Set environment variables
ENV FLASK_APP=frontend.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Create entrypoint script
RUN echo '#!/bin/bash\npython metrics_server.py &\nflask run --host=0.0.0.0 --port=5000' > entrypoint.sh && \
    chmod +x entrypoint.sh

# Command to run both services
CMD ["./entrypoint.sh"]