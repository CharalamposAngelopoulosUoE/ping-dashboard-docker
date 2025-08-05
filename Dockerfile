# Use lightweight Python
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy project files into container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Run dashboard by default
CMD ["python", "monitor/monitor.py", "dashboard"]

