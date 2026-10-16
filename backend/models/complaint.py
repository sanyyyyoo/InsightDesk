from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ComplaintSubmit(BaseModel):
    """
    What a logged-in customer sends to /analyze.

    Deliberately has no user_id: the server takes it from the verified
    Supabase token. Unknown fields (including a user_id) are ignored.
    """
    complaint_text: str = Field(min_length=10, max_length=5000)
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