


from fastapi import FastAPI

from app.api import chatbot, feedback, user, auth
from app.core.jwt_auth import create_access_token, verify_token

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to CareChat Track2 Backend!"}

app.include_router(chatbot.router)
app.include_router(feedback.router)
app.include_router(user.router)
app.include_router(auth.router)
