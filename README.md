## OnboardBot

*** Why OnboardBot
Forms suck. LLMs are good at conversational-izing data operations. So, we can use LLMs like Mixtral or GPT-4 to get our users (and ourselves, even) into an "onboarded" state.

More interesting, we can use LLMs to provide a continuous interface for managing our relational data. Examples coming soon.


### Server

The OnboardBot server is a simple, opinionated and flexible `chainlit run` project.
So you run it like `chainlit run app.py` from `OnboardBot/src/server`.
This will open a browser tab running the chatbot interface.

The real meaning of this project is found in the default `models.py`.
Initially, all of your attention should be on this file.
Here it is:

```python
    from pydantic import BaseModel, Field, validator
    from typing import Annotated, List, Optional

    # TODO: Inject these doctstrings into the prompt loop if `LLM:`

    class User(BaseModel):
        '''
        LLM: a person (or avatar) using the chat interface
        '''
        user_name: str # the person using the form

    class Goal(BaseModel):
        '''
        LLM: something that the person wants to accomplish via chat
        '''
        goal_name: str
        goal_description: str

    class UserData(User):
        # you will be changing this for the user data YOU want to collect
        favorite_color: str
        favorite_marine_mammal: str
```

OnboardBot (via `prompts.py`) will use the data models above to collect data from the user in a conversational, helpful manner. Note that to enable a Model, it must be imported into `app.py` and added to `datamodels`.

### GOALS
- should `User` and `Goal` may need to be first-class models, and should prompt be different for definitions of data models versus class that inherit from them? there is a tricky truth here that we are defining pydantic models for LLM's understanding, when we are conditioned to write data models to make our code more meaningful. So, we may need utility classes (or first-class classes?) that support DataModels that are intended for the LLMs understanding.
- tbd


### Client
OnboardBot does not use a custom client. It uses the default `chainlit` UI. 
Everything OnboardBot wishes to achieve is done via chat.


## Support
email aloha@oahu.ai