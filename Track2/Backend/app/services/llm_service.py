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
    
    async def generate_response(self, prompt: str, max_words: int = 150, **kwargs) -> str:
        """
        Generate response from Gemini AI with word limit control
        
        Args:
            prompt: Input prompt for the AI
            max_words: Maximum number of words in response (default: 150)
            **kwargs: Additional parameters (temperature, top_p, etc.)
        """
        try:
            # Calculate approximate max tokens (roughly 1.3 tokens per word)
            max_tokens = int(max_words * 1.3)
            kwargs['max_tokens'] = max_tokens
            
            # Add word limit instruction to prompt
            enhanced_prompt = f"{prompt}\n\nIMPORTANT: Keep your response to {max_words} words or fewer."
            
            response = await self._gemini_request(enhanced_prompt, **kwargs)
            
            # Validate word count and truncate if necessary
            response = self._enforce_word_limit(response, max_words)
            
            return response
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail=f"Gemini service error: {str(e)}"
            )
    
    def _enforce_word_limit(self, text: str, max_words: int) -> str:
        """
        Enforce word limit by truncating text if it exceeds the limit
        
        Args:
            text: The response text to check
            max_words: Maximum allowed words
            
        Returns:
            Truncated text if necessary
        """
        words = text.split()
        if len(words) <= max_words:
            return text
        
        # Truncate to max_words and add ellipsis
        truncated = ' '.join(words[:max_words])
        # Try to end at a sentence if possible
        if '.' in truncated:
            sentences = truncated.split('.')
            if len(sentences) > 1:
                # Keep all complete sentences except the last incomplete one
                truncated = '.'.join(sentences[:-1]) + '.'
        
        return truncated
    
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
                # Check if content has parts first, otherwise get text from content directly
                content = data["candidates"][0]["content"]
                if "parts" in content and content["parts"]:
                    return content["parts"][0]["text"]
                elif "text" in content:
                    return content["text"]
                else:
                    # Handle empty response or MAX_TOKENS case
                    if data["candidates"][0].get("finishReason") == "MAX_TOKENS":
                        raise HTTPException(
                            status_code=500,
                            detail="Response was truncated due to max tokens limit. Please try a shorter prompt."
                        )
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail="Empty response from Gemini API"
                        )
            except (KeyError, IndexError) as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Invalid response format from Gemini: {str(e)} - Response: {data}"
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
