"""FastAPI app for the internal API (powers the QA console; P3 customer surface).

Every route except /health requires the internal API key. Routers depend on the
QaService seam, so the app is unit-testable with a fake service. In production the
app FAILS CLOSED: it refuses to start on the insecure dev key, and the interactive
API docs are disabled.
"""

from __future__ import annotations

from fastapi import Depends, FastAPI
from li_core.config import DEV_INTERNAL_API_KEY, get_settings

from li_api.auth import require_api_key
from li_api.routers import costs, qa


class InsecureConfigError(RuntimeError):
    """Production was started without overriding an insecure default."""


def create_app() -> FastAPI:
    settings = get_settings()
    if settings.is_production and settings.internal_api_key == DEV_INTERNAL_API_KEY:
        # Fail closed: never run production on a source-code-known key.
        raise InsecureConfigError(
            "INTERNAL_API_KEY is still the dev default in production; set a real key."
        )

    title = "Lead Intelligence — internal API"
    if settings.is_production:
        # Interactive docs / schema are open (no auth) — disable them in production.
        app = FastAPI(title=title, version="0.1.0", docs_url=None, redoc_url=None, openapi_url=None)
    else:
        app = FastAPI(title=title, version="0.1.0")

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    # All data routes sit behind the API-key dependency.
    app.include_router(qa.router, dependencies=[Depends(require_api_key)])
    app.include_router(costs.router, dependencies=[Depends(require_api_key)])
    return app


app = create_app()
