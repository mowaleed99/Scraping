from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import posts, scrape

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

    app.include_router(posts.router)
    app.include_router(scrape.router)
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "message": str(exc.detail)}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Extract the first error message to make it human readable
        errors = exc.errors()
        if errors:
            first_error = errors[0]
            field = ".".join(str(loc) for loc in first_error.get("loc", []) if loc not in ("body", "query", "path"))
            msg = first_error.get("msg", "Invalid input parameters")
            human_readable = f"Invalid input parameters: {field} - {msg}" if field else f"Invalid input parameters: {msg}"
        else:
            human_readable = "Invalid input parameters"
            
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": human_readable}
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Internal server error"}
        )

    return app

app = create_app()
