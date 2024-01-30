import os

from langchain.chat_models import ChatOpenAI
from langchain_together import Together


def to_dict(**kwargs) -> dict:
    return kwargs


class TogetherChat(ChatOpenAI):
    def __init__(self, **kwargs):
        defaults = to_dict(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            temperature=0,
            max_retries=3,
            request_timeout=15,
            openai_api_key=os.environ["TOGETHER_API_KEY"],
            openai_api_base="https://api.together.xyz",
        )
        defaults.update(kwargs)
        super().__init__(**defaults)


class TogetherCompletion(Together):
    def __init__(self, **kwargs):
        defaults = to_dict(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            temperature=0,
            max_tokens=10,
        )
        defaults.update(kwargs)
        super().__init__(**defaults)
