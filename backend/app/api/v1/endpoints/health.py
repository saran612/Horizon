from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/health", response_model=Dict[str, str])
def health_check() -> Dict[str, str]:
    return {"status": "ok", "message": "Horizon API is running smoothly."}
