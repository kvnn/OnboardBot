## OnboardBot

Demo: [Onboard.bot](https://onboard.bot)

Forms suck. LLMs are good at conversational-izing data operations. So, we can use LLMs like Mixtral or GPT-4 to get our users (and ourselves, even) into an "onboarded" state.

More interesting, we can use LLMs to provide a continuous interface for managing our relational data. Examples coming soon.


### Install
1. `git clone git@github.com:kvnn/OnboardBot.git`
2. `cd OnboardBoat/src/server`
3. `pip install -r requirements.txt` (TODO: clean this up .. sorry about that ... useful stuff in there tho)
4. Create an `.env` file in the server directory:
```bash
CHAINLIT_AUTH_SECRET="YOUR SECRET KEY"
OPENAI_API_KEY="YOUR SECRET KEY"
OPENROUTER_API_KEY="YOUR OPENROUTER_API_KEY"
```
5. `chainlit run app.py`

### Optional
1. Postgres database for permanent data storage. Create your database and add this to the .env file: `DATA_DB_CONNECTION="postgresql+asyncpg://{YOUR DB USER}:{YOUR DB PASSWORD}@{YOUR DB URL}:5432/{YOUR DB NAME}}"` .

TODO: If you add this, responses will be saved to the db. The data models in `models.py` will be stored as `jsonb` columns. The database schema can be found in `db_schema.sql` . For now you'll need to create the db schema yourself (copy / paste into something like PGAdmin in your database's public schema) Remember: if you don't have database experience, just ask a good bot for help.


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

OnboardBot (via `prompts.py`) will use the data models above to collect data from the user in a conversational, helpful manner. Note that to enable a Model, it must be imported into `app.py` and added to `enabled_models`.


### UI
OnboardBot does not use a custom client. It uses the default `chainlit` UI. 
Everything OnboardBot wishes to achieve is done via chat.


## Support

create an issue


### TODO

- Support "conditional waterfall" system ?
  - 
- Support OpenAI (you'll need to modify `llm.py` to do this for now. Just remove the `base_url` property from `llm_chat_client_async` and change the default models to an OpenAI model. 
- Support duplicate key names in data classes (the LLM needs to understand they are unique, even with same key)
- Decide: should `User` and `Goal` may need to be first-class models, and should prompt be different for definitions of data models versus class that inherit from them? there is a tricky truth here that we are defining pydantic models for LLM's understanding, when we are conditioned to write data models to make our code more meaningful. So, we may need utility classes (or first-class classes?) that support enabled_models that are intended for the LLMs understanding.
