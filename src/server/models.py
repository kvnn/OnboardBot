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

class UserData(User):
    '''
    LLM: data about the person using the chat interface
    '''
    favorite_color: str
    favorite_marine_mammal: str

class Goal(BaseModel):
    '''
    LLM: something that the person wants to accomplish via chat.
    '''
    goal_name: str
    goal_description: str

enabled_models = [
    UserData,
    Goal
]