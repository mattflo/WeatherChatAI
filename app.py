import chainlit as cl

from weather_chat_ai.chat import WeatherChat


@cl.langchain_factory(use_async=True)
def factory():
    return WeatherChat.create_chain()
