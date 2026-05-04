from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PostResponse(BaseModel):
    id: str
    type: str
    item: Optional[str] = None
    location: Optional[str] = None
    contact: Optional[str] = None
    created_at: datetime
    source: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "abc123",
                "type": "lost",
                "item": "wallet",
                "location": "Port Said",
                "contact": "01012345678",
                "created_at": "2026-05-04T01:25:16Z",
                "source": "facebook"
            }
        }
    )

class ScrapeResponse(BaseModel):
    status: str
    posts_scraped: int
    posts_processed: int
    skipped_duplicates: int
    message: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "posts_scraped": 10,
                "posts_processed": 3,
                "skipped_duplicates": 7,
                "message": None
            }
        }
    )

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "error",
                "message": "Invalid input parameters"
            }
        }
    )
