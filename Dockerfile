FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media

# Copy project files
COPY . .

# Remove any existing static files
RUN rm -rf /app/staticfiles/*

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# Run migrations and start server with default port 8000 if PORT is not set
CMD python manage.py migrate && gunicorn my_django_project.wsgi:application --bind 0.0.0.0:${PORT:-8000} --timeout 300 