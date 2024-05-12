## OnboardBot
Demo: [Onboard.bot](https://onboard.bot)

OnboardBot allows you to direct Chatbot conversations towards collecting data defined by flexible YAML files.

For example, the following YAML will direct the Chatbot to collect Name, email and the user's desired number of bedrooms / bathrooms:

```
models:
  - name: Buyer
    class_type: Question
    fields:
      - name: name
      - name: email_address

  - name: DesiredProperty
    class_type: Question
    fields:
      - name: number_of_bedrooms
        type: int
      - name: number_of_bathrooms
        type: float
  
```


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
# Optional
DB_ENGINE_URL="postgresql://postgres:{password}@{host}:5432/postgres"
```

### Data collection
`DB_ENGINE_URL` is optional, but without it the data retrieved from the chats will not be readily available to you.
Its also trivial to send the data to a Slack channel, for example. Built-in support for this is coming soon. Here is an example of an output:

```
buyer:
  email_address: kriggen@gmail.com
  name: Kevin
desiredproperty:
  number_of_bathrooms: 2.5
  number_of_bedrooms: 3
multifamilydetails:
  business headquarters: false
  grandparents quarters: true
  off-grid compound: false
  vacation rental: false
musthave:
  must_haves: green gardens , good aesthetics
propertystyle:
  condo: false
  land: false
  multi_family: true
  other: false
  single_family: false
  townhouse: false

```



### Config.yml
1. you can modify `config.yml` to point to a new model definition to fit your use case
2. for now, it will be best to copy `bots/realty.yml` , and experiment with modifications
3. there are three model types:
   1. `Question` : an open-ended question . The user's text answer is saved to the model instance value.
   2. `Choice` : a single choice . The user's choice is saved to the model instance value.
   3. `MultiChoice` : coming soon. its working in my fork of chainlit , and the PR should be merged soon . See https://github.com/Chainlit/chainlit/pull/965
4. there is `conditions` logic. See `MultiFamilyDetails` in `bots/realty.yml`. `for_choice` is a pointer to another model. A model with this config will show only if that model has a value matched in the `for_value` key of the config. So, You can show / hide questions based on the values of previous questions.


### Server

The OnboardBot server is a simple, opinionated and flexible [Chainlit](https://github.com/Chainlit/chainlit) project.
So you run it like `chainlit run app.py` from `OnboardBot/src/server`.
This will open a browser tab running the chatbot interface.


OnboardBot (via `prompts.py`) will use the data model given in `config.yml` to collect data from the user in a conversational, helpful manner.

Notice that conditional logic, in the case of `notification_preference_sms_email_whatsapp_or_combination`, is handled in the field name itself. The LLMs (including 
`Mixtral-8x7B-Instruct` which is 100x cheaper than gpt-4) handle this exactly how we'd wish. The aim is to push the simplicity as far as possible before implementing logic chains in the models.

Single choice, Multiple choice and conditional logic is supported. 

### UI
OnboardBot does not use a custom client. It uses the default `chainlit` UI. 
Everything OnboardBot wishes to achieve is done via chat.


## Support

create an issue or email [kriggen@gmail.com](mailto:kriggen@gmail.com)


### TODO
- Explain and give good examples of Choice , MultiChoice and conditionals
- Support OpenAI (you'll need to modify `llm.py` to do this for now. Just remove the `base_url` property from `llm_chat_client_async` and change the default models to an OpenAI model. 
- Support duplicate key names in data classes (the LLM needs to understand they are unique, even with same key)
- Decide: should `User` and `Goal` may need to be first-class models, and should prompt be different for definitions of data models versus class that inherit from them? there is a tricky truth here that we are defining pydantic models for LLM's understanding, when we are conditioned to write data models to make our code more meaningful. So, we may need utility classes (or first-class classes?) that support enabled_models that are intended for the LLMs understanding.
