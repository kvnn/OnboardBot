import json
import yaml

import chainlit as cl
from chainlit.auth import create_jwt
from chainlit.server import app
from fastapi import Request
from fastapi.responses import JSONResponse
import pprint
from pydantic import ValidationError


from prompts import (
    get_onboarding_prompt,
    finished_message,
    fallback_followup_response,
    welcome_message
)
from models import load_models_from_yaml, hyrdate_db, save_db_session, Onboarding

from llm import (
    ask_llm_simple_json,
)


models_yaml_filename = 'models.yml'

# open_router_model_name = 'gpt-3.5-turbo'    # not good for OnboardBot
# open_router_model_name = 'mistralai/mistral-medium' # not good for Onboardbot?

# very good for OnboardBot. strictest conformity to implicit field requirements.
# for example, will make the user correct "octopus" if the field name is "favorite_marine_mammal", b/c octopus is not a mammal.

open_router_model_name = 'anthropic/claude-3-opus' # great for OnboardBot. Slower than gpt-4

open_router_model_name = 'anthropic/claude-3-sonnet' # good for OnboarBot. Quick. Not 100% accurate

open_router_model_name = 'gpt-4' # best for OnboardBot.

# good for Onboardbot! great for playing with it. good for production IF strict imlplicit field adherance
# is not required. For example, if "octopus" is a good enough answer for "favorite_marine_mammal".
# open_router_model_name = 'anthropic/claude-3-haiku'

# Load the models from the yaml file
models, enabled_models = load_models_from_yaml(models_yaml_filename)

# Initialize the database
hyrdate_db()


@app.get("/health-check", status_code=200)
def health_check():
    return {'status':'ok'}


@app.get("/custom-auth")
async def custom_auth():
    # Verify the user's identity with custom logic.
    token = create_jwt(cl.User(identifier="Test User"))
    return JSONResponse({"token": token})


@cl.on_chat_start
async def start_chat():
    cl.user_session.set(
        "message_history",
        [
         ],
    )
    await cl.Avatar(
        name="OnboardBot",
        url="/public/favicon.png",
    ).send()
    
    msg = cl.Message(author="OnboardBot", content=welcome_message)

    await msg.send()
    
    current_model = cl.user_session.get("current_model", enabled_models[0])
    model_meta = current_model.__doc__ if current_model.__doc__ else ""
    current_data = {}
    await onboarding_flow([], current_model, current_data, model_meta)

@cl.action_callback("save_models")
async def save_models(action):
    print(f'value={action.value} action={action}')
    msg = cl.Message(author="OnboardBot", content='Coming soon!')
    await msg.send()

async def choice_flow(message_history, current_model, current_data, model_meta):
    actions = []
    message = current_model.__doc__

    for field_name, field_type in current_model.__annotations__.items():
        actions.append(
            cl.Action(
                name=field_name,
                value=field_name,
                label=f"✅ {field_name}",
            )
        )
    print(f'[choice_flow]: choices={current_model.__annotations__}')

    # Note: this will await until the user selects a choice
    res = await cl.AskActionMessage(
        content=message,
        actions=actions
    ).send()

    if res and res.get("value"):
        choice = res.get("value")
        for field_name in current_model.__annotations__.keys():
            current_data[field_name] = False
        current_data[choice] = True

        current_data[res.get("value")] = True
        cl.user_session.set('current_data', current_data)

        await onboarding_flow(message_history, current_model, current_data, model_meta)

async def onboarding_flow(message_history, current_model, current_data, model_meta):
    followup_response = fallback_followup_response
    current_model_name = current_model.__tablename__

    # If current_model is an OnboardModel , we need to ask the LLM to fill it out based on message history
    # If its a ChoiceModel, then the user has already made a choice
    if current_model.__base__.__name__ == 'OnboardModel':
        prompt = get_onboarding_prompt(
            message_history=message_history,
            model_schema=current_model.schema_json(),
            model_meta=model_meta,
            current_data=current_data
        )
        
        content = await ask_llm_simple_json(
            query=prompt,
            model=open_router_model_name
        )

        message_history.append({
            "role": "OnboardBot",
            "content": content
        })

        # TODO: if not content, there is an error we need to communicate / handle

        current_data = content.get('current_data', {})
        followup_response = content.get('followup_response', followup_response)

    try:        
        # If the current model can be created from the current data, then its portion of the onboarding is complete
        finished_model = current_model(**current_data)
        finished_data = cl.user_session.get('finished_data', {})
        finished_data[finished_model.__tablename__] = finished_model.model_dump()
        cl.user_session.set('finished_data', finished_data)
        current_data_content = pprint.pformat(current_data)
        current_data_content = f'```{current_model_name}``` = ```{current_data_content}```'

        try:
            onboard_session = cl.user_session.get('onboard_session', Onboarding(data=finished_data))
            onboard_session = save_db_session(onboard_session, finished_data)
            cl.user_session.set('onboard_session', onboard_session)
            msg_content = content=current_data_content
        except Exception as e:
            msg_content = f'There was an error saving to database, but we will carry on! The error was {e}'
        
        msg = cl.Message(author="OnboardBot", content=msg_content)
        await msg.send()

        # Set up the next model and enter the Onboarding Loop
        if enabled_models.index(current_model) < len(enabled_models) - 1:
            current_model = enabled_models[enabled_models.index(current_model) + 1]
            current_data = {}
            cl.user_session.set('current_model', current_model)
            cl.user_session.set('current_data', current_data)

            if current_model.__base__.__name__ == 'ChoiceModel':
                # if its a ChoiceModel, then we ask the user to make a choice
                await choice_flow(message_history, current_model, current_data, model_meta)
            else:
                # if this is an OnboardModel, then we continue the onboarding loop            
                # Note: this is a recursive call
                await onboarding_flow(message_history, current_model, current_data, model_meta)
        # Finished Onboarding
        else:
            finished_content = 'We are finished! Here is your data:\n\n'
            finished_content += '```yaml\n'
            finished_content += yaml.dump(finished_data, default_flow_style=False)
            finished_content += '```'

            actions = [
                cl.Action(label="Send to team", name="save_models", value=finished_content, description="Do it!")
            ]
            msg = cl.Message(author="OnboardBot", content=finished_content, actions=actions)
            await msg.send()

    except ValidationError as e:
        print(f'current_data ValidationError: {e}')
        print(f'{current_model.__tablename__} not yet complete from current_data {current_data}')
        cl.user_session.set('current_data', current_data)
        msg = cl.Message(author="OnboardBot", content=followup_response)
        await msg.send()


@cl.on_message
async def main(message: cl.Message):
    current_model = cl.user_session.get("current_model", enabled_models[0])
    current_data = cl.user_session.get("current_data", {})
    model_meta = current_model.__doc__ if current_model.__doc__ else ""

    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    
    await onboarding_flow(message_history, current_model, current_data, model_meta)

