from __future__ import annotations

import logging

from fastapi import FastAPI

from mt5_platform_api.config import ApiSettings, settings as default_settings
from mt5_platform_api.routers import all_routers


def create_app(*, settings: ApiSettings | None = None) -> FastAPI:
    resolved = default_settings if settings is None else settings
    logging.basicConfig(level=getattr(logging, resolved.log_level.upper(), logging.INFO))
    app = FastAPI(
        title=resolved.app_name,
        version=resolved.app_version,
        openapi_url=f"{resolved.api_prefix}/openapi.json" if resolved.expose_openapi else None,
    )
    for router in all_routers:
        app.include_router(router, prefix=resolved.api_prefix)
    return app


def run() -> None:
    import uvicorn

    uvicorn.run("mt5_platform_api.app:app", host="0.0.0.0", port=8000, reload=False)


app = create_app()
