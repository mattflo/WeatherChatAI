import chainlit as cl
import structlog
from chainlit import user_session

from weather_chat_ai.weather_chat_chain import WeatherChatChain

logger = structlog.get_logger()


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

### 📝 Examples

* `Should I wear a jacket tonight in Denver?`
* `I'm traveling to Seattle on Monday. Should I bring an umbrella?`
* `Which day is better for a hike this weekend in Leadville?`

### ⛔ Limitations

* **Location Unaware** I don't know where you are, so tell me the location you're interested in.
* **No Memory** I don't currently have memory. Please include the location in every message.
* **No International Support** I'm powered by the [National Weather Service](https://www.weather.gov/), so I can only answer questions about the United States.
* **7 Day Forecast** I can only answer questions about the next 7 days."""

        res = await cl.AskUserMessage(content=email_prompt, timeout=60).send()
        if res:
            session_id = cl.user_session.get("id")
            user_session.set(
                "chain", WeatherChatChain(whoami=res["content"], session_id=session_id)
            )
            await cl.Message(content=greeting).send()
    except Exception as e:
        logger.exception("Failed to start chat.")


@cl.on_message
async def main(message: cl.Message):
    try:
        chain = cl.user_session.get("chain")
        cb = cl.AsyncLangchainCallbackHandler(
            stream_final_answer=True,
        )
        cb.answer_reached = True

        res = await chain.acall(
            message.content,
            callbacks=[cb],
            include_run_info=True,
        )
        logger.info(f"Run id: {res['__run'].run_id}")

    except Exception as e:
        logger.exception("Failed to process message.")
