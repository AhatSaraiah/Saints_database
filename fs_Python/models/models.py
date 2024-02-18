from pydantic import BaseModel


class Occupation(BaseModel):
    name: str
    isSaint: bool

class Customer(BaseModel):
    id: int
    name: str
    age: int
    occupation: Occupation  # Change this to use the Occupation model

class Config:
    orm_mode = True

class Short_Customer(BaseModel):
     name: str
     occupation: Occupation  # Change this to use the Occupation model
