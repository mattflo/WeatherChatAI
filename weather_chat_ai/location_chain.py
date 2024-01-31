from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from weather_chat_ai.models import *


class StrOutputStripper(StrOutputParser):
    def parse(self, text: str) -> str:
        """Returns the input text with no changes."""
        return text.strip(" \n*\"'").split("\n")[0].strip(" .")


class LocationChain(LLMChain):
    def __init__(self):
        location_template = """You are responsible for figuring out the city to look up the weather for. The city might be mentioned in the weather request or the chat history. Be sure to check both. If the request is for an attraction, pick the nearest city for which we can get the weather report. If you can't figure out the city, just default to Denver, CO.

chat history:
{history}

weather request: {input}

Only answer with the city and state in the following format: City, ST

Answer:"""

        super().__init__(
            llm=FireworksCompletion(),
            prompt=PromptTemplate.from_template(location_template),
            output_key="location",
            output_parser=StrOutputStripper(),
        )
