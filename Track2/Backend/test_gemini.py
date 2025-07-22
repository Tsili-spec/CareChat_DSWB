#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the Backend directory to Python path
sys.path.insert(0, '/home/asongna/Desktop/Carechat/Track2/Backend')

from app.services.llm_service import gemini_service

async def test_gemini():
    try:
        print("Testing Gemini service...")
        print("Health status:", gemini_service.get_health_status())
        
        # Test with timeout
        response = await asyncio.wait_for(
            gemini_service.generate_response("Explain how AI works in a few words"),
            timeout=10.0
        )
        print(f"Success! Response: {response}")
    except asyncio.TimeoutError:
        print("Error: Request timed out")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini())
