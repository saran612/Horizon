import os
import shutil
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict, Any

router = APIRouter()

# Define upload directory path relative to backend root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

@router.post("/upload", response_model=Dict[str, Any])
async def upload_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    try:
        # Ensure upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_size = os.path.getsize(file_path)
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file_size,
            "saved_path": file_path,
            "status": "success",
            "message": f"File '{file.filename}' uploaded and saved successfully."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process and save uploaded file: {str(e)}"
        )
