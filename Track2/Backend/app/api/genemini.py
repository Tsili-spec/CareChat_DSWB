from fastapi import APIRouter, HTTPException, Body
import httpx

router = APIRouter()

GOOGLE_API_KEY = "AIzaSyCkokXWCOn23c2Upr1LFQVaOvVOE5ZuW-o"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

@router.post("/genemini")
async def genemini_chat(prompt: str = Body(..., embed=True)):
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    params = {"key": GOOGLE_API_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.post(GEMINI_API_URL, headers=headers, params=params, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        data = response.json()
        try:
            answer = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            answer = data
        return {"response": answer}
