# Anonymous session handling (optional)
from fastapi import APIRouter

router = APIRouter()

@router.post('/user')
def create_user():
    return {'status': 'User created'}
