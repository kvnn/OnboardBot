## OnboardBot

Forms suck. LLMs are good at conversational-izing data operations. So, we can use LLMs like Mixtral or GPT-4 to get our users (and ourselves, even) into an "onboarded" state.

More interesting, we can use LLMs to provide a continuous interface for managing our relational data. Examples coming soon.


### Install
1. `git clone git@github.com:kvnn/OnboardBot.git`
2. `cd OnboardBoat/src/server`
3. `pip install -r requirements.txt` (TODO: clean this up .. sorry about that ... useful stuff in there tho)
4. Create an `.env` file in the server directory:
```bash
CHAINLIT_AUTH_SECRET="secret"
OPENROUTER_API_KEY="YOUR_OPENROUTER_KEY"
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
```
5. `chainlit run app.py`


### Server

The OnboardBot server is a simple, opinionated and flexible [Chainlit](https://github.com/Chainlit/chainlit) project.
So you run it like `chainlit run app.py` from `OnboardBot/src/server`.
This will open a browser tab running the chatbot interface.

The real meaning of OnboardBot is found in the default `models.py`.
You'll be modifying this file heavily.
Here is an example:

```python
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
        # you will be changing this for the user data YOU want to collect
        favorite_color: str
        favorite_marine_mammal: str

    class Goal(BaseModel):
        '''
        LLM: something that the person wants to accomplish via chat.
        Sometimes we
        '''
        goal_name: str
        goal_description: str
```

OnboardBot (via `prompts.py`) will use the data models above to collect data from the user in a conversational, helpful manner. Note that to enable a Model, it must be imported into `app.py` and added to `datamodels`.


### UI
OnboardBot does not use a custom client. It uses the default `chainlit` UI. 
Everything OnboardBot wishes to achieve is done via chat.


## Support

email aloha@oahu.ai


### TODO

- Support OpenAI (you'll need to modify `llm.py` to do this for now. Just remove the `base_url` property from `llm_chat_client_async` and change the default models to an OpenAI model. 
- Support duplicate key names in data classes (the LLM needs to understand they are unique, even with same key)
- Decide: should `User` and `Goal` may need to be first-class models, and should prompt be different for definitions of data models versus class that inherit from them? there is a tricky truth here that we are defining pydantic models for LLM's understanding, when we are conditioned to write data models to make our code more meaningful. So, we may need utility classes (or first-class classes?) that support DataModels that are intended for the LLMs understanding.
