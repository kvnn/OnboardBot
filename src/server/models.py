from typing import Optional
import yaml

from pydantic import create_model
from sqlmodel import Field, SQLModel


models_yaml_filename = 'models.yml'


class OnboardModel(SQLModel):
    ''' You can use this to create a model for the user to fill out.'''

    # TODO: fix the above
    # TODO: inject model doctstrings into the prompt loop, for the LLM's context
    pass


class ChoiceModel(SQLModel):
    ''' You can use this to create a list of choices for the user to select from.
    
    Simply subclass this model, add the message to send to the user as its docstring and add the choices as fields.
    
    NOTE: the field types MUST be bools'''
    pass


def load_models_from_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    models = {}
    for model_data in data['models']:
        model_name = model_data['name']
        model_fields = {}
        for field in model_data['fields']:
            field_name = field['name']
            if 'type' in field:
                field_type = eval(field['type'])
            else:
                field_type = bool
            model_fields[field_name] = (field_type, ...)

        class_type = model_data['class_type']
        base_class = eval(class_type)

        description = model_data.get('description', '')
        if description:
            model_cls = create_model(model_name, __base__=base_class, __doc__=description, **model_fields)
        else:
            model_cls = create_model(model_name, __base__=base_class, **model_fields)

        models[model_name] = model_cls

    enabled_models = [models[model_name] for model_name in data['enabled_models']]

    return models, enabled_models


# Load the models from the yaml file
models, enabled_models = load_models_from_yaml(models_yaml_filename)

