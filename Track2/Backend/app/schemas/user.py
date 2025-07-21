# Pydantic: user-related I/O
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    phone_number: str
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    phone_number: str
