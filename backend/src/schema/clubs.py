from pydantic import BaseModel


class City(BaseModel):
    id: int | None
    name: str
