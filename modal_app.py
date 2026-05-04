import modal

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi",
    "uvicorn",
    "sqlalchemy[asyncio]",
    "asyncpg",
    "alembic",
    "groq",
    "apify-client",
    "pydantic",
    "pydantic-settings",
    "structlog",
    "litellm",
).add_local_python_source("app")

app = modal.App("lost-found-backend", image=image)

# Secrets: Ensure we have .env configured via Modal Secrets
# e.g., modal secret create lost-found-secrets --from-dotenv

@app.function(secrets=[modal.Secret.from_name("lost-found-secrets")], min_containers=1)
@modal.asgi_app()
def fastapi_server():
    from app.api.main import app as fastapi_app
    return fastapi_app

