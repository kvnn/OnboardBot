from typing import Optional

from sqlmodel import Field, SQLModel


class OnboardModel(SQLModel):
    ''' You can use this to create a model for the user to fill out.'''

    # TODO: fix the above
    # TODO: inject model doctstrings into the prompt loop, for the LLM's context
    pass


class ChoiceModel(SQLModel):
    ''' You can use this to create a list of choices for the user to select from.
    
    Simply subclass this model, add the message to send to the user as its docstring and add the choices as fields.
    
    NOTE: the field types MUST be bools'''
    pass



class Buyer(OnboardModel):
    first_name: str
    last_name: str


class ContactInfo(OnboardModel):
    '''
    '''
    email_address: str
    phone_number: str


class DesiredProperty(OnboardModel):
    number_of_bedrooms: int
    number_of_bathrooms: float


class PropertyStyle(ChoiceModel):
    ''' What is your desire property type?'''
    townhouse: bool
    condo: bool
    single_family: bool
    multi_family: bool
    land: bool
    other: bool
    

class DealBreakers(OnboardModel):
    ''' What are your deal breakers for the property?'''
    what_are_your_must_haves: str
    things_you_dont_want: str



# ALERT!!
# This is what dictates what the OnboardBot asks about, and in which order
enabled_models = [
    Buyer,
    ContactInfo,
    DesiredProperty,
    PropertyStyle,
    DealBreakers
]