import chainlit as cl
from chainlit.db import db_push
from chainlit import user_session

from weather_chat_ai.chat import WeatherChat
from weather_chat_ai.nws_chain import create_logger


logger = create_logger(__name__)


def init_db():
    db_push()


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
            user_session.set("chain", WeatherChat.create_chain(whoami=res["content"]))
            await cl.Message(content=greeting).send()
    except Exception as e:
        logger.exception("Failed to start chat.")


@cl.on_message
async def main(message: str):
    try:
        chain = cl.user_session.get("chain")

        res = await chain.acall(
            {"input": message},
            callbacks=[cl.AsyncLangchainCallbackHandler()],
            include_run_info=True,
        )
        logger.info(f"Run id: {res['__run'].run_id}")

        await cl.Message(content=res["text"]).send()
    except Exception as e:
        logger.exception("Failed to process message.")
