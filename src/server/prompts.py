import json

import sys

from models import enabled_models

with open('prompts.json', "r") as file:
    '''
        Open and decode prompts json file
    '''
    try:
        prompt_data = json.load(file)
    except IOError:
        print("Unable to open file {}", "prompts.json")
        sys.exit(1)
    except:
        print('Internal error')
        sys.exit(1)

def get_welcome_message() -> str:
    return prompt_data['welcome']

def get_finished_message() -> str:
    return prompt_data['finish']

def get_fallback_message() -> str:
    return prompt_data['fallback']


def get_onboarding_prompt(message_history, model_meta, model_schema, current_data) -> str:
    prompt = f"{prompt_data['primary']}\n{prompt_data['mistral']}\n\n"

    prompt += f' Here is the data model: `{model_schema}`'
    prompt += f' Here is the metadata for the data model: `{model_meta}`'
    prompt += f' Here is the message history so far: `{message_history}`'
    
    return prompt