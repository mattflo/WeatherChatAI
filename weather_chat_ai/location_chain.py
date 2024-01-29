from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from weather_chat_ai.models import TogetherCompletion


class LocationChain(LLMChain):
    def __init__(self):
        location_template = """What is the location of the weather request? Answer in the following format: city, state. If no location is present in the weather request or chat history, answer Denver, CO.

chat history:
{history}

weather request: {input}

Location in cty, st format:"""

        super().__init__(
            llm=TogetherCompletion(),
            prompt=PromptTemplate.from_template(location_template),
            output_key="location",
        )
