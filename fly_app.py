import chainlit as cl
from chainlit.db import db_push
from chainlit import user_session

from weather_chat_ai.chat import WeatherChat


def init_db():
    db_push()


@cl.on_chat_start
async def main():
    email_prompt = """Before we chat about 🌞 weather 💦, my human supervisors 👥 would love to know who you are and how to get in touch!

What's your 📪 email, 🐦 twitter, ⛓️ linked in? Whatever you're comfortable sharing!

If you've been here before on the same device, but your session has expired and you're seeing this again, thanks to the chainlit team 🔗🔥 you have a convenient way to resend a previous message! 💪

Please, and many, many thank yous! 🙏"""

    email_answer = """# Don't just ask what the weather is. Ask what you really want to know and let me answer your underlying question.

Examples:

* Should I wear a jacket tonight in Denver?
* I'm traveling to Seattle on Monday. Should I bring an umbrella?
* Which day is better for a hike this weekend in Leadville?
"""
    res = await cl.AskUserMessage(content=email_prompt, timeout=60).send()
    if res:
        user_session.set("whoami", res["content"])
        elements = [
            cl.Text(
                name="Tips and Tricks",
                content=email_answer,
                display="inline",
                language="markdown",
            )
        ]

        await cl.Message(content="🙏 Awesome, let's get started!", elements=elements).send()

    cl.user_session.set("chain", WeatherChat.create_chain())


@cl.on_message
async def main(message: str):
    chain = cl.user_session.get("chain")
    whoami = cl.user_session.get("whoami")

    res = await chain.acall({"input": message, "whoami": whoami}, callbacks=[cl.AsyncLangchainCallbackHandler()])

    await cl.Message(content=res["text"]).send()
