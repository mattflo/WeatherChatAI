from langchain import LLMChain, OpenAI, PromptTemplate
from langchain.chains import SequentialChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from weather_chat_ai.nws_chain import NWSChain


class WeatherChat(SequentialChain):
    @classmethod
    def create_chain(cls, whoami=""):
        location_template = """What is the location of the weather request? Answer in the following format: city, state. If no location is present in the weather request, answer Denver, CO.
weather request: {input}"""
        location_chain = LLMChain(
            llm=OpenAI(),
            prompt=PromptTemplate.from_template(location_template),
            output_key="location",
        )

        system_template = """Answer a question about the weather. Below is the forecast you should use to answer the question. It includes the current day and time for reference. You may include the location in your answer, but you should not include the current day or time. If you don't know the answer, don't make anything up. Just say you don't know."""

        human_template = """{forecast}

Never answer with the entire forecast. If the question doesn't contain any specifics, just answer with the current weather for today or tonight. If it's a yes or no question, provide supporting details from the forecast for your answer.

Location: {location}
Question: {input}"""

        reply_chain = LLMChain(
            llm=ChatOpenAI(temperature=0),
            prompt=ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(system_template),
                    HumanMessagePromptTemplate.from_template(human_template),
                ]
            ),
        )

        return cls(
            chains=[location_chain, NWSChain(), reply_chain],
            input_variables=["input"],
            tags=[whoami],
        )
