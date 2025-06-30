from pydantic import BaseModel
from uuid import UUID


class TagBase(BaseModel):
    name: str
    color: str


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    pass


class TagOut(TagBase):
    id: UUID

    class Config:
        from_attributes = True
