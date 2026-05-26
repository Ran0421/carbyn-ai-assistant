import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.services.assistant_service import generate_assistant_response
from backend.utils.file_handler import save_uploaded_file
from backend.models.response_model import AnalysisResponse
 
router = APIRouter()
 
 
@router.get("/")
def home():
    return {"message": "Industrial AI Assistant API running"}
 
 
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_equipment(
    query: str = Form(...),
    image: UploadFile = File(...),
):
    # Validate file type before saving
    if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {image.content_type}")
 
    image_path = None
    try:
        image_path = save_uploaded_file(image)
        result = generate_assistant_response(
            image_path=image_path,
            user_query=query,
        )
        return AnalysisResponse(**result)
 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
    finally:
        # Always clean up the temp image file after the request
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
 