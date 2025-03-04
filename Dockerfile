FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media

# Copy project files
COPY . .

# Clear existing static files
RUN rm -rf /app/staticfiles/*

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# Create and set permissions for start script
RUN echo '#!/bin/bash\n\
\n\
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
echo "Waiting for system to initialize..."\n\
sleep 10\n\
\n\
echo "Running database migrations..."\n\
retry python manage.py migrate --noinput\n\
\n\
echo "Running deployment checks..."\n\
python manage.py check --deploy\n\
\n\
echo "Starting Gunicorn..."\n\
exec gunicorn -c gunicorn.conf.py my_django_project.wsgi:application\n\
'> /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8080

# Set the default command
CMD ["/app/start.sh"] 