import asyncio
from typing import AsyncGenerator, Generator, List

import streamlit as st
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from weather_chat_ai.weather_graph_agent import WeatherGraphAgent

greeting = """### Answer vs Search

Don't just get the weather. Ask what you really want to know and let me answer your underlying question.

### ⛔ Limitations

* **Location Unaware** I don't know where you are, so tell me the location you're interested in.
* **No International Support** I'm powered by the [National Weather Service](https://www.weather.gov/), so I can only answer questions about the United States.
* **7 Day Forecast** I can only answer questions about the next 7 days.

📝 Here are some examples to get you started, or enter whatever you like!
"""

suggestions = {
    "denver": "Should I wear a jacket tonight in Denver?",
    "seattle": "I'm traveling to Seattle on Monday. Should I bring an umbrella?",
    "leadville": "Which day is better for a hike this weekend in Leadville?",
}


def add_human_message(prompt: str):
    st.session_state.messages.append({"role": "user", "content": prompt})


def start_chat():
    st.title("Weather Chat AI")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": greeting}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    last_message = st.session_state.messages[-1]
    if last_message["role"] == "user":
        run_agent(last_message["content"])

    if "suggestions" not in st.session_state:
        st.session_state.suggestions = st.empty()

    if "show_suggestions" not in st.session_state:
        st.session_state.show_suggestions = False
        container = st.session_state.suggestions.container()
        for choice in suggestions:
            container.button(
                suggestions[choice],
                on_click=add_human_message,
                args=(suggestions[choice],),
            )


def get_messages() -> List[BaseMessage]:
    messages = []
    for message in st.session_state.messages:
        if message["role"] == "user":
            messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            messages.append(AIMessage(content=message["content"]))
    return messages


def get_agent_response(agent: WeatherGraphAgent) -> Generator[str, None, None]:
    async def async_generator() -> AsyncGenerator[str, None]:
        response = ""
        async for chunk in agent.astream():
            response += chunk
            yield response

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        agen = async_generator()
        while True:
            try:
                yield loop.run_until_complete(agen.__anext__())
            except StopAsyncIteration:
                break
    finally:
        loop.close()


def run_agent(prompt: str):
    st.session_state.suggestions.empty()
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    agent = WeatherGraphAgent(messages=get_messages())

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        with response_placeholder.container():
            with st.spinner("Thinking..."):
                response_generator = get_agent_response(agent)
                first_response = next(response_generator, None)

        if first_response is not None:
            full_response = first_response
            response_placeholder.markdown(full_response + "▌")

            for partial_response in response_generator:
                full_response = partial_response
                response_placeholder.markdown(full_response + "▌")

    response_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})


def main():
    start_chat()

    if prompt := st.chat_input("What's your weather related question?"):
        add_human_message(prompt)
        run_agent(prompt)


if __name__ == "__main__":
    main()
