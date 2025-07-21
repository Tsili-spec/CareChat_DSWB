# Chat endpoint for LLM response
from fastapi import APIRouter

router = APIRouter()

@router.post('/chat')
def chat():
    return {'response': 'LLM response here'}
