import os
import io
import json
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict, Any
from app.utils.extractor import extract_text_from_file, extract_uuids_from_text, extract_resume_data
from app.core.config import settings
from app.core.minio_client import minio_client, ensure_bucket_exists

router = APIRouter()

@router.post("/upload", response_model=Dict[str, Any])
async def upload_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    temp_file_path = None
    try:
        # Ensure MinIO bucket exists
        ensure_bucket_exists(settings.MINIO_BUCKET_NAME)
        
        # Create a temporary file to run extraction
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            shutil_file = file.file
            shutil_file.seek(0)
            content = shutil_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
            file_size = len(content)
            
        # Extract text, UUIDs, and comprehensive resume data from the temp file
        extracted_text = extract_text_from_file(temp_file_path, file.content_type)
        extracted_uuids = extract_uuids_from_text(extracted_text)
        resume_data_model = extract_resume_data(extracted_text)
        resume_data_dict = resume_data_model.model_dump()
        
        # Upload the original file to MinIO
        with open(temp_file_path, "rb") as file_data:
            minio_client.put_object(
                settings.MINIO_BUCKET_NAME,
                file.filename,
                file_data,
                file_size,
                content_type=file.content_type
            )
            
        generated_files = []
        
        # Upload the parsed structured JSON to MinIO
        base_name = os.path.splitext(file.filename)[0]
        json_filename = f"{base_name}_resume_data.json"
        json_bytes = json.dumps(resume_data_dict, indent=2).encode("utf-8")
        minio_client.put_object(
            settings.MINIO_BUCKET_NAME,
            json_filename,
            io.BytesIO(json_bytes),
            len(json_bytes),
            content_type="application/json"
        )
        generated_files.append(json_filename)

        # Generate & upload <uuid>.md files to MinIO if any UUIDs found
        for uuid in extracted_uuids:
            md_filename = f"{uuid}.md"
            md_content = (
                f"# Extract Metadata\n\n"
                f"- **Unique ID (UUID)**: {uuid}\n"
                f"- **Source File**: {file.filename}\n"
                f"- **Candidate**: {resume_data_model.personal_info.full_name or 'N/A'}\n"
                f"- **Email**: {resume_data_model.personal_info.email or 'N/A'}\n"
                f"- **Content Type**: {file.content_type}\n"
                f"- **File Size**: {file_size} bytes\n"
            )
            md_bytes = md_content.encode("utf-8")
            minio_client.put_object(
                settings.MINIO_BUCKET_NAME,
                md_filename,
                io.BytesIO(md_bytes),
                len(md_bytes),
                content_type="text/markdown"
            )
            generated_files.append(md_filename)
            
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file_size,
            "status": "success",
            "message": f"File '{file.filename}' parsed and stored successfully.",
            "extracted_uuids": extracted_uuids,
            "generated_files": generated_files,
            "resume_data": resume_data_dict
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process and upload file to MinIO: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass
