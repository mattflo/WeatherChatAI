import asyncio
from typing import AsyncGenerator, List

import streamlit as st
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from weather_chat_ai.weather_graph_agent import WeatherGraphAgent


def get_messages() -> List[BaseMessage]:
    messages = []
    for message in st.session_state.messages:
        if message["role"] == "user":
            messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            messages.append(AIMessage(content=message["content"]))
    return messages


async def get_agent_response(agent: WeatherGraphAgent) -> AsyncGenerator[str, None]:
    response = ""
    async for chunk in agent.astream():
        response += chunk
        yield response


async def main():
    st.title("Weather Chat AI")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What's on your mind?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        agent = WeatherGraphAgent(messages=get_messages())

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            async for partial_response in get_agent_response(agent):
                full_response = partial_response
                response_placeholder.markdown(full_response + "▌")

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


if __name__ == "__main__":
    asyncio.run(main())
