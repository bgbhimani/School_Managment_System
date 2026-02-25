from pydantic import BaseModel
import uuid
from typing import Optional

class NoticeCreate(BaseModel):
    title : str
    description : str
    created_by : uuid.UUID
    class_id : Optional[uuid.UUID]
    standard : Optional[int]
    
class NoticeResponse(BaseModel):
    id : uuid.UUID
    title : str
    description : str
    created_by : uuid.UUID
    class_id : Optional[uuid.UUID]
    standard : Optional[int]

class NoticeResponseWithID(NoticeResponse):
    id: uuid.UUID