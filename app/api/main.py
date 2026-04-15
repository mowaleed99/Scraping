from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, posts, matches, groups

def create_app() -> FastAPI:
    app = FastAPI(
        title="Lost & Found Scraper API",
        description="API for managing scraper jobs, retrieved posts, and intelligence matches.",
        version="0.1.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # For development, specify domains in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(groups.router)
    app.include_router(posts.router)
    app.include_router(matches.router)
    
    return app

app = create_app()
