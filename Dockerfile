FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
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

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose the port
EXPOSE 8080

# Create startup script with retries
RUN echo '#!/bin/bash\n\
\n\
# Function to retry commands\n\
retry() {\n\
    local retries=5\n\
    local count=1\n\
    until "$@"; do\n\
        exit=$?\n\
        wait=$((count * 10))\n\
        count=$((count + 1))\n\
        if [ $count -lt $retries ]; then\n\
            echo "Retry $count/$retries exited $exit, retrying in $wait seconds..."\n\
            sleep $wait\n\
        else\n\
            echo "Retry $count/$retries exited $exit, no more retries left."\n\
            return $exit\n\
        fi\n\
    done\n\
    return 0\n\
}\n\
\n\
# Wait for a moment to ensure system is ready\n\
echo "Waiting for system to initialize..."\n\
sleep 10\n\
\n\
# Run migrations with retry\n\
echo "Running database migrations..."\n\
retry python manage.py migrate --noinput\n\
\n\
# Run deployment checks\n\
echo "Running deployment checks..."\n\
python manage.py check --deploy\n\
\n\
# Start Gunicorn with config file\n\
echo "Starting Gunicorn..."\n\
exec gunicorn -c gunicorn.conf.py my_django_project.wsgi:application\n'\
> /app/start.sh && chmod +x /app/start.sh

# Run startup script
CMD ["/app/start.sh"] 