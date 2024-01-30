from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from weather_chat_ai.models import TogetherCompletion


class LocationChain(LLMChain):
    def __init__(self):
        location_template = """You are responsible for figuring out the city to look up the weather for. The city might be mentioned in the weather request or the chat history. Be sure to check both. If the request is for an attraction, pick the nearest city for which we can get the weather report. If you can't figure out the city, just default to Denver, CO.

chat history:
{history}

weather request: {input}

Only answer with the city and state in the following format: City, ST

Answer:"""

        super().__init__(
            llm=TogetherCompletion(),
            prompt=PromptTemplate.from_template(location_template),
            output_key="location",
        )
