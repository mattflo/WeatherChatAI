import chainlit as cl
import structlog
from chainlit import user_session

from weather_chat_ai.weather_chat_chain import WeatherChatChain

logger = structlog.get_logger()


async def run_chain(input: str):
    chain = cl.user_session.get("chain")
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True,
    )
    cb.answer_reached = True

    await chain.acall(
        input,
        callbacks=[cb],
        include_run_info=True,
    )


@cl.action_callback("initial_hints")
async def on_action(action):
    input = action.label

    await cl.Message(
        author="User",
        content=input,
        author_is_user=True,
    ).send()

    await run_chain(input)
    # the action button can be removed, but we don't want to remove these
    # await action.remove()


@cl.on_chat_start
async def main():
    try:
        email_prompt = """## First, please share your contact info.

My human supervisors 👥 would love to know who you are and how to get in touch!

**What's your 📪 Email, 🐦 Twitter, ⛓️ Linked In?**

Enter whatever you're comfortable sharing in the chat box below. Please, and many, many thank yous! 🙏"""

        greeting = """🙏 Awesome, let's get started! Below are some helpful hints.

### Answer vs Search

Don't just get the weather. Ask what you really want to know and let me answer your underlying question.

### ⛔ Limitations

* **Location Unaware** I don't know where you are, so tell me the location you're interested in.
* **No International Support** I'm powered by the [National Weather Service](https://www.weather.gov/), so I can only answer questions about the United States.
* **7 Day Forecast** I can only answer questions about the next 7 days.

📝 Here are some examples to get you started, or enter whatever you like!
"""

        res = await cl.AskUserMessage(content=email_prompt, timeout=60).send()
        if res:
            session_id = cl.user_session.get("id")
            user_session.set(
                "chain", WeatherChatChain(whoami=res["content"], session_id=session_id)
            )
            initial_choices = {
                "denver": "Should I wear a jacket tonight in Denver?",
                "seattle": "I'm traveling to Seattle on Monday. Should I bring an umbrella?",
                "leadville": "Which day is better for a hike this weekend in Leadville?",
            }
            actions = [
                cl.Action(
                    name="initial_hints", value=choice, label=initial_choices[choice]
                )
                for choice in initial_choices
            ]
            await cl.Message(content=greeting, actions=actions).send()
    except Exception as e:
        logger.exception("Failed to start chat.")


@cl.on_message
async def main(message: cl.Message):
    try:
        await run_chain(message.content)

    except Exception as e:
        logger.exception("Failed to process message.")
