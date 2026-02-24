from pydantic import BaseModel, Field
from typing import Literal, Optional
from uuid import UUID


class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role: str


class UserResponse(BaseModel):
    full_name: str
    email: str
    role: str

    class Config:
        orm_mode = True


class UserResponseWithID(BaseModel):
    id: UUID
    full_name: str
    email: str
    role: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: str
    password: str


class TeacherCreate(UserCreate):
    role: Literal["teacher"] = "teacher"


class StudentCreate(UserCreate):
    role: Literal["student"] = "student"


class TeacherAssignSubject(BaseModel):
    teacher_id: UUID
    subject_id: UUID


class TeacherAssignSubjectResponse(BaseModel):
    id: UUID
    user_id: UUID
    subject_id: UUID

    class Config:
        orm_mode = True

class TeacherAssignClass(BaseModel):
    teacher_id: UUID
    class_id: UUID
    is_class_teacher: Optional[bool] = False 


class TeacherAssignClassResponse(BaseModel):
    id: UUID
    teacher_id: UUID
    class_id: UUID
    is_class_teacher: bool 
    
    class Config:
        orm_mode = True
