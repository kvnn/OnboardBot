## OnboardBot

Demo: [Onboard.bot](https://onboard.bot)

https://github.com/kvnn/OnboardBot/assets/251807/be165084-9a80-4a00-8855-23690a3d662a

Forms suck. LLMs are good at conversational-izing data operations. So, we can use LLMs like Mixtral or GPT-4 to get our users (and ourselves, even) into an "onboarded" state.

More interesting, we can use LLMs to provide a continuous interface for managing our relational data. Examples coming soon.

For now OnboardBot is a simple starter project for a [Chainlit](https://github.com/Chainlit/chainlit)-based data-collecting Chatbot.


### Import Notes
1. Currently , your models config MUST start with a `Question` model type. Hoping to fix this soon.

### Install
1. `git clone git@github.com:kvnn/OnboardBot.git`
2. `cd OnboardBot/src/server`
3. (optional) `python3 -m venv .venv && source .venv/bin/activate`)
4. `pip install -r requirements.txt`
5. Create an `.env` file in the server directory:
```bash
CHAINLIT_AUTH_SECRET="YOUR SECRET KEY"
OPENROUTER_API_KEY="YOUR OPENROUTER_API_KEY"
```
6. Copy `models.example.yml` to `models.yml` (you can define your own models / flow here)
1. `chainlit run app.py`


### Modifications
1. modify `models.py` for your use-case
2. modify `prompt.py` as you wish
3. add branding assets to the `public` folder as you wish (some of which can be pointed to in the `config.yml`)
4. modify `config.yml` as you wish (this is a Chainlit construct)
5. you may need to `Ctrl+C` the local server and then re-run `chainlit run app.py`


### Server

The OnboardBot server is a simple, opinionated and flexible [Chainlit](https://github.com/Chainlit/chainlit) project.
So you run it like `chainlit run app.py` from `OnboardBot/src/server`.
This will open a browser tab running the chatbot interface.

The real meaning of OnboardBot is found in the default `models.py`.
You'll be modifying this file heavily.

Here is an example for beginning to onboard Landscaping candidates:

```python
Employee:
    - employee_name
    - employee_age
    - phone_number
    - email_address

Preferences:
    - preferred_working_hours
    - notification_preference_sms_email_whatsapp_or_combination

enabled_models = [
    Employee,
    Preferences
]
```

OnboardBot (via `prompts.py`) will use the data models above to collect data from the user in a conversational, helpful manner. Note that to enable a Model, it must be added to the `enabled_models` list in `models.py`.

Notice that conditional logic, in the case of `notification_preference_sms_email_whatsapp_or_combination`, is handled in the field name itself. The LLMs (including 
`Mixtral-8x7B-Instruct` which is 100x cheaper than gpt-4) handle this exactly how we'd wish. The aim is to push the simplicity as far as possible before implementing logic chains in the models.


### UI
OnboardBot does not use a custom client. It uses the default `chainlit` UI. 
Everything OnboardBot wishes to achieve is done via chat.


## Support

create an issue or email [kriggen@gmail.com](mailto:kriggen@gmail.com)


### TODO

- Support "conditional waterfall" system ?
  - 
- Support OpenAI (you'll need to modify `llm.py` to do this for now. Just remove the `base_url` property from `llm_chat_client_async` and change the default models to an OpenAI model. 
- Support duplicate key names in data classes (the LLM needs to understand they are unique, even with same key)
- Decide: should `User` and `Goal` may need to be first-class models, and should prompt be different for definitions of data models versus class that inherit from them? there is a tricky truth here that we are defining pydantic models for LLM's understanding, when we are conditioned to write data models to make our code more meaningful. So, we may need utility classes (or first-class classes?) that support enabled_models that are intended for the LLMs understanding.
