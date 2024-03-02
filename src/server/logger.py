import logging
import json
from logging.handlers import RotatingFileHandler


ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger = logging.getLogger("LLMPromptsLogger")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def log_message_history_and_prompts(model, message_history):
    pretty_message_history = json.dumps(message_history, indent=4, ensure_ascii=False)
    log_message = f"Prompt:\n{model}\nMessage History:\n{pretty_message_history}\n"
    logger.info(log_message)