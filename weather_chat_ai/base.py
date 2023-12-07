from weather_chat_ai.runnables import MergeKeys, WrapWithKey
from weather_chat_ai.location_chain import LocationChain
from weather_chat_ai.nws_chain import NWSChain
from weather_chat_ai.reply_chain import ReplyChain


from langchain.memory import ConversationBufferWindowMemory, PostgresChatMessageHistory
from langchain.schema.runnable.base import RunnableSequence
from langchain_core.runnables.config import RunnableConfig
from langchain_core.runnables.utils import (
    Input,
    Output,
)

import os
import uuid
from typing import Optional


class WeatherChatAIChain(RunnableSequence):
    def __init__(self, session_id: str = None):
        session_id = str(uuid.uuid4())
        history = PostgresChatMessageHistory(
            connection_string=os.getenv("DATABASE_URL"),
            session_id=session_id,
        )

        memory = ConversationBufferWindowMemory(
            chat_memory=history,
            input_key="input",
        )

        reply_chain = ReplyChain(memory)

        runnables = [
            WrapWithKey("input"),
            MergeKeys(memory.load_memory_variables),
            LocationChain().with_retry(),
            NWSChain().with_retry(),
            reply_chain.with_retry(),
        ]

        first = runnables[0]
        middle = runnables[1:-1]
        last = runnables[-1]

        super().__init__(
            first=first,
            middle=middle,
            last=last,
        )

        self.last = reply_chain

    def invoke(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
    ) -> Output:
        result = super().invoke(input, config)
        return result[self.last.output_key]
