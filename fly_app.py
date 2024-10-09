import os
from typing import List

import sentry_sdk

from weather_chat_ai.weather_graph_agent import WeatherGraphAgent

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    # Enable performance monitoring
    enable_tracing=True,
)


import sys

import structlog

if not sys.stderr.isatty():
    structlog.configure(
        [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    )


logger = structlog.get_logger(__name__)


import chainlit as cl
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


def update_chat_history(message: BaseMessage) -> List[BaseMessage]:
    chat_history = cl.user_session.get("chat_history")
    if chat_history is None:
        chat_history = []

    chat_history.append(message)
    cl.user_session.set("chat_history", chat_history)
    return chat_history


async def run_agent(input: str):
    chat_history = update_chat_history(HumanMessage(content=input))
    session_id = cl.user_session.get("id")

    agent = WeatherGraphAgent(messages=chat_history, session_id=session_id)
    msg = cl.Message(content="")

    full_response = ""
    async for chunk in agent.astream():
        full_response += chunk
        await msg.stream_token(chunk)

    update_chat_history(AIMessage(content=full_response))


@cl.action_callback("initial_hints")
async def on_action(action):
    input = action.label

    await cl.Message(
        author="User",
        content=input,
        author_is_user=True,
    ).send()

    await run_agent(input)


async def send_intro(whoami):
    initial_choices = {
        "denver": "Should I wear a jacket tonight in Denver?",
        "seattle": "I'm traveling to Seattle on Monday. Should I bring an umbrella?",
        "leadville": "Which day is better for a hike this weekend in Leadville?",
    }
    actions = [
        cl.Action(name="initial_hints", value=choice, label=initial_choices[choice])
        for choice in initial_choices
    ]
    greeting = """🙏 Awesome, let's get started! Below are some helpful hints.

### Answer vs Search

Don't just get the weather. Ask what you really want to know and let me answer your underlying question.

### ⛔ Limitations

* **Location Unaware** I don't know where you are, so tell me the location you're interested in.
* **No International Support** I'm powered by the [National Weather Service](https://www.weather.gov/), so I can only answer questions about the United States.
* **7 Day Forecast** I can only answer questions about the next 7 days.

📝 Here are some examples to get you started, or enter whatever you like!
"""

    await cl.Message(content=greeting, actions=actions).send()


@cl.on_chat_start
async def main():
    try:
        contact_info_prompt = """## First, please share your contact info.

My human supervisors 👥 would love to know who you are and how to get in touch!

**What's your 📪 Email, 🐦 Twitter, ⛓️ Linked In?**"""

        actions = [
            cl.Action(name="anon", value="sure", label="Sure!"),
            cl.Action(name="anon", value="anon", label="I'd prefer not to say"),
        ]

        answer = await cl.AskActionMessage(
            content=contact_info_prompt, timeout=60, actions=actions
        ).send()

        whoami = {"content": "Anonymous"}

        if answer and "value" in answer and answer["value"] == "sure":
            ask = "\n\nEnter whatever you're comfortable sharing in the chat box below. Please, and many, many thank yous! 🙏"
            whoami = await cl.AskUserMessage(content=ask, timeout=60).send()

        if answer and whoami:
            await send_intro(whoami["content"])
    except Exception as e:
        logger.error("An exception occurred: %s", e, exc_info=True)


@cl.on_message
async def main(message: cl.Message):
    try:
        await run_agent(message.content)

    except Exception as e:
        logger.error("An exception occurred: %s", e, exc_info=True)
