# Use lightweight Python image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy project files into container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir pandas matplotlib fpdf flask colorama python-dotenv

# Expose Flask port for dashboard
EXPOSE 5000

# Default command (runs dashboard manually)
CMD ["python", "monitor/monitor.py", "dashboard"]
