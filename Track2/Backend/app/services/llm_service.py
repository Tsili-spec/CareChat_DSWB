"""
Gemini LLM Service for CareChat
"""
import httpx
import json
from typing import Dict, Any, Optional
from fastapi import HTTPException
from app.core.config import GEMINI_API_KEY

class GeminiService:
    def __init__(self):
        self.timeout = 30.0
        # Don't raise an error during initialization, check during requests
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from Gemini AI"""
        try:
            return await self._gemini_request(prompt, **kwargs)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail=f"Gemini service error: {str(e)}"
            )
    
    async def _gemini_request(self, prompt: str, **kwargs) -> str:
        """Handle Gemini API requests using the Google AI Studio format"""
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        # Use the correct Gemini API model and endpoint
        model = kwargs.get("model", "gemini-2.0-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        # Use X-goog-api-key header as per Google AI Studio format
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": GEMINI_API_KEY
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        # Add generation config if parameters are provided
        if any(key in kwargs for key in ["temperature", "max_tokens", "top_p", "top_k"]):
            payload["generationConfig"] = {}
            if "temperature" in kwargs:
                payload["generationConfig"]["temperature"] = kwargs["temperature"]
            if "max_tokens" in kwargs:
                payload["generationConfig"]["maxOutputTokens"] = kwargs["max_tokens"]
            if "top_p" in kwargs:
                payload["generationConfig"]["topP"] = kwargs["top_p"]
            if "top_k" in kwargs:
                payload["generationConfig"]["topK"] = kwargs["top_k"]
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                error_detail = f"Gemini API error: {response.status_code} - {response.text}"
                raise HTTPException(status_code=response.status_code, detail=error_detail)
            
            data = response.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Invalid response format from Gemini: {str(e)}"
                )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the Gemini service"""
        return {
            "status": "healthy",
            "provider": "gemini",
            "configured": bool(GEMINI_API_KEY),
            "message": "Gemini service is ready" if GEMINI_API_KEY else "Gemini API key not configured"
        }

# Global Gemini service instance
gemini_service = GeminiService()
