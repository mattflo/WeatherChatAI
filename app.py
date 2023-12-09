import chainlit as cl
from langchain_core.runnables.config import RunnableConfig

from weather_chat_ai.base import WeatherChatAI


@cl.on_chat_start
async def main():
    session_id = cl.user_session.get("id")
    chain = WeatherChatAI(session_id=session_id)
    cl.user_session.set("chain", chain)


@cl.on_message
async def main(message: cl.Message):
    chain = cl.user_session.get("chain")

    cb = cl.AsyncLangchainCallbackHandler()

    msg = cl.Message(content="")

    async for chunk in chain.astream(
        {"input": message.content},
        config=RunnableConfig(callbacks=[cb]),
    ):
        await msg.stream_token(chunk.content)
