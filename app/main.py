import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.db.init_db import init_db
from app.api.routes import router
from app.observability.otel import setup_tracing
from app.observability.metrics import REQUESTS, LATENCY

def create_app() -> FastAPI:
    app = FastAPI(title="AI Infrastructure Orchestrator", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def _startup():
        init_db()
        setup_tracing()
        FastAPIInstrumentor.instrument_app(app)

    @app.middleware("http")
    async def metrics_mw(request: Request, call_next):
        path = request.url.path
        method = request.method
        with LATENCY.labels(path=path, method=method).time():
            resp: Response = await call_next(request)
        REQUESTS.labels(path=path, method=method, status=str(resp.status_code)).inc()
        return resp

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    app.include_router(router)
    return app

app = create_app()
