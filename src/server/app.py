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
from models import enabled_models

from llm import (
    ask_llm_simple_json,
)

# open_router_model_name = 'gpt-3.5-turbo'    # not good for OnboardBot
# open_router_model_name = 'mistralai/mistral-medium' # not good for Onboardbot?

# very good for OnboardBot. strictest conformity to implicit field requirements.
# for example, will make the user correct "octopus" if the field name is "favorite_marine_mammal", b/c octopus is not a mammal.
open_router_model_name = 'gpt-4'

# good for Onboardbot! great for playing with it. good for production IF strict imlplicit field adherance
# is not required. For example, if "octopus" is a good enough answer for "favorite_marine_mammal".
open_router_model_name = 'anthropic/claude-3-haiku'

@app.get("/health-check", status_code=200)
def health_check():
    return {'status':'ok'}


# ALERT: this is just allowing the websocket to connect.
# For production, you're on your own for now (regarding client security).
@app.get("/custom-auth")
async def custom_auth():
    # Verify the user's identity with custom logic.
    token = create_jwt(cl.User(identifier="Test User"))
    return JSONResponse({"token": token})


@cl.action_callback("edit_models")
async def edit_models(action: cl.Action):
    print('edit_models action_callback')
    content = f'Just kidding! But you will be able to soon.'
    msg = cl.Message(content=content)
    # Optionally remove the action button from the chatbot user interface
    # await action.remove()
    await msg.send()


@cl.on_chat_start
async def start_chat():
    cl.user_session.set(
        "message_history",
        [
         ],
    )

    await cl.Avatar(
        name="OnboardBot",
        url="/public/img/onboardbot-avatar.png",
    ).send()

    actions = []
    
    msg = cl.Message(author="OnboardBot", content=welcome_message, actions=actions)

    await msg.send()
    
    current_model = cl.user_session.get("current_model", enabled_models[0])
    model_meta = current_model.__doc__ if current_model.__doc__ else ""
    current_data = {}
    await onboarding_flow([], current_model, current_data, model_meta)


is_first_user_message = True

async def onboarding_flow(message_history, current_model, current_data, model_meta):
    global is_first_user_message

    current_model_name = current_model.__name__

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

    current_data = content['current_data']
    followup_response = content.get('followup_response', fallback_followup_response)

    print(f'first_user_message={is_first_user_message}')

    if is_first_user_message:
        is_first_user_message = False
        content = "By the way, you can edit the models right here in the chat."
        actions = [
            cl.Action(label="Edit models", name="edit_models", value="edit_models", description="Do it!")
        ]
        msg = cl.Message(author="OnboardBot", content=content, actions=actions)
        await msg.send()

    try:
        finished_data = current_model(**current_data)
        current_data_content = pprint.pformat(current_data)
        current_data_content = f'```{current_model_name}``` = ```{current_data_content}```'
        msg = cl.Message(author="OnboardBot", content=current_data_content)
        await msg.send()

        if enabled_models.index(current_model) < len(enabled_models) - 1:
            current_model = enabled_models[enabled_models.index(current_model) + 1]
            current_data = {}
            cl.user_session.set('current_model', current_model)
            cl.user_session.set('current_data', current_data)
            await onboarding_flow(message_history, current_model, current_data, model_meta)
        else:
            finished_content = ''
            for model in enabled_models:
                finished_content += f'```{model.__name__}``` = ```{pprint.pformat(current_data)}```\n'
            msg = cl.Message(author="OnboardBot", content=finished_content)
            await msg.send()

    except ValidationError as e:
        print(f'current_data ValidationError: {e}')
        print(f'{current_model.__name__} not yet complete from current_data {current_data}')
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

