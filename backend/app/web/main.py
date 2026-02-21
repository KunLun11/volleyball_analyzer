import logging

from fastapi import FastAPI

from app.config import settings
from app.web.lifespan import lifespan
from app.web.routers import health, matches, reports, ws

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    docs_url="/docs",
    openapi_url="/openapi.json",
    title="Volleyball API",
    lifespan=lifespan,
)

app.include_router(matches.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(ws.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.web.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True,
    )
