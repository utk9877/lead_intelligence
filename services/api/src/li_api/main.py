"""FastAPI app for the internal API (powers the QA console; P3 customer surface).

Every route except /health requires the internal API key. Routers depend on the
QaService seam, so the app is unit-testable with a fake service.
"""

from __future__ import annotations

from fastapi import Depends, FastAPI

from li_api.auth import require_api_key
from li_api.routers import costs, qa


def create_app() -> FastAPI:
    app = FastAPI(title="Lead Intelligence — internal API", version="0.1.0")

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    # All data routes sit behind the API-key dependency.
    app.include_router(qa.router, dependencies=[Depends(require_api_key)])
    app.include_router(costs.router, dependencies=[Depends(require_api_key)])
    return app


app = create_app()
