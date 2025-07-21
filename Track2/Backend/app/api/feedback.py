# Submit evaluations from clinicians
from fastapi import APIRouter

router = APIRouter()

@router.post('/feedback')
def submit_feedback():
    return {'status': 'Feedback submitted'}
