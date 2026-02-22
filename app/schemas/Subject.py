from pydantic import BaseModel

class SubjectCreate(BaseModel):
    name: str

class SubjectResponse(BaseModel):
    name: str

