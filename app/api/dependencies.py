from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import get_settings

security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    settings = get_settings()
    if credentials.credentials != settings.api_secret_key:
        # We will catch this in the global exception handler
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return credentials.credentials
