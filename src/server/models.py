from datetime import datetime
import json
import os
from typing import Optional
import yaml

from pydantic import create_model
from sqlmodel import Field, SQLModel, create_engine, Session


db_engine_url = os.environ.get('DB_ENGINE_URL', 'sqlite:///OnboardBot.db')


class Onboarding(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    data: str
    created: str | None = Field(default=datetime.now().isoformat())
    updated: str | None = Field(default=None)


class Question(SQLModel):
    ''' You can use this to create a model for the user to fill out.'''

    # TODO: fix the above
    # TODO: inject model doctstrings into the prompt loop, for the LLM's context
    pass


class Choice(SQLModel):
    ''' You can use this to create a list of choices for the user to select from.
    Simply subclass this model, add the message to send to the user as its docstring and add the choices as fields.
    '''
    pass

class MultiChoice(SQLModel):
    # ALERT: In Progress
    ''' You can use this to create a checkbox group of choices for the user to select from.
    '''
    pass


def hyrdate_db():
    engine = create_engine(db_engine_url)
    SQLModel.metadata.create_all(engine)


def save_db_session(onboard_session: Onboarding = None, finished_models: dict = {}):
    engine = create_engine(db_engine_url)
    onboard_session.updated = datetime.now().isoformat()
    onboard_session.data = json.dumps(finished_models)
    session = Session(engine)
    session.add(onboard_session)
    session.commit()
    return onboard_session

def load_models_from_yaml(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, filename)
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    welcome_message = data.get('welcome_message', 'Welcome to the onboarding bot! Let\'s get started!')
    models = {}
    for model_data in data['models']:
        model_name = model_data['name']
        model_fields = {}
        for field in model_data['fields']:
            field_name = field['name']
            if model_data['class_type'] in ['Choice', 'MultiChoice']:
                model_fields[field_name] = (bool, Field(default=False))
            else:
                field_type = eval(field.get('type', 'str'))
                model_fields[field_name] = (field_type, ...)

        class_type = model_data['class_type']
        base_class = eval(class_type)

        description = model_data.get('description', '')
        if description:
            model_cls = create_model(model_name, __base__=base_class, __doc__=description, **model_fields)
        else:
            model_cls = create_model(model_name, __base__=base_class, **model_fields)

        model_cls.conditions = model_data.get('conditions', [])

        models[model_name] = model_cls

    enabled_models = [models[model_name] for model_name in data['enabled_models']]

    return welcome_message, enabled_models


