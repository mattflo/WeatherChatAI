import chainlit as cl

from weather_chat_ai.weather_chat_chain import WeatherChatChain


@cl.on_chat_start
async def main():
    session_id = cl.user_session.get("id")
    chain = WeatherChatChain(tags=["local-chainlit"], session_id=session_id)
    cl.user_session.set("chain", chain)


@cl.on_message
async def main(message: cl.Message):
    chain = cl.user_session.get("chain")
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True,
    )
    cb.answer_reached = True

    await chain.acall(
        message.content,
        callbacks=[cb],
    )
