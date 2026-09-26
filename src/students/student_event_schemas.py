from pydantic import BaseModel
from uuid import UUID


class StudentEvent(BaseModel):
    event: str
    event_id: UUID
    student_id: UUID
    name: str