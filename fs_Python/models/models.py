from typing import Optional
from pydantic import BaseModel


class Occupation(BaseModel):
    name: str
    isSaint: bool

class Customer(BaseModel):
    id: int
    name: str
    age: int
    occupation: Occupation  # Change this to use the Occupation model
    photo_path: Optional[str]  # Make photo_path optional by using Optional[str]

class Config:
    orm_mode = True

class Short_Customer(BaseModel):
     name: str
     occupation: Occupation  # Change this to use the Occupation model
