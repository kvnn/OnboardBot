from pydantic import BaseModel, Field, validator
from typing import Annotated, List, Optional


# class Foo(BaseModel):
#     count: int
#     size: Optional[float] = None

#     @validator('size')
#     def prevent_none(cls, v):
#         assert v is not None, 'size may not be None'
#         return v


class User(BaseModel):
    '''
    '''
    name: str
    age: int
    # Note: gpt-3.5-turbo gets extremely confused with "occupation" here.
    job_title: str

class Company(BaseModel):
    name: str
    timezone: str
    room_count: int

    trip_advisor_id: str
    welcome_message: str
    away_message: str

class CompanyLocation(BaseModel):
    country: str
    city: str
    state: str
    zip_code: str
    address_line: str
    hotel_phone: str