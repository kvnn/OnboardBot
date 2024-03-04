from pydantic import BaseModel, Field, validator
from typing import Annotated, List, Optional

# TODO: Inject these doctstrings into the prompt loop if `LLM:`
# TODO: Implement Goal

class User(BaseModel):
    '''
    LLM: a person (or avatar) using the chat interface
    '''
    user_name: str # the person using the form
    user_age: float

class Favorites(BaseModel):
    '''
    LLM: data about the person using the chat interface
    '''
    favorite_color: str
    favorite_marine_mammal: str

class Preferences(BaseModel):
    '''
    LLM: something that the person wants to accomplish via chat.
    '''
    soccer_or_volleyball: str
    dogs_or_kangaroos: str
    red_or_blue: str

enabled_models = [
    User,
    Favorites,
    Preferences
]