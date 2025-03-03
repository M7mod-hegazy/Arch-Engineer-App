import os
import logging

logger = logging.getLogger("gunicorn.error")

# Server socket
bind = "0.0.0.0:8080"
backlog = 2048

# Worker processes
workers = 2
worker_class = 'gthread'
threads = 4
worker_connections = 1000
timeout = 300
keepalive = 2
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "debug"
capture_output = True
enable_stdio_inheritance = True

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

def when_ready(server):
    logger.info("Server is ready. Doing nothing.")

def pre_fork(server, worker):
    logger.info("Pre-fork: Doing nothing.")

def post_fork(server, worker):
    logger.info("Post-fork: Worker spawned (pid: %s)", worker.pid)

def pre_request(worker, req):
    if req.path == '/health':
        worker.log.debug("Health check request received")
        return None
    return None

def post_request(worker, req, environ, resp):
    if req.path == '/health':
        worker.log.debug(f"Health check response sent: {resp.status}") 