from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID
class UserCreate(BaseModel):
    full_name : str
    email : str
    password : str
    role : str

class UserResponse(BaseModel):
    full_name : str
    email : str
    role : str

    class Config:
        orm_mode = True
    
class UserResponseWithID(BaseModel):
    id: UUID
    full_name : str
    email : str
    role : str

    class Config:
        orm_mode = True
    
class UserLogin(BaseModel):
    email: str
    password: str



class TeacherCreate(UserCreate):
    role: Literal['teacher'] = 'teacher'
    
class StudentCreate(UserCreate):
    role: Literal['student'] = 'student'