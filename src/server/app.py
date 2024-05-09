import json
import os
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


current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, 'config.yml')
    
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

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
models_config_path = os.path.join(current_dir, config['models_config_path'])
print(f'models_config_path={models_config_path}')
enabled_models = load_models_from_yaml(models_config_path)

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
    print(f'Chat started')
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

async def multi_choice_flow(message_history, current_model, current_data, model_meta):
    options = []
    message = current_model.__doc__

    for field_name, field_type in current_model.__annotations__.items():
        options.append(cl.CheckboxGroupOption(
            label = field_name,
            name = field_name,
            value = field_name
        ))
    import pdb; pdb.set_trace()
    
    options = [
        CheckboxGroupOption(name='townhouse', value='townhouse', label='townhouse'),
        CheckboxGroupOption(name='condo', value='condo', label='condo'),
        CheckboxGroupOption(name='single_family', value='single_family', label='single_family'),
        CheckboxGroupOption(name='multi_family', value='multi_family', label='multi_family'),
        CheckboxGroupOption(name='land', value='land', label='land'),
        CheckboxGroupOption(name='other', value='other', label='other')
    ]

    checkbox_group = cl.CheckboxGroup(
        name=current_model.__tablename__,
        options=options
    )
    print(f'[multi_choice_flow]: options={options}')

    # Note: this will await until the user selects a choice
    res = await cl.AskCheckboxMessage(
        content=message,
        checkbox_group=checkbox_group
    ).send()

    if res:
        selected_names = [option['name'] for option in res['selected']]
        for field_name in current_model.__annotations__.keys():
            if field_name in selected_names:
                current_data[field_name] = True
            else:
                current_data[field_name] = False
        cl.user_session.set('current_data', current_data)

    await onboarding_flow(message_history, current_model, current_data, model_meta)

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

async def continue_or_end_onboarding_flow(message_history, current_model, current_data, model_meta):
    finished_data = cl.user_session.get('finished_data', {})

    # Set up the next model and enter the Onboarding Loop
    if enabled_models.index(current_model) < len(enabled_models) - 1:
        current_model = enabled_models[enabled_models.index(current_model) + 1]
        current_data = {}
        cl.user_session.set('current_model', current_model)
        cl.user_session.set('current_data', current_data)

        # if its a Choice, then we ask the user to make a choice
        if current_model.__base__.__name__ == 'Choice':
            await choice_flow(message_history, current_model, current_data, model_meta)
        # TODO: Multiple Choice
        elif current_model.__base__.__name__ == 'MultiChoice':
            await multi_choice_flow(message_history, current_model, current_data, model_meta)
        # if this is a Question, then we continue the onboarding loop
        else:
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

async def onboarding_flow(message_history, current_model, current_data, model_meta):
    conditions_exist = len(current_model.conditions)
    conditions_met = False
    followup_response = fallback_followup_response
    current_model_name = current_model.__tablename__
    finished_data = cl.user_session.get('finished_data', {})

    print(f'[onboarding_flow] finished_data={finished_data}')
    # If current_model is conditional, then lets run the condition
    for conditional in current_model.conditions:
        if conditional.get('type') == 'ShowForChoice':
            field_name = conditional.get('for_choice')
            # Ohhhhh this is gross. Refactor holistically to make finished_models / enabled_models more cogent throughout the app lifecycle.
            enabled_models_by_name = {model.__name__: model for model in enabled_models}
            our_finished_data_keyname = enabled_models_by_name[field_name].__tablename__
            print(f'enabled_models_by_name={enabled_models_by_name}')
            print(f'our_finished_data_keyname={our_finished_data_keyname}')
            if field_name in enabled_models_by_name:
                if finished_data[our_finished_data_keyname][conditional.get('for_value')]:
                    conditions_met = True
            else:
                print(f'[onboarding_flow] error: conditional field {field_name} not in curent data')

    # If the conditions for showing this question / model are not met, skip it
    if conditions_exist and not conditions_met:
        return await continue_or_end_onboarding_flow(message_history, current_model, current_data, model_meta)

    # If current_model is a Question , we need to ask the LLM to fill it out based on message history
    # If its a Choice, then the user has already made a choice
    if current_model.__base__.__name__ == 'Question':
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
        finished_data[finished_model.__tablename__] = finished_model.model_dump()
        cl.user_session.set('finished_data', finished_data)
        print(f'finished_data={finished_data}')
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

        await continue_or_end_onboarding_flow(message_history, current_model, current_data, model_meta)

    except ValidationError as e:
        print(f'current_data ValidationError: {e}')
        print(f'{current_model.__tablename__} not yet complete from current_data {current_data}')
        cl.user_session.set('current_data', current_data)
        msg = cl.Message(author="OnboardBot", content=followup_response)
        await msg.send()


@cl.on_message
async def main(message: cl.Message):
    print('message received')
    current_model = cl.user_session.get("current_model", enabled_models[0])
    current_data = cl.user_session.get("current_data", {})
    model_meta = current_model.__doc__ if current_model.__doc__ else ""

    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    
    await onboarding_flow(message_history, current_model, current_data, model_meta)

