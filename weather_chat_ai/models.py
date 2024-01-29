import os

from langchain.chat_models import ChatOpenAI
from langchain_together import Together


class TogetherChat(ChatOpenAI):
    def __init__(self, **kwargs):
        defaults = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "temperature": 0,
            "openai_api_key": os.environ["TOGETHER_API_KEY"],
            "openai_api_base": "https://api.together.xyz",
        }

        kwargs = {**defaults, **kwargs}

        super().__init__(**kwargs)


class TogetherCompletion(Together):
    def __init__(self, **kwargs):
        defaults = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "temperature": 0,
        }

        kwargs = {**defaults, **kwargs}

        super().__init__(**kwargs)
