import os
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict

import pytest
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferWindowMemory, PostgresChatMessageHistory
from langchain.memory.chat_memory import BaseChatMemory
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.schema.runnable.base import RunnableSequence

from weather_chat_ai.location_chain import LocationChain
from weather_chat_ai.nws_chain import NWSChain
from weather_chat_ai.reply_chain import ReplyChain
from weather_chat_ai.weather_chat_chain import WeatherChatChain


def dated_tag():
    current_date = datetime.now().strftime("%Y%m%d")
    epoch_timestamp = str(time.time())[-4:]
    return f"{current_date}-{epoch_timestamp}"


# @pytest.mark.focus
@pytest.mark.asyncio
async def test_async_chain():
    chain = WeatherChatChain(tags=[dated_tag()])
    result = await chain.acall("What is the weather today in Denver, CO?")

    assert "in Denver" in result["text"]


# @pytest.mark.focus
def test_sync_chain():
    chain = WeatherChatChain(tags=[dated_tag()])
    result = chain("What is the weather today in Denver, CO?")

    assert "in Denver" in result["text"]


class PrintablePassthrough(RunnablePassthrough):
    """Useful as a debugger for a RunnableSequence.

    Probably need to instantiate a new instance for each chain invocation.

    Maybe there is a way to get the name of the previous runnable in the chain and print that too.
    """

    print_num: int = 0

    def __init__(self):
        super().__init__(self.print_passthrough)

    def print_passthrough(self, input: Any) -> Dict[str, Any]:
        name = self.__class__.__name__
        self.print_num += 1
        print(f"{name} {self.print_num}: {type(input)}")
        if isinstance(input, dict):
            print(f"{name} {self.print_num}: {input.keys()}")
        else:
            print(f"{name} {self.print_num}: {input}")
        return input


class Collector:
    """An instance class to collect inputs from chain invocation and propagate them down the chain.

    Inheriting from RunnablePassthrough is not desirable here. We want a new RunnableLambda each time we call collect. But we want one instance of CollectInputs to be passed around to collect a single dictionary.

    Really need to instantiate a new instance for each chain invocation."""

    inputs: Dict[str, Any] = {}

    def __call__(
        self,
        *,
        key: str = None,
        value: Any = None,
    ) -> RunnableLambda:
        """Return a RunnableLambda that will collect new dict entries and return all that have been previously collected."""
        return RunnableLambda(self.collect_callable(key, value))

    def collect_callable(
        self,
        key: str = None,
        build_time_value: Any = None,
    ) -> Callable[[Any], Dict[str, Any]]:
        def collect(run_time_value: Any) -> Dict[str, Any]:
            if isinstance(build_time_value, dict):
                # TODO: maybe we should capture the current passed in dict here and also merge it
                # TODO: or maybe this branch for dict makes no sense
                self.inputs.update(build_time_value)
            elif callable(build_time_value):
                result = build_time_value(self.inputs)
                # TODO: do we need to throw if an unexpected type arrives from the callable?
                isinstance(result, dict) and self.inputs.update(result)
                isinstance(result, str) and key is not None and self.inputs.update(
                    {key: result}
                )
            elif key is not None:
                self.inputs.update({key: run_time_value})
            return self.inputs

        return collect


async def run_async_chain_with_memory(
    chain: RunnableSequence,
    memory: BaseChatMemory,
    input: str,
):
    answer = ""

    async for chunk in chain.astream(input):
        answer += chunk.content

    memory.save_context({"input": input}, {"text": answer})
    return answer


@pytest.mark.focus
@pytest.mark.asyncio
async def test_lcel():
    session_id = str(uuid.uuid4())
    history = PostgresChatMessageHistory(
        connection_string=os.getenv("DATABASE_URL"),
        session_id=session_id,
    )

    memory = ConversationBufferWindowMemory(
        chat_memory=history,
        input_key="input",
    )
    memory.save_context
    location_chain = LocationChain(memory)

    reply_chain = ReplyChain(memory)
    reply_prompt = reply_chain.prompt
    reply_llm = ChatOpenAI(temperature=0)

    collect = Collector()
    debugger = PrintablePassthrough()

    chain = (
        # debugger
        # |
        collect(key="input")
        # | debugger
        | collect(key="history", value=memory.load_memory_variables)
        # | debugger
        | location_chain.prompt
        # | debugger
        | OpenAI()
        # | debugger
        | collect(key="location")
        # | debugger
        # something in the pipe operator puts the string back in a dictionary before NWSChain is called
        | NWSChain()
        # | debugger
        | reply_prompt
        # | debugger
        | reply_llm
        # | debugger
    )

    assert chain is not None, "chain should have been created"

    answer = await run_async_chain_with_memory(
        chain,
        memory,
        "What is the weather today in Breckenridge?",
    )

    print(answer)

    assert isinstance(answer, str), "answer should be a string"
    assert len(answer) > 0, "answer should not be empty"
    assert "breckenridge" in answer.lower(), "answer should mention location"

    answer2 = await run_async_chain_with_memory(
        chain,
        memory,
        "what about tomorrow?",
    )

    print(answer2)
    assert "breckenridge" in answer2.lower(), "answer2 should have remembered location"
