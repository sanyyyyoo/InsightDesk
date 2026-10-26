from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

MAX_COMPLAINT_CHARS = 5000


class ComplaintSubmit(BaseModel):
    """
    What a logged-in customer sends to /analyze.

    Deliberately has no user_id: the server takes it from the verified
    Supabase token. Unknown fields (including a user_id) are ignored.
    Text beyond MAX_COMPLAINT_CHARS characters is truncated, not rejected.
    """
    complaint_text: str = Field(min_length=10)

    @field_validator("complaint_text", mode="before")
    @classmethod
    def truncate(cls, v):
        return v[:MAX_COMPLAINT_CHARS] if isinstance(v, str) else v
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    product: Optional[str] = Field(default=None, max_length=200)


class ComplaintCreate(BaseModel):
    complaint_text: str
    user_id: str
    rating: Optional[int] = None
    source: Optional[str] = None
    product: Optional[str] = None
    company_size: Optional[str] = None
    is_synthetic: bool = False


class ComplaintDB(ComplaintCreate):
    complaint_id: int
    case_id: Optional[int] = None
    cleaned_text: Optional[str] = None
    is_duplicate: bool = False
    created_at: datetime