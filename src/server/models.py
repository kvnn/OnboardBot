from pydantic import BaseModel, Field, validator
from typing import Annotated, List, Optional



class OnboardModel(BaseModel):
    # ALERT!!! field names must be unique across all child models.

    # TODO: fix the above
    # TODO: inject model doctstrings into the prompt loop, for the LLM's context
    pass


class User(OnboardModel):
    '''
    a person using the chat interface
    '''
    user_name: str # the person using the form
    user_age: float


class Favorites(OnboardModel):
    '''
    some of the user's favorite things
    '''
    favorite_musician: str
    favorite_marine_mammal: str


class Preferences(OnboardModel):
    '''
    personal preferences of the user
    '''
    soccer_or_volleyball: str
    dogs_or_kangaroos: str
    coffee_or_tea_or_other: str


# ALERT!!
# This is what dictates what the OnboardBot asks about, and in which order
enabled_models = [
    User,
    Favorites,
    Preferences
]