from pydantic import BaseModel
import uuid


class SubjectCreate(BaseModel):
    name: str


class SubjectResponse(BaseModel):
    name: str

    class Config:
        from_attributes = True


class SubjectResponseWithID(SubjectResponse):
    id: uuid.UUID
    name: str

    class Config:
        from_attributes = True
