from pydantic import BaseModel
import uuid
class ClassCreate(BaseModel):
    standard : int
    section : str
    
class ClassResponse(BaseModel):
    standard : int
    section : str

    class Config:
        from_attributes = True
    
class ClassResponseWithID(ClassResponse):
    id: uuid.UUID
    standard : int
    section : str

    class Config:
        from_attributes = True