import asyncio
import json
import os

import chainlit as cl
import openai
from openai import AsyncOpenAI

from logger import log_message_history_and_prompts
from utils import get_llm_response_as_json


default_model = "mistralai/mixtral-8x7b-instruct" # Cheap but will not currently work with OnboardBot. TODO: add prompt logic to fix?

settings = {
    "temperature": 0.5,
    # "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}


llm_chat_client_async = AsyncOpenAI(    
  base_url="https://openrouter.ai/api/v1",
  api_key=os.environ['OPENROUTER_API_KEY']
)


def format_llm_content(content):
    return (
        content.strip().lstrip().replace('\n',' ')
        .replace('\\','')
        .replace('vbnet', '')
        .replace('```sql','')
        .replace('```python','')
        .replace('```','').replace('`','')
        .strip()
        # .split(';')[0]
    ).lower()


async def ask_llm(message_history, stream=False, model=default_model, as_json=False):
    log_message_history_and_prompts(model, message_history)
    chat_completion = await llm_chat_client_async.chat.completions.create(
        messages=message_history,
        model=model,
        stream=stream,
        **settings
    )

    try:
        content = chat_completion.choices[0].message.content
        
        print(f'[ask_llm] response_content={content}')
        if as_json:
            try:
                content = get_llm_response_as_json(content)
                if content:
                    return content
            except Exception as e:
                print(f'[ask_llm] error parsing json, e={e}, content={content}')
        return format_llm_content(content)
    except Exception as e:
        print(f'[ask_llm] error chat_completion={chat_completion}, e={e}, message_history={message_history}')


async def ask_llm_simple_json(query, model=default_model):
    ''' Send a simple user prompt to a model, without history '''
    message_history = [{
        "role": "user",
        "content": query
    }]
    content = await ask_llm(message_history=message_history, model=model, as_json=True)
    return content


async def get_llm_stream_simple(query, model=default_model):
    return await llm_chat_client_async.chat.completions.create(
        messages = [{
            "role": "user",
            "content": query
        }],
        model=model,
        stream = True,
        **settings
    )

async def get_llm_stream(message_history, model=default_model):
    return await llm_chat_client_async.chat.completions.create(
        messages = message_history,
        stream = True,
        model=model,
        **settings
    )
    
async def simulate_stream(text, chunk_size=10):
    """Asynchronous generator that yields parts of the given text."""
    for i in range(0, len(text), chunk_size):
        yield text[i:i+chunk_size]
        await asyncio.sleep(0.1)  # simulate delay
