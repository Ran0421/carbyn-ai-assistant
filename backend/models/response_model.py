from pydantic import BaseModel, field_validator
from typing import List, Optional
 
 
class AnalysisResponse(BaseModel):
    status: str
    query: str
    vision_analysis: Optional[str] = None   # None when Gemini parsing fails
    diagnosis: Optional[str] = None          # parsed from **Diagnosis:**
    retrieved_context: Optional[str] = None  # None when DB is empty
    recommendations: List[str] = []          # empty list, never None
    manual_reference: Optional[str] = None   # parsed from **Manual reference:**
    raw_response: Optional[str] = None       # full LLM output for debugging
    error: Optional[str] = None              # set when status == "error"
 
    @field_validator("vision_analysis", "retrieved_context", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        """Treat empty strings the same as None so the frontend can use 'or' checks."""
        if isinstance(v, str) and not v.strip():
            return None
        return v
 
    @field_validator("recommendations", mode="before")
    @classmethod
    def ensure_list(cls, v):
        """Never let recommendations be None — always return a list."""
        if v is None:
            return []
        return v
 