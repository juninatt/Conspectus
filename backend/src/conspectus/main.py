"""Application entry point."""

from fastapi import FastAPI

from conspectus.api import health


def create_app() -> FastAPI:
    """Build the FastAPI application with all routers registered."""
    app = FastAPI(
        title="Conspectus",
        summary="Tabular data from configurable sources, served over HTTP.",
        version="0.1.0",
    )
    app.include_router(health.router)
    return app


app = create_app()
