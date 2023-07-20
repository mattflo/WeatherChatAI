import chainlit as cl
from chainlit.db import init_local_db, db_push

from weather_chat_ai.chat import WeatherChat


@cl.langchain_factory(use_async=True)
def factory():
    return WeatherChat.create_chain()


def init_db():
    db_push()