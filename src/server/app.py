import chainlit as cl
from chainlit.auth import create_jwt
from chainlit.server import app
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError


from prompts import get_onboarding_prompt, finished_message
from models import enabled_models

from llm import (
    ask_llm_simple_json,
)

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
        url="/public/img/onboardbot-avatar.png",
    ).send()
    
    msg = cl.Message(author="OnboardBot", content="Welcome to OnboardBot")
    await msg.send()


async def onboarding_flow(message_history, current_model, current_data, model_meta):
    prompt = get_onboarding_prompt(
        message_history=message_history,
        model_schema=current_model.schema_json(),
        model_meta=model_meta,
        current_data=current_data
    )
    
    content = await ask_llm_simple_json(
        query=prompt,
        model='gpt-4'
    )

    message_history.append({
        "role": "OnboardBot",
        "content": content
    })

    current_data = content['current_data']
    followup_response = content.get('followup_response', "Oh no! I'm not sure what to ask. Maybe you know what I need?")

    try:
        finished_data = current_model(**current_data)
        print(f'{current_model.__name__} is finished with {finished_data}')
        if enabled_models.index(current_model) < len(enabled_models) - 1:
            current_model = enabled_models[enabled_models.index(current_model) + 1]
            current_data = {}
            cl.user_session.set('current_model', current_model)
            cl.user_session.set('current_data', current_data)
            await onboarding_flow(message_history, current_model, current_data, model_meta)
        else:
            print('WE ARE FINISHED!!!')
            msg = cl.Message(author="OnboardBot", content=finished_message)
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

