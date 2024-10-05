from typing import List

import chainlit as cl
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from weather_chat_ai.weather_graph_agent import WeatherGraphAgent


def update_chat_history(message: BaseMessage) -> List[BaseMessage]:
    chat_history = cl.user_session.get("chat_history")
    if chat_history is None:
        chat_history = []

    chat_history.append(message)
    cl.user_session.set("chat_history", chat_history)
    return chat_history


@cl.on_message
async def main(message: cl.Message):
    chat_history = update_chat_history(HumanMessage(content=message.content))
    session_id = cl.user_session.get("id")

    agent = WeatherGraphAgent(messages=chat_history, session_id=session_id)
    msg = cl.Message(content="")

    full_response = ""
    async for chunk in agent.astream():
        full_response += chunk
        await msg.stream_token(chunk)

    update_chat_history(AIMessage(content=full_response))
