import os

from langchain.chat_models import ChatOpenAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_community.llms.openai import OpenAI
from langchain_community.llms.fireworks import Fireworks
from langchain_together import Together

defaults = {"temperature": 0}


def to_dict(**kwargs) -> dict:
    return {**kwargs, **defaults}


open_ai_defaults = to_dict(
    max_retries=3,
    request_timeout=20,
)


class OpenAIChat(ChatOpenAI):
    def __init__(self, **kwargs):
        defaults = to_dict(
            model="gpt-3.5-turbo-1106",
            **open_ai_defaults,
        )
        defaults.update(kwargs)
        super().__init__(**defaults)


class OpenAICompletion(OpenAI):
    def __init__(self, **kwargs):
        defaults = to_dict(
            model="gpt-3.5-turbo-instruct",
            **open_ai_defaults,
        )
        defaults.update(kwargs)
        super().__init__(**defaults)


class MistralAIChat(ChatMistralAI):
    def __init__(self, **kwargs):
        defaults = to_dict(
            model="mistral-medium",
            **open_ai_defaults,
        )
        defaults.update(kwargs)
        super().__init__(**defaults)


class FireworksModels:
    mistral_7b = "accounts/fireworks/models/mistral-7b"
    mistral_7b_instruct = "accounts/fireworks/models/mistral-7b-instruct-4k"
    mixtral_8x7b = "accounts/fireworks/models/mixtral-8x7b"
    mixtral_8x7b_instruct = "accounts/fireworks/models/mixtral-8x7b-instruct"


class FireworksChat(ChatOpenAI):
    def __init__(self, **kwargs):
        defaults = to_dict(
            model=FireworksModels.mixtral_8x7b_instruct,
            openai_api_key=os.environ["FIREWORKS_API_KEY"],
            openai_api_base="https://api.fireworks.ai/inference/v1",
            **open_ai_defaults,
        )
        defaults.update(kwargs)
        super().__init__(**defaults)


class FireworksCompletion(Fireworks):
    def __init__(self, **kwargs):
        defaults = to_dict(
            model=FireworksModels.mixtral_8x7b_instruct,
            model_kwargs={"max_tokens": 10},
            **open_ai_defaults,
        )
        defaults.update(kwargs)
        super().__init__(**defaults)


class TogetherChat(ChatOpenAI):
    def __init__(self, **kwargs):
        defaults = to_dict(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            openai_api_key=os.environ["TOGETHER_API_KEY"],
            openai_api_base="https://api.together.xyz",
            **open_ai_defaults,
        )
        defaults.update(kwargs)
        super().__init__(**defaults)


class TogetherCompletion(Together):
    def __init__(self, **kwargs):
        defaults = to_dict(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            max_tokens=10,
        )
        defaults.update(kwargs)
        super().__init__(**defaults)
