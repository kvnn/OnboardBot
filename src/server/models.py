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



class SoccerPlayer(OnboardModel):
    player_email_address: str
    player_name: str


class ContactInfo(OnboardModel):
    '''
    '''
    email_address: str
    mailing_address: str
    sms_phone_number: str


class Measurements(OnboardModel):
    shoe_size: str
    height: str
    weight: str


class CleatSize(ChoiceModel):
    ''' What is your cleat size?'''
    size_6: bool
    size_6_5: bool
    size_7: bool
    size_7_5: bool
    size_8: bool
    size_8_5: bool
    size_9: bool
    size_9_5: bool
    size_10: bool
    size_10_5: bool
    size_11: bool
    size_11_5: bool
    size_12: bool
    size_12_5: bool
    other: bool
    


class FavoriteSoccerPosition(ChoiceModel):
    ''' What is your favorite soccer position?'''
    center_back: bool
    fullback: bool 
    midfielder: bool
    attacking_midfielder: bool
    forward: bool



# ALERT!!
# This is what dictates what the OnboardBot asks about, and in which order
enabled_models = [
    SoccerPlayer,
    ContactInfo,
    Measurements,
    CleatSize,
    FavoriteSoccerPosition
]