
import os

# Gunicorn configuration for production
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
workers = os.environ.get('WEB_CONCURRENCY', 1)
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
accesslog = '-'
errorlog = '-'
loglevel = 'info'
