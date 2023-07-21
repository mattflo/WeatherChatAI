import chainlit as cl
from chainlit.db import db_push
from chainlit import user_session

from weather_chat_ai.chat import WeatherChat


def init_db():
    db_push()


@cl.on_chat_start
async def main():
    cl.user_session.set("chain", WeatherChat.create_chain())


@cl.on_message
async def main(message: str):
    chain = cl.user_session.get("chain")
    whoami = cl.user_session.get("whoami")

    res = await chain.acall({"input": message, "whoami": whoami}, callbacks=[cl.AsyncLangchainCallbackHandler()])

    await cl.Message(content=res["text"]).send()
