"""
Multi-LLM Service for CareChat with RAG Integration
Supports both Gemini and Groq LLM providers
"""
import httpx
import json
from typing import Dict, Any, Optional, Literal
from fastapi import HTTPException
from app.core.config import settings
import logging

# Import Groq client
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

logger = logging.getLogger(__name__)

LLMProvider = Literal["gemini", "groq"]

class MultiLLMService:
    def __init__(self):
        self.timeout = 30.0
        self.rag_service = None
        self.groq_client = None
        
        # Initialize Groq client if available and configured
        groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
        if GROQ_AVAILABLE and groq_api_key:
            try:
                self.groq_client = Groq(api_key=groq_api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
                self.groq_client = None
        else:
            logger.warning("Groq not available or API key not configured")
    
    async def initialize(self):
        """Initialize the LLM service"""
        logger.info("LLM service initialization completed")
    
    async def generate_response(
        self, 
        prompt: str, 
        provider: LLMProvider = "groq",
        **kwargs
    ) -> str:
        """
        Generate response from specified LLM provider
        
        Args:
            prompt: Input prompt for the AI (may be RAG-enhanced already)
            provider: LLM provider to use ("gemini" or "groq")
            **kwargs: Additional parameters (temperature, top_p, etc.)
        """
        try:
            # Route to appropriate provider
            if provider == "groq":
                response = await self._groq_request(prompt, **kwargs)
            elif provider == "gemini":
                response = await self._gemini_request(prompt, **kwargs)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported LLM provider: {provider}. Use 'gemini' or 'groq'"
                )
            
            return response
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail=f"{provider.title()} service error: {str(e)}"
            )
    
    def _extract_user_message(self, prompt: str) -> Optional[str]:
        """
        Extract user message from the formatted prompt
        
        Args:
            prompt: Full formatted prompt
            
        Returns:
            Extracted user message or None
        """
        try:
            # Look for "Current message:" in the prompt
            if "Current message:" in prompt:
                parts = prompt.split("Current message:")
                if len(parts) > 1:
                    return parts[-1].strip()
            
            # Fallback: look for "Human:" pattern
            if "Human:" in prompt:
                lines = prompt.split('\n')
                for line in reversed(lines):
                    if line.startswith("Human:"):
                        return line.replace("Human:", "").strip()
            
            return None
        except Exception:
            return None
    
    async def _groq_request(self, prompt: str, **kwargs) -> str:
        """Handle Groq API requests"""
        groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
        if not groq_api_key:
            raise HTTPException(status_code=500, detail="Groq API key not configured")
        
        if not self.groq_client:
            raise HTTPException(status_code=500, detail="Groq client not initialized")
        
        try:
            # Extract parameters with defaults
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 1000)
            top_p = kwargs.get("top_p", 1.0)
            
            # Create chat completion with fixed model
            completion = self.groq_client.chat.completions.create(
                model="gemma2-9b-it", # Use a fixed model for Groq
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_completion_tokens=max_tokens,
                top_p=top_p,
                stream=False,
                stop=None,
            )
            
            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Empty response from Groq API"
                )
                
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"Groq API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Groq API error: {str(e)}"
            )
    
    async def _gemini_request(self, prompt: str, **kwargs) -> str:
        """Handle Gemini API requests using the Google AI Studio format"""
        gemini_api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        # Use the correct Gemini API model and endpoint
        model = kwargs.get("model", "gemini-2.0-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        # Use X-goog-api-key header as per Google AI Studio format
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": gemini_api_key
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
            try:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code != 200:
                    error_detail = f"Gemini API error: {response.status_code} - {response.text}"
                    logger.error(error_detail)
                    raise HTTPException(status_code=response.status_code, detail=error_detail)
                
                data = response.json()
                
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
                logger.error(f"Invalid response format from Gemini: {str(e)} - Response: {data}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Invalid response format from Gemini: {str(e)}"
                )
            except Exception as e:
                logger.error(f"Gemini API request failed: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Gemini API request failed: {str(e)}"
                )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all LLM services"""
        gemini_api_key = getattr(settings, 'GEMINI_API_KEY', None)
        groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
        
        return {
            "status": "healthy",
            "providers": {
                "gemini": {
                    "configured": bool(gemini_api_key),
                    "available": bool(gemini_api_key),
                    "message": "Gemini service is ready" if gemini_api_key else "Gemini API key not configured"
                },
                "groq": {
                    "configured": bool(groq_api_key),
                    "available": bool(self.groq_client),
                    "message": "Groq service is ready" if self.groq_client else "Groq not available or API key not configured"
                }
            },
            "default_provider": "groq"
        }

# Global Multi-LLM service instance
llm_service = MultiLLMService()
