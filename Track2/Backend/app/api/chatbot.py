"""
Gemini Chat endpoint for CareChat
"""
from fastapi import APIRouter, HTTPException
from app.services.llm_service import gemini_service
import logging

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

@router.post("/")
async def chat(prompt: str):
    """
    Send a message to Gemini AI and get a response.
    
    Uses Google's Gemini 2.0 Flash model for healthcare conversations.
    """
    try:
        logger.info(f"Chat request to Gemini with prompt length: {len(prompt)}")
        
        response_text = await gemini_service.generate_response(prompt)
        
        return {
            "response": response_text,
            "provider": "gemini"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat service error: {str(e)}"
        )
