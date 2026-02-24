from prometheus_client import Counter, Histogram

REQUESTS = Counter("aio_requests_total", "Total HTTP requests", ["path", "method", "status"])
LATENCY = Histogram("aio_request_latency_seconds", "Request latency", ["path", "method"])
