from pydantic import BaseModel

class ClassCreate(BaseModel):
    standard : int
    section : str
    
class ClassResponse(BaseModel):
    standard : int
    section : str
    
